# Session 10803 report (chain 740, lab-desktop window 3): part D, the page

- **What a reader of the page will see once landed:** `/impact` gains "Datacenter" as a fifth project type; the four plants keep every field and figure. A datacenter's left box: an announced project to pick (the document's own MW, investment and jobs), project, spending, jobs and wages, taxes, present value, every default grey with its source on hover. A and B side by side (a plant beside a datacenter works), the datacenter's own lines (sales tax before, forgone by the exemption, property on the building and on the equipment, electricity) shown only when a scenario is a datacenter; its year chart and table; its taxes in other states; CSV, Python and Stata downloads.
- **Restored:** `site/lib/datacenter.ts` (see session 10802's report); the model now `site/lib/dcimpact.ts`.
- **check-values:** recomputes every `datacenter|` key with `dcRun` from its own read of the parameter files; two addresses added.
- **Tests run:** tsc clean for every file touched (the remaining tsc errors are generated types and built content, present before); 62 node tests; 109 Python tests that touch `/impact` or check-values.
- **Waiting:** the local build (the build lock was held by window B's suite, then window A's gate).
- **Commits (branch):** fields and address; the page; the restore and rename; check-values.
- **Needs the key:** nothing.
- **Decisions made without you:** the datacenter's address names are its own (`dmw`, `invest`, `perm`, ...) so no plant link changes; a move between a plant and a datacenter starts the scenario from its defaults; when a scenario is a datacenter the downloads are the datacenter's files (a plant scenario's rows in the CSV in the plant's columns; its Python and Stata are offered when both scenarios are plants).
- **For Samuel's ruling:** nothing new.
