# Local citation preview fix

Use `../start.ps1` for preview and `../build.ps1` for static HTML (`-SiteOnly` builds article JSON). Both commands prepare and verify the theme before MyST runs. A missing template is downloaded once. A changed or unsupported theme stops the command before it starts a server or builds an export. MyST is pinned to 1.10.1 and this patch supports the stock `@myst-theme/article` 1.3.1 build.

The Windows launcher runs MyST with Bun (including when using `PARETO_MYST_CLI`) and downloads to a relative cache path. The pinned CLI's template globbing fails on absolute Windows paths under Node, even when those files exist. Node is still required for the theme patcher and its tests. Install Node.js, Bun and PowerShell before using the launcher.

The readable implementation is `hover-popover.cjs`. It retains Radix HoverCard's placement, opening delay, Escape/outside-click dismissal and interactive content. Its local 300 ms close timer also closes a card when Radix has retained a stale document-wide selection flag. Entering the card cancels that timer; leaving the card closes it. Focus loads lazy cross-reference content. User selections are neither cleared nor globally modified.

Reference labels in `paper.md` now attach to the entire reference paragraph, rather than just its author/year heading. Preserve that single paragraph when editing the bibliography. The appendix references those targets and has no separate bibliography to merge.

## Why a checked bundle patch

The cached stock theme contains build artifacts, while the separate `myst-theme` checkout includes unrelated Pretext changes. Switching to that checkout would expand the scope. `patch-article-theme.cjs` therefore checks the package identity/version and the exact original browser and SSR functions, then injects the same readable factory into both. It changes no other renderer. Updating the theme requires intentionally updating these checks against its source.

The patcher computes the affected JavaScript dependency graph, gives each affected filename a content-derived patch fingerprint, and updates all module references and the SSR asset manifest. Existing immutable browser caches cannot retain the old citation implementation through the new entry URLs. Other assets keep their original names.

All validation happens before the active template is changed. The complete replacement is prepared in a sibling directory, verified, and swapped into place before MyST starts; a failed swap restores the original. The original template directory is retained at the path printed by the patcher and recorded in `.pareto-hover-patch.json`. Do not run the patcher against a template while its server is running. Subsequent runs verify hashes and make no changes. Do not edit patched cached bundles by hand.

For an upstream theme upgrade, stop the preview and restore/download a clean supported template, update the exact-function profiles if needed, and run the regressions before previewing. Do not suppress the validation failure.

## Regression tests

`node --test theme/tests/hover-popover.test.cjs` uses React, React DOM, Radix HoverCard and jsdom. These developer dependencies are declared in `theme/package.json`; install them there for an independent checkout. An existing development dependency directory may instead be supplied with `PARETO_THEME_NODE_MODULES`. Set `PARETO_STOCK_THEME` to a pristine article-theme 1.3.1 directory to also validate and exercise its actual bundled functions and the patch transaction. The tests make no changes to that directory; patch transaction tests use temporary copies.

Tests cover the stock text-selection regression, the fixed browser/SSR functions, selection preservation, trigger-to-card movement, focus loading, dismissal, quick traversal, timer cleanup, hash consistency, idempotence and rejection of a changed template. Browser verification of the article is still required after deployment.
