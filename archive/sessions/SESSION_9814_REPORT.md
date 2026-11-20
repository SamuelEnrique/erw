# Session 9814: `/privacy` and `/terms` against the code (chain 610, part C)

Energy Research Warehouse (ERW). 20 November 2026, 20:16 to 20:24 UTC. The desktop's third window.

## What was done

- [`docs/reviews/privacy-against-code-2026-11-20.md`](https://github.com/SamuelEnrique/erw/blob/main/docs/reviews/privacy-against-code-2026-11-20.md): seven rows where the pages and the code disagree, and what was read and found as written. Nothing on either page changed (the words are Samuel's).
- The three rows a careful reader would most likely take as a broken promise:
  - an address stays in a server instance's memory for as long as the instance runs, not for the hour of the limit (`/api/ask` keeps a map of its own that never drops an address);
  - the model receives the conversation's earlier turns, and on Ask ERCOT the page and settings the reader came from, not only the question;
  - the address typed into the sign-up form goes to Resend, which neither page names.
- Found as written: the two internal cookies are the only cookies; the battery game's two keys are the only browser storage; no analytics service; the font served by the site; the Ask log line holds no identifier.

## What to review

- [`https://erw-flame.vercel.app/privacy`](https://erw-flame.vercel.app/privacy) and [`https://erw-flame.vercel.app/terms`](https://erw-flame.vercel.app/terms) (in review: open the internal view first) beside the review file: each row names the sentence and the file.

## For Samuel's ruling

- Each of the seven rows: change the sentence, or leave it. Default: left as it is.

## Needs the key

- Nothing.
