#!/usr/bin/env node
'use strict';

const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const createHoverPopover = require('./hover-popover.cjs');

const PATCH_ID = 'pareto-hover-v1';
const MARKER = '.pareto-hover-patch.json';
const SOURCE = createHoverPopover.toString();
const sha = text => crypto.createHash('sha256').update(text).digest('hex');
const profiles = [
  {
    file: 'public/build/_shared/chunk-TDT2BMLS.js', name: 'vi', react: 'fT',
    radix: ['lT', 'cT', 'dT', 'uT', 'hT'],
    original: 'function vi({children:r,openDelay:e=400,card:t,side:i,arrowClass:n="fill-white"}){let[s,o]=(0,fT.useState)(!1);return(0,Xa.jsxs)(lT,{openDelay:e,children:[(0,Xa.jsx)(cT,{asChild:!0,onMouseEnter:()=>o(!0),children:r}),(0,Xa.jsx)(dT,{children:(0,Xa.jsxs)(uT,{className:"exclude-from-outline hover-card-content",sideOffset:5,side:i,children:[typeof t=="function"?s&&t({load:s}):t,(0,Xa.jsx)(hT,{className:n})]})})]})}',
  },
  {
    file: 'build/index.js', name: 'cx', react: 'uzr',
    radix: ['izr', 'azr', 'szr', 'ozr', 'lzr'],
    original: 'function cx({children:t,openDelay:e=400,card:r,side:n,arrowClass:i="fill-white"}){let[s,a]=(0,uzr.useState)(!1);return(0,PB.jsxs)(izr,{openDelay:e,children:[(0,PB.jsx)(azr,{asChild:!0,onMouseEnter:()=>a(!0),children:t}),(0,PB.jsx)(szr,{children:(0,PB.jsxs)(ozr,{className:"exclude-from-outline hover-card-content",sideOffset:5,side:n,children:[typeof r=="function"?s&&r({load:s}):r,(0,PB.jsx)(lzr,{className:i})]})})]})}',
  },
];

function replacement(profile) {
  const fields = ['Root', 'Trigger', 'Portal', 'Content', 'Arrow'];
  const radix = fields.map((field, i) => `${field}:${profile.radix[i]}`).join(',');
  return `/*${PATCH_ID}:begin*/var ${profile.name}=(${SOURCE})(${profile.react},{${radix}});/*${PATCH_ID}:end*/`;
}

function walk(dir) {
  return fs.readdirSync(dir, { withFileTypes: true }).flatMap(entry => {
    const file = path.join(dir, entry.name);
    return entry.isDirectory() ? walk(file) : [file];
  });
}

function assertPackage(template) {
  const pkg = JSON.parse(fs.readFileSync(path.join(template, 'package.json'), 'utf8'));
  if (pkg.name !== '@myst-theme/article' || pkg.version !== '1.3.1') {
    throw new Error(`Unsupported article theme ${pkg.name}@${pkg.version}; expected @myst-theme/article@1.3.1.`);
  }
}

function checkPatched(template) {
  assertPackage(template);
  const marker = JSON.parse(fs.readFileSync(path.join(template, MARKER), 'utf8'));
  if (marker.patch !== PATCH_ID || marker.sourceHash !== sha(SOURCE)) {
    throw new Error('The cached patch differs from local source; restore a pristine 1.3.1 template before updating it.');
  }
  for (const file of marker.files) {
    const current = fs.readFileSync(path.join(template, file.path));
    if (sha(current) !== file.sha256) throw new Error(`Patched asset changed unexpectedly: ${file.path}`);
  }
  for (const asset of marker.renamedAssets) {
    if (fs.existsSync(path.join(template, asset.from))) throw new Error(`Old asset remains in active template: ${asset.from}`);
  }
  return marker;
}

function planPatch(template) {
  assertPackage(template);
  const jsFiles = walk(path.join(template, 'public', 'build')).filter(file => file.endsWith('.js'));
  const source = new Map(jsFiles.map(file => [path.relative(template, file).replaceAll('\\', '/'), fs.readFileSync(file, 'utf8')]));
  source.set('build/index.js', fs.readFileSync(path.join(template, 'build', 'index.js'), 'utf8'));
  const edited = new Map(source);
  for (const profile of profiles) {
    const text = source.get(profile.file);
    if (!text || text.split(profile.original).length !== 2) {
      throw new Error(`Expected exactly one stock HoverPopover in ${profile.file}; no files were changed.`);
    }
    edited.set(profile.file, text.replace(profile.original, replacement(profile)));
  }

  // Fingerprint the complete changed dependency graph. Changing only a chunk's
  // body would leave the previous code in browsers' immutable asset caches.
  const affected = new Set([profiles[0].file]);
  let previousSize;
  do {
    previousSize = affected.size;
    const names = [...affected].map(file => path.posix.basename(file));
    for (const [file, text] of source) {
      if (file.startsWith('public/build/') && names.some(name => text.includes(name))) affected.add(file);
    }
  } while (affected.size !== previousSize);
  const fingerprint = sha(SOURCE + [...affected].sort().map(file => `\n${file}:${sha(source.get(file))}`).join('')).slice(0, 12);
  const renamedAssets = [...affected].sort().map(from => ({
    from, to: from.replace(/\.js$/, `-pareto-hover-${fingerprint}.js`),
  }));
  const files = [];
  for (const [file, text] of edited) {
    let changed = text;
    for (const asset of renamedAssets) changed = changed.replaceAll(path.posix.basename(asset.from), path.posix.basename(asset.to));
    const destination = renamedAssets.find(asset => asset.from === file)?.to ?? file;
    if (changed !== source.get(file) || destination !== file) files.push({ path: destination, source: file, text: changed, sha256: sha(changed) });
  }
  const resulting = new Map([...source].filter(([file]) => !affected.has(file)));
  for (const file of files) resulting.set(file.path, file.text);
  // Ensure no stale import/manifest entry survives, and every referenced local
  // JavaScript module exists in the same transaction.
  for (const [file, text] of resulting) {
    for (const asset of renamedAssets) {
      if (text.includes(path.posix.basename(asset.from))) throw new Error(`Unrewritten asset reference in ${file}`);
    }
    for (const match of text.matchAll(/\/myst_assets_folder\/([^\s"'`]+\.js)(?=["'`])/g)) {
      if (!resulting.has(`public/build/${match[1]}`)) throw new Error(`Missing local module ${match[1]} referenced by ${file}`);
    }
  }
  return { files, renamedAssets, fingerprint };
}

function checkedSibling(template, prefix) {
  const result = path.resolve(path.dirname(template), `${path.basename(template)}.${prefix}-${crypto.randomUUID()}`);
  if (path.dirname(result) !== path.dirname(template) || result === template) throw new Error('Unsafe transaction path');
  return result;
}

function patchTemplate(templateIn, { check = false } = {}) {
  const template = path.resolve(templateIn);
  if (fs.existsSync(path.join(template, MARKER))) return { changed: false, ...checkPatched(template) };
  if (check) throw new Error('Article theme is not patched. Run theme/patch-article-theme.cjs before preview/build.');
  const plan = planPatch(template); // All original-code and dependency checks precede writes.
  const staging = checkedSibling(template, 'pareto-hover-staging');
  const backup = checkedSibling(template, 'pareto-hover-original');
  const marker = {
    patch: PATCH_ID, sourceHash: sha(SOURCE), fingerprint: plan.fingerprint,
    files: plan.files.map(({ path: file, sha256 }) => ({ path: file, sha256 })),
    renamedAssets: plan.renamedAssets, backup,
  };
  try {
    fs.cpSync(template, staging, { recursive: true });
    for (const file of plan.files) fs.writeFileSync(path.join(staging, file.path), file.text);
    for (const asset of plan.renamedAssets) fs.unlinkSync(path.join(staging, asset.from));
    fs.writeFileSync(path.join(staging, MARKER), JSON.stringify(marker, null, 2) + '\n');
    checkPatched(staging);
    fs.renameSync(template, backup);
    try { fs.renameSync(staging, template); }
    catch (error) { fs.renameSync(backup, template); throw error; }
  } catch (error) {
    // This directory was resolved and confined to template's parent above.
    if (fs.existsSync(staging)) fs.rmSync(staging, { recursive: true, force: true });
    throw error;
  }
  return { changed: true, ...marker };
}

if (require.main === module) {
  try {
    const args = process.argv.slice(2);
    const templateArg = args.find(arg => !arg.startsWith('--'));
    const template = templateArg || path.resolve(__dirname, '../_build/templates/site/myst/article-theme');
    const result = patchTemplate(template, { check: args.includes('--check') });
    console.log(`${PATCH_ID}: ${result.changed ? 'applied' : 'verified'} (${result.fingerprint}, ${result.renamedAssets.length} fingerprinted assets).`);
    if (result.changed) console.log(`Original template retained at ${result.backup}`);
  } catch (error) { console.error(error.message); process.exitCode = 1; }
}

module.exports = { patchTemplate, planPatch, checkPatched, replacement, profiles, PATCH_ID };
