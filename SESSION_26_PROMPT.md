Session 26 of the Energy Research Warehouse (ERW). Read CLAUDE.md, warehouse/thesis/build.py, warehouse/policy/reads.py, site/lib/pages.ts, SESSION_24_REPORT.md and SESSION_25_REPORT.md first. Same non-negotiables; commit after each task; may push after merging origin/main; API spend stop USD 3. Reading warehouse/news/score.py is allowed.

Human rulings: in Thesis Builder, public companies stay on Incumbents and off Landscape, and if one appears on Landscape its Raised cell is blank with the note "public company"; investor names and dates in Capital rows need a quoted span from a source, like the policy reads, else the field is blank; in policy reads, a date restated in a different format is accepted when the date appears in the source text; FERC stays via the Federal Register; other state PUCs are deferred.

TASK 1. Apply the Thesis Builder rulings, then rebuild both existing workbooks from their saved states with --resume (no new research calls) and report what changed in the ten spot-checked rows. Commit.

TASK 2. Apply the policy date ruling and re-run only the reads whose fields were dropped for a date restatement (from the run log), plus the one malformed read; report how many fields were recovered and the cost. Commit.

TASK 3. Tool 10 seed on the site: add energy_companies to the live set and build /companies: a filterable table (sector, niche tags, stage, state, confidence), each row expandable to description, founders, raised, sources and the confidence clause, with a scope note that the table grows from Thesis Builder runs and the deal tracker; link from Investors on the home page and from /deals. Cross-link company names in /deals to their /companies rows where names match.

TASK 4. Regenerate the chat spec after every llms.txt change (add a check to run_daily.sh that fails if spec.json is older than llms.txt). Validator, coverage, live set, value check, screenshots of /companies and the changed pages, SESSION_26_REPORT.md. Final commit and push.