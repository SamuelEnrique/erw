# Session 1589 report: the Markdown table on /data/licenses: left, with the reason

Energy Research Warehouse (ERW), session 1589, chain 187, samueloldlaptop, 6 November 2026, 15:11 UTC. Model: Claude Opus 5.5 (the file names Fable 5.1). Model spend USD 0. No warehouse data written; nothing sent or posted. On main.

## What it found

- `/data/licenses`'s third table scrolls and cannot be reached by keyboard. The table is drawn by `site/lib/markdown.ts` from `docs/licenses.md`, and the same renderer draws the Digest, the Roundup and every methods page. But `ScrollRegions.tsx` already marks `.prose-erw table` while it scrolls (session 583, which names `/data/licenses`), at run time. So with scripts the table is reachable, and AccessLint's finding is its reading before that pass. A server-side fix would change every Markdown page, the Digest's and the Roundup's included, and is not worth that reach.

## Decisions made without you

- No fix: the run-time marking covers it. The next file names it as read, not open.

## For Samuel's ruling

- None.
