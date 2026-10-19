# DeckyMods development constraints

- Read `docs/LESSONS.md` and `docs/CONTRACT.md` before changing behavior.
- Default verification uses isolated fixtures and GitHub CI. Do not connect to,
  install on, restart, or modify a Steam Deck without a new explicit user request.
- Never publish personal API keys, account files, subscriptions, NXM grants,
  browser cookies, launch options, private backups, device addresses, or MOD files.
- Publish from the sanitized independent repository, not local private history.
- Keep a failing regression for each reproduced bug before fixing it. Use an
  independent code review and the relevant language review before publishing.
- System Python success does not establish Decky frozen-runtime compatibility.
  Keep the missing-stdlib and empty-CA regressions; never disable TLS verification.
- Keep catalog recognition, format support, and actual game validation distinct.
  Never describe synthetic tests as game or hardware validation.
- Preserve existing game identities, MOD layers, backups, manual roots, tasks,
  launch options and receiver preferences across upgrades. Fail closed on conflicts.
- Do not guess a Nexus domain, target path, loader, optional archive variant, or
  launch parameter. Unknown games require the explicit root-install mode.
- API binding, browser login and file-download authorization are separate states.
  Follow the official ordinary-member browser/NXM flow and keep local import usable.
- UI lists stay folded by default, but all validated installed games are visible
  without a franchise filter. Async replies must belong to the current selection.
- Use Decky's existing native update connection and confirmation modal. Do not open
  a second websocket or claim installation is complete from a copied ZIP alone.
- Install update packages only after signed manifest, hash, size, layout and
  permission checks. Keep prereleases out of the normal feed until validated.
- Record each iteration's reproduced trigger, fix, regression, review and checks
  in `docs/ITERATIONS.md`; do not count a version bump alone as an improvement.
