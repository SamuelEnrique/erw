# Progress of chain 630 (lab-desktop second window, the codebook)

One line a step or a family of tables: state, counts, session. States: done (with the commit), partial (which tables wait), waiting (what for).

- Queue: 630 taken by hand (chain_queue refuses a window mark on the data machine), bce5bc7b4. Session 9200.
- Resume file `queue/next/631-resume-chain-630.md`: done. Session 9200.
- Part B, read fields: done for the 582 public tables (`warehouse/codebook/build_variables.py --group 1` and `--group 2`, 2026-11-20; no failure); `_shared.yaml` holds the data standard's 32 names. Session 9200.
- Part B, written fields (row, labels, units, missing meaning, source names, variable labels): partial. Group 1 (196 tables): 92 written in full as of 11:05 UTC; group 2: 20. Families done: ba, eia (group 1). Hand files in `runs/c630/hand/` (inputs only; the table files hold the result). Session 9200.
- Part C, the test: written, `tests/test_codebook.py` on `wip/c630-codebook`; six of seven checks pass, the unit check waits for part B. Not requested for landing yet. Session 9200.
- Part D1 (site): `site/components/Codebook.tsx` and the method page, on the branch; build and 1280/390 checks wait for part B. Session 9200.
- Part D2 (package): `erw.describe()`, `erw.variables()`, `package/tools/build_codebook.py`, tests (5 pass), README and packages.md, on the branch. Session 9200.
- Part D3 (llms.txt and the chat): `scripts/build_llms.py` and `warehouse/chat/tools.py describe_table` read the codebook, on the branch; llms.txt is rewritten at landing. Session 9200.
- Part D4 (Redivis): `warehouse/redivis/codebook.py` writes `docs/redivis/codebook/` and applies it to a draft under the lock; `upload.py` takes its descriptions and labels. On the branch; the data request row is filed with the landing. Session 9200.
- Part E (documents): `warehouse/codebook/build_docs.py` draws `docs/codebook/` (50 family documents and the index); redrawn after each family. Session 9200.
- Part A, the ground: done, `docs/reviews/codebook-plan-2026-11-20.md` and `.csv` (698 tables, 50 families; 196 public read by the site, 386 other public, 116 internal; 568 series, 74 entities, 56 events). Session 9200.
