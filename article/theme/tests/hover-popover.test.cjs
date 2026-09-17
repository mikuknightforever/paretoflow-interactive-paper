'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { createRequire } = require('node:module');
const { spawnSync } = require('node:child_process');
const patcher = require('../patch-article-theme.cjs');
const createHoverPopover = require('../hover-popover.cjs');

const dependencies = process.env.PARETO_THEME_NODE_MODULES;
const req = dependencies ? createRequire(path.join(path.resolve(dependencies), '..', 'package.json')) : require;
const { JSDOM } = req('jsdom');
const dom = new JSDOM('<html><body></body></html>', { url: 'http://example.test/', pretendToBeVisual: true });
const win = dom.window;
for (const key of ['window', 'document', 'navigator', 'Node', 'Element', 'HTMLElement', 'HTMLInputElement', 'NodeFilter', 'CustomEvent', 'Event', 'MouseEvent', 'getComputedStyle', 'MutationObserver']) {
  Object.defineProperty(global, key, { value: win[key], configurable: true });
}
global.requestAnimationFrame = win.requestAnimationFrame.bind(win);
global.cancelAnimationFrame = win.cancelAnimationFrame.bind(win);
global.ResizeObserver = class { observe() {} unobserve() {} disconnect() {} };
// Radix schedules with window.setTimeout but cancels with global clearTimeout.
// jsdom uses numeric window IDs; Node's clearTimeout alone cannot cancel them.
const nodeClearTimeout = global.clearTimeout;
global.clearTimeout = timer => typeof timer === 'number' ? win.clearTimeout(timer) : nodeClearTimeout(timer);
const React = req('react');
const jsx = req('react/jsx-runtime');
const { createRoot, hydrateRoot } = req('react-dom/client');
const HoverCard = req('@radix-ui/react-hover-card');
const h = React.createElement;
const wait = ms => new Promise(resolve => setTimeout(resolve, ms));
const stockTemplate = process.env.PARETO_STOCK_THEME;
let transactionRoot;
let patchedTemplate;
let marker;

function fixtureCopy(source, destination) {
  fs.mkdirSync(destination, { recursive: true });
  const copy = (relative) => {
    const target = path.join(destination, relative);
    fs.mkdirSync(path.dirname(target), { recursive: true });
    fs.copyFileSync(path.join(source, relative), target);
  };
  copy('package.json');
  copy('build/index.js');
  const walk = relative => {
    for (const entry of fs.readdirSync(path.join(source, relative), { withFileTypes: true })) {
      const file = path.join(relative, entry.name);
      if (entry.isDirectory()) walk(file);
      else if (file.endsWith('.js')) copy(file);
    }
  };
  walk('public/build');
}

if (stockTemplate) {
  transactionRoot = fs.mkdtempSync(path.join(os.tmpdir(), 'pareto-hover-test-'));
  patchedTemplate = path.join(transactionRoot, 'article-theme');
  fixtureCopy(stockTemplate, patchedTemplate);
  marker = patcher.patchTemplate(patchedTemplate);
}

function actualFunction(profile, patched) {
  let source;
  if (stockTemplate) {
    let file = profile.file;
    if (patched) file = marker.renamedAssets.find(asset => asset.from === file)?.to ?? file;
    const bundle = fs.readFileSync(path.join(patched ? patchedTemplate : stockTemplate, file), 'utf8');
    source = patched
      ? bundle.match(/\/\*pareto-hover-v1:begin\*\/([\s\S]*?)\/\*pareto-hover-v1:end\*\//)?.[1]
      : bundle.includes(profile.original) && profile.original;
    assert.ok(source, `Expected ${patched ? 'patched' : 'stock'} function in actual ${file}`);
  } else source = patched ? patcher.replacement(profile) : profile.original;
  const fields = ['Root', 'Trigger', 'Portal', 'Content', 'Arrow'];
  const names = [profile.react, profile.name === 'vi' ? 'Xa' : 'PB', ...profile.radix];
  const values = [React, jsx, ...fields.map(key => HoverCard[key])];
  return new Function(...names, `${source};return ${profile.name};`)(...values);
}

const Stock = actualFunction(patcher.profiles[0], false);
const Fixed = actualFunction(patcher.profiles[0], true);

function fire(target, type, relatedTarget = document.body, extra = {}) {
  const event = type === 'keydown'
    ? new win.KeyboardEvent(type, { bubbles: true, ...extra })
    : new win.MouseEvent(type, { bubbles: true, relatedTarget, ...extra });
  Object.defineProperty(event, 'pointerType', { value: 'mouse' });
  target.dispatchEvent(event);
}

function view(Component, id = 'one') {
  return h(Component, { openDelay: 0, card: () => h('p', { id: `preview-${id}` }, 'Complete reference title and publication details') },
    h('span', { id: `trigger-${id}`, tabIndex: 0 }, 'Author (2024)'),
  );
}

async function mount(component = view(Fixed)) {
  document.body.innerHTML = '<p id="outside">Article text selected outside the citation</p><div id="root"></div>';
  const root = createRoot(document.getElementById('root'));
  root.render(component);
  await wait(30);
  return root;
}

async function enter(id = 'one') {
  const trigger = document.getElementById(`trigger-${id}`);
  fire(trigger, 'pointerover');
  fire(trigger, 'mouseover');
  await wait(60);
  assert.ok(document.getElementById(`preview-${id}`));
  return trigger;
}

async function unmount(root) {
  root.unmount();
  document.getSelection().removeAllRanges();
  await wait(20);
}

test('the actual stock function reproduces the stale outside-selection close bug', async () => {
  const root = await mount(view(Stock));
  try {
    const trigger = await enter();
    const range = document.createRange();
    range.selectNodeContents(document.getElementById('outside'));
    document.getSelection().addRange(range);
    fire(document.body, 'pointerup');
    await wait(30);
    document.getSelection().removeAllRanges();
    fire(trigger, 'pointerout');
    await wait(380);
    assert.ok(document.getElementById('preview-one'), 'stock Radix retains a stale selection flag');
  } finally { await unmount(root); }
});

test('fixed actual bundle closes after outside selection without changing that selection', async () => {
  const root = await mount();
  try {
    const trigger = await enter();
    const range = document.createRange();
    range.selectNodeContents(document.getElementById('outside'));
    document.getSelection().addRange(range);
    const selected = document.getSelection().toString();
    fire(document.body, 'pointerup');
    await wait(30);
    fire(trigger, 'pointerout');
    await wait(380);
    assert.equal(document.getElementById('preview-one'), null);
    assert.equal(document.getSelection().toString(), selected);
  } finally { await unmount(root); }
});

test('trigger-to-card movement retains the card, then leaving content closes it', async () => {
  const root = await mount();
  try {
    const trigger = await enter();
    const card = document.querySelector('.hover-card-content');
    fire(trigger, 'pointerout', card);
    fire(card, 'pointerover', trigger);
    await wait(380);
    assert.ok(document.getElementById('preview-one'));
    fire(card, 'pointerout');
    await wait(380);
    assert.equal(document.getElementById('preview-one'), null);
  } finally { await unmount(root); }
});

test('entering the card across the five-pixel gap cancels the pending close timer', async () => {
  const root = await mount();
  try {
    const trigger = await enter();
    const card = document.querySelector('.hover-card-content');
    fire(trigger, 'pointerout');
    await wait(100);
    fire(card, 'pointerover');
    await wait(380);
    assert.ok(document.getElementById('preview-one'));
  } finally { await unmount(root); }
});

test('keyboard focus loads lazy content, and Escape dismisses it', async () => {
  const root = await mount();
  try {
    document.getElementById('trigger-one').focus();
    await wait(60);
    assert.ok(document.getElementById('preview-one'));
    fire(document, 'keydown', null, { key: 'Escape' });
    await wait(30);
    assert.equal(document.getElementById('preview-one'), null);
  } finally { await unmount(root); }
});

test('quick traversal closes older citations and outside click dismisses the current one', async () => {
  const root = await mount(h('div', null, view(Fixed, 'one'), view(Fixed, 'two'), view(Fixed, 'three')));
  try {
    for (const id of ['one', 'two', 'three']) {
      const trigger = await enter(id);
      if (id !== 'three') fire(trigger, 'pointerout');
    }
    await wait(380);
    assert.equal(document.querySelectorAll('.hover-card-content').length, 1);
    assert.ok(document.getElementById('preview-three'));
    fire(document.getElementById('outside'), 'pointerdown');
    await wait(30);
    assert.equal(document.querySelectorAll('.hover-card-content').length, 0);
  } finally { await unmount(root); }
});

test('unmount cancels pending local close timers', async () => {
  const root = await mount();
  const trigger = await enter();
  fire(trigger, 'pointerout');
  await unmount(root);
  await wait(380);
  assert.equal(document.querySelectorAll('.hover-card-content').length, 0);
});

test('actual browser and server replacements hydrate the same initial markup', async () => {
  const serverProfile = patcher.profiles[1];
  const serverSource = stockTemplate
    ? fs.readFileSync(path.join(patchedTemplate, 'build/index.js'), 'utf8').match(/\/\*pareto-hover-v1:begin\*\/([\s\S]*?)\/\*pareto-hover-v1:end\*\//)[1]
    : patcher.replacement(serverProfile);
  const payload = `
    const {createRequire}=require('node:module');
    const req=createRequire(${JSON.stringify(req.resolve('react'))});
    const React=req('react'),HC=req('@radix-ui/react-hover-card');
    const Component=new Function('uzr','izr','azr','szr','ozr','lzr',${JSON.stringify(serverSource + ';return cx;')})(React,HC.Root,HC.Trigger,HC.Portal,HC.Content,HC.Arrow);
    const h=React.createElement;
    process.stdout.write(req('react-dom/server').renderToString(h(Component,{openDelay:0,card:()=>h('p',{id:'preview-one'},'Complete reference title and publication details')},h('span',{id:'trigger-one',tabIndex:0},'Author (2024)'))));
  `;
  const ssr = spawnSync(process.execPath, ['-e', payload], { encoding: 'utf8' });
  assert.equal(ssr.status, 0, ssr.stderr);
  document.body.innerHTML = `<div id="root">${ssr.stdout}</div>`;
  const errors = [];
  const root = hydrateRoot(document.getElementById('root'), view(Fixed), { onRecoverableError: error => errors.push(error.message) });
  await wait(50);
  try {
    assert.deepEqual(errors, []);
    await enter();
    assert.ok(document.getElementById('preview-one'));
  } finally { await unmount(root); }
});

test('patch transaction fingerprints imports/SSR and is idempotent', { skip: !stockTemplate }, () => {
  assert.equal(marker.changed, true);
  assert.ok(marker.renamedAssets.length >= 2);
  const before = fs.readFileSync(path.join(patchedTemplate, 'build/index.js'));
  const result = patcher.patchTemplate(patchedTemplate);
  assert.equal(result.changed, false);
  assert.deepEqual(fs.readFileSync(path.join(patchedTemplate, 'build/index.js')), before);
  assert.ok(fs.existsSync(marker.backup));
  assert.ok(marker.files.some(file => file.path === 'build/index.js'));
  assert.ok(marker.files.some(file => /manifest-.*pareto-hover/.test(file.path)));
});

test('unexpected template source fails before any template write', { skip: !stockTemplate }, () => {
  const template = path.join(transactionRoot, 'changed-theme');
  fixtureCopy(stockTemplate, template);
  const bundle = path.join(template, patcher.profiles[1].file);
  const before = fs.readFileSync(bundle, 'utf8').replace(patcher.profiles[1].original, '/* different upstream implementation */');
  fs.writeFileSync(bundle, before);
  const siblings = fs.readdirSync(transactionRoot);
  assert.throws(() => patcher.patchTemplate(template), /Expected exactly one stock/);
  assert.equal(fs.readFileSync(bundle, 'utf8'), before);
  assert.deepEqual(fs.readdirSync(transactionRoot), siblings);
  assert.equal(fs.existsSync(path.join(template, '.pareto-hover-patch.json')), false);
});

test('tampering with a patched asset is rejected', { skip: !stockTemplate }, () => {
  const bundle = path.join(patchedTemplate, marker.files[0].path);
  fs.appendFileSync(bundle, '\n// unexpected edit');
  assert.throws(() => patcher.patchTemplate(patchedTemplate), /changed unexpectedly/);
});

test.after(() => {
  dom.window.close();
  global.clearTimeout = nodeClearTimeout;
  if (transactionRoot) {
    const resolved = path.resolve(transactionRoot);
    assert.equal(path.dirname(resolved), path.resolve(os.tmpdir()));
    assert.ok(path.basename(resolved).startsWith('pareto-hover-test-'));
    fs.rmSync(resolved, { recursive: true, force: true });
  }
});
