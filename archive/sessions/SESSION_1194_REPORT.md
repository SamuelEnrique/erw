# Session 1194 report: the answer's sources, in the brand's form

23 October 2026, 23:30 to 23:40 UTC, on samueloldlaptop, unattended. Chain `queue/done/089-day-26-october-code-ask-board-4.md`. Model spend USD 0.

- **Done**: `site/components/ask/AnswerSources.tsx`, an answer's source lines and read lines in the brand's source line (`components/tool/ToolPage.tsx` `SourceLine`: 12 px, grey, a rule above, "Source: ERW table ..."), drawn the same under every chat's answer. Until now Ask ERCOT's and the grids' panel (`components/ask/AskPanel.tsx`) drew a grey list and the general chat's form (`app/ask/AskForm.tsx`) a "Sources" heading in 18 px with its own list; both now draw the one component. Each source names its table with a link (`sourceHref`, moved into the component and exported from the panel as before: a grid's written page, a page's own file, or the catalogue's row), its tier (the model-extracted label with its title), its source report and, on hover, the data's version; each read as sessions 1115 and 1132 wrote it (`readWords`). The marks the browser checks count (`data-sources` with one `li` a source, `data-reads`) are kept.
- **Links**: every link the component draws goes through `SiteLink` (`gate="plain"`) to `/data#<table>`, `/grid?grid=<slug>` or a page's own address, as before; `check-links.mjs` on the chain's build reads them.
- **AccessLint**, on the component rendered with a stored answer and no model call: session 1149's t06 (`warehouse/chat/eval/eval_s1133_s1114_run.json`, its citation and the four reads of its recorded queries), compiled from the component's own source with TypeScript and rendered by React's server renderer, `SiteLink` stood in by a plain anchor (the script stays in the session's scratchpad, not the repository): no violations. Without the site's stylesheet, so contrast is not judged there: the chain's build checks it on the page.
- **Tests**: `site/scripts/test-ask-1115.mjs` and `tests/test_session1145.py` read the reads' mark in the component and its use in the panel and the form (their old literals moved); the Ask tests of sessions 92, 168, 241b, 299, 315, 351, 1115 and 1145: 71 passed, 15 skipped. Type check clean but for the build's generated files; ESLint finds two errors in `BoardView.tsx`'s older effects (lines 395 and 426, `set-state-in-effect`), there before this chain.
- **Not yet**: the screenshots of an answer: they need an answer on a served build; with no model call in this chain, of the board's Ask section with a stored answer's sources is not possible either (the form draws only what the route returns). Under "To finish".
- On `wip/1190-ask`.

## Decisions made without you

1. One component for both chats, the general form's "Sources" heading dropped for the brand's source line. Reversible.

## For Samuel's ruling

None.

## To finish

1. Screenshots of an answer with its sources at 390 and 1280, on a build with one question asked (093's session 1302 has the cap).
