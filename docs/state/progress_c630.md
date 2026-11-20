# Progress of chain 630 (lab-desktop second window, the codebook)

One line a step or a family of tables: state, counts, session. States: done (with the commit), partial (which tables wait), waiting (what for).

- Queue: 630 taken by hand (chain_queue refuses a window mark on the data machine), bce5bc7b4. Session 9200.
- Resume file `queue/next/631-resume-chain-630.md`: done. Session 9200.
- Part B, read fields: done for the 582 public tables (`warehouse/codebook/build_variables.py --group 1` and `--group 2`, 2026-11-20; no failure); `_shared.yaml` holds the data standard's 32 names. Session 9200.
- Part B, written fields (row, labels, units, missing meaning, source names, variable labels): group 1 done (196 of 196 tables, 1,167 own columns, 4,497 variables), sessions 9200 and 9201. Group 2: 242 of 386 written at 11:21 UTC; four agents on the rest (ISO markets and NOAA; other sources; EIA forms, UK, Canada and federal; EPA, NRC, ORNL, LBNL, DOE and the rest). Hand files in `runs/c630/hand/` (inputs only; the table files hold the result).
- Part F, internal tables (group 3, 116): read fields done with values withheld (session 9200); written fields under way (two agents), session 9201.
- Data request 564 filed (session 9201): `interconnection_queue_summary`'s `active_mw_parts_*` carry unit count but are MW.
- Part C, the test: written, `tests/test_codebook.py` on `wip/c630-codebook`; six of seven checks pass, the unit check waits for part B. Not requested for landing yet. Session 9200.
- Part D1 (site): `site/components/Codebook.tsx` and the method page, on the branch; build and 1280/390 checks wait for part B. Session 9200.
- Part D2 (package): `erw.describe()`, `erw.variables()`, `package/tools/build_codebook.py`, tests (5 pass), README and packages.md, on the branch. Session 9200.
- Part D3 (llms.txt and the chat): `scripts/build_llms.py` and `warehouse/chat/tools.py describe_table` read the codebook, on the branch; llms.txt is rewritten at landing. Session 9200.
- Part D4 (Redivis): `warehouse/redivis/codebook.py` writes `docs/redivis/codebook/` and applies it to a draft under the lock; `upload.py` takes its descriptions and labels. On the branch; the data request row is filed with the landing. Session 9200.
- Part E (documents): `warehouse/codebook/build_docs.py` draws `docs/codebook/` (50 family documents and the index); redrawn after each family. Session 9200.
- Part A, the ground: done, `docs/reviews/codebook-plan-2026-11-20.md` and `.csv` (698 tables, 50 families; 196 public read by the site, 386 other public, 116 internal; 568 series, 74 entities, 56 events). Session 9200.
