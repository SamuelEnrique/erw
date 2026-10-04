# Session 99 report: who is buying

**Built, on `wip/099-buyers`, nothing loaded and nothing deployed.** The 17,955 buyer names of `ferc_eqr_contracts` are brought to one spelling by rule and counted as 13,836. Every merge is listed for a person to check; 1,281 doubtful pairs are listed apart and not merged. `/contracts` has a second view, "The largest buyers and sellers", for energy, capacity and tolling. The three new tables are internal, as their input is, and are in no file of the repository.

## To make it live

```bash
# Nothing below was run. No preview address: GitHub recorded no Vercel deployment for this branch's push.

# 1. THE THREE TABLES into the warehouse's records (internal: Redivis's internal dataset, not the public one).
git fetch origin && git checkout wip/099-buyers && git merge origin/main
python warehouse/lock.py run --task "EQR buyers" --minutes 10 -- <the venv's python> warehouse/derived/eqr_buyers.py
python warehouse/validate/erw_validate.py warehouse/output/ferc_eqr_buyer_names.csv warehouse/output/ferc_eqr_buyer_doubtful.csv warehouse/output/ferc_eqr_party_totals.csv   # exit 0
python warehouse/metadata/build_coverage.py                                 # read its exit code; all three must show license internal
python warehouse/archive/archive.py --tables "ferc_eqr_(buyer_names|buyer_doubtful|party_totals)" write
python warehouse/redivis/upload.py --check-license                          # before any upload: internal tables go to the internal dataset only
python warehouse/redivis/upload.py --tables ferc_eqr_buyer_names ferc_eqr_buyer_doubtful ferc_eqr_party_totals

# 2. THE VIEW'S FIGURES. The page reads the stored summary of the contract table; the loader fills it. No migration.
#    After the freeze (the loader writes the live set):
python warehouse/supabase/load.py              # stores the summary with the largest buyers and sellers; read its exit code
#    Until then /contracts?view=largest says "not loaded here yet". The three tables themselves are not loaded and
#    need no live-set rule: only the first 25 of each list travel, inside the summary, behind the internal token.

# 3. THE PAGE (in review, internal view only). A push to a task branch redeploys the site; no live page changes:
python -m unittest tests.test_session99                                     # read its exit code
cd site && node scripts/snapshot-live.mjs take before-099 && cd ..
git push origin wip/099-buyers:task/099-buyers
cd site && node scripts/snapshot-live.mjs take after-099 && node scripts/snapshot-live.mjs compare before-099 after-099
```

**Read these four first:**

1. **Where the lists for you to check are.** On the data machine, not in git: `warehouse/output/ferc_eqr_buyer_names.csv` (every name as filed, the name it is counted under in `x_counted_as`, the rules that changed it in `x_rules`, and `x_merged` yes or no: sort by `x_key` to read a group) and `warehouse/output/ferc_eqr_buyer_doubtful.csv` (each pair in `parties`, the reason in `x_reason`, sorted so that the pairs filed on the most rows come first). They become readable anywhere once step 1 puts them in the internal Redivis dataset.
2. **One rule goes further than spelling, and you may want it off.** `suffix_left_off`: a name filed with no legal form is counted with the same name filed with exactly one legal form ("Example Power" with "Example Power Company"). 564 names were joined this way. It is a rule and every case is listed, but it rests on a belief that the bare name is the same company. Where the same name is filed with two different legal forms, nothing is merged and the pairs are in the doubtful list. If you read "never merged on a guess" more strictly than I did, it is one block of `groups_of` and the count after the rules rises by those 564 less their groups.
3. **The view is by contracts, not megawatts, and the market operators lead it.** Only 8,060 of the 66,192 rows in force of the three products file a quantity in MW, so a ranking by megawatts would rank who fills in a column. The page ranks by contracts in force and shows the MW filed and the rows it rests on. The grid operators stand at the top of the buyers of energy and capacity because a sale into an organized market is filed with the operator as its customer; the page says they are counterparties of record, not users of the power.
4. **The view shows no figure on production until you load.** I did not store anything in the database tonight: the freeze, and the stored summary belongs to a load. The view was checked on the built site against a stand-in for the database that serves the summary the loader would store, from a file kept out of git. Against the real database the view says "not loaded here yet", and the page's first view is as it was.

Energy Research Warehouse (ERW), session 99, on the old laptop (`samueloldlaptop`, data role), 2026-10-04 from about 11:04 to 11:30 UTC, unattended. **Model spend: USD 0.00.** No pull, no request to any publisher, no model call (the names are merged by rule, not by a model), no load, no force push, no deploy. The data lock was taken once (under a minute) and is free.

## The license

`ferc_eqr_contracts` is internal by session 83's ruling: FERC's filings are public, but the data machine could not read FERC's license statement (its site answers automated requests with HTTP 403), so the table is held for internal use. No new source was read. A derived table inherits its input's license: the three tables are internal in their headers and in the source registry's entry; a test holds that no file of theirs is tracked by git, that the page reads no file of the site for them, and that none of the names at the top of the real lists appears in any file this session wrote, this report included.

## The names

`warehouse/derived/eqr_buyers.py`. Two names are one buyer only when every rule leaves them identical:

| Rule | Names it changed |
|---|---|
| `case_space`: capitals; spaces closed up | 15,189 |
| `punctuation`: "&" as "and"; periods, commas, apostrophes, brackets out; a hyphen or slash as a space | 10,319 |
| `abbreviation`: a short list of whole words written one way (Corp, Inc, Co, Ltd, Coop, Assn, Elec, Dept and ten more) | 1,885 |
| `suffix_left_off`: a name with and without its one legal form | 564 |
| `leading_the` | 221 |
| `legal_suffix`: L L C as LLC, Limited Partnership as LP and the like | 67 |

A rule that changes a name does not always merge it: most names are changed by `case_space` because the key is in capitals. 17,955 names as filed are 13,836 after the rules; 2,341 of those groups hold more than one name, 6,460 names in all.

Two places where a rule holds back: "Co" is left alone as the last word of a name that begins City, Town, Village, County or Borough, or that holds "of" (there it may be Colorado); and likeness of spelling is never used to merge, only to list a pair. A test reads the builder's merging code and holds that it does not call the likeness measure.

**Doubtful, 1,281 pairs, none merged:**

| Reason | Pairs |
|---|---|
| `different_legal_form`: the same name under two legal forms (an LLC and an Inc may be two companies) | 245 |
| `extra_clause`: a name that is another plus a d/b/a, f/k/a, "as agent for" or bracketed clause | 349 |
| `near_spelling`: 12 letters or more, at least 94 percent alike, not differing by a number | 687 |

A project's I and II, or 1 and 2, are two companies and not a doubt; such pairs are not listed. I read a sample of each rule's merges and of each kind of pair before building: the near spellings are mostly typing errors in a utility's or an operator's name, with some that are plainly two things (two states' subsidiaries of one marketer) and are rightly left for a person.

**What the rules do not do:** a parent and its subsidiaries stay apart, and a misspelling stays apart until a person rules on its pair. A buyer's count is a floor. "Who is buying" at the level of a corporate family needs a table of parents kept by a person; the same was true of the storage owners in session 87.

## The totals and the view

`ferc_eqr_party_totals`: 12,290 rows. Over the 66,192 rows in force whose product is energy, capacity or tolling energy: each buyer by its merged name and each seller by FERC's company identifier, with contracts (a filer's contract identifier), rows, counterparties, and the MW filed with the rows that file one.

| Product | Contracts in force | Rows | Buyers, after the rules | Sellers |
|---|---|---|---|---|
| Energy | 22,808 | 47,883 | 4,517 | 2,824 |
| Capacity | 12,598 | 17,928 | 3,188 | 1,531 |
| Tolling energy | 216 | 381 | 128 | 102 |

`/contracts` now opens with two views. The first is the page as it was (the contracts by the quarter signed). The second, `/contracts?view=largest&product=energy|capacity|tolling`: a sentence, three numbers, the first 25 buyers and the first 25 sellers, and two folds: how a buyer's names are brought together (with the two tables' names, and that a count is a floor), and what the ranking is and is not (by contracts, not megawatts; in force, not new; not Texas).

The page reads the contract table's stored summary, as before. `warehouse/supabase/load.py` gained `eqr_largest`: the first 25 of each list and the counts of the name rules, added to the summary the loader stores (22 kB). The database function that stores the summary takes it whole, so no migration is needed.

## Tests and checks

| Check | Result |
|---|---|
| `tests/test_session99.py` | 9 tests pass, on made-up names only. Each rule and what it records; "Co" held back; thirteen made-up names counted as ten, with the bare name joining its one legal form, two legal forms not merged, a d/b/a and a typing error listed and not merged, a project's I and II neither merged nor listed; the merging code does not use likeness, a model or a request. The totals on rows made for the test (two spellings of a buyer are one counterparty of its seller). The loader's summary from tables written to a temporary folder, and none when the tables are absent. The tables as built: every name less is a name merged; each product's contracts and rows equal by buyer and by seller. The three tables ignored by git; none of the real lists' leading names in any file of the session |
| `site/scripts/check-contracts-largest.mjs`, the built site against a stand-in | 18 checks pass: for each product every figure and every name is the summary's (160 to 164 figures, 50 names); most contracts first; the folds; `/contracts` opens on the first view with a link to the second; a view it does not understand opens the first; with a summary stored before this view existed it says so and shows no table; a visitor gets the in-review page with no name and no figure; the site read the stand-in |
| The built site against the real database | `/contracts` as before; `/contracts?view=largest` says "not loaded here yet" |
| Sessions 83's and 90's tests of the page and the summary | pass (one of session 83's failed first: it counts the list items between two points of the page's file, and my component sat between them; moved below) |
| Site: types, build (twice), route check | exit 0 each; no statement cancelled. Route check: 111 of 111 pages, and 16 live with 95 in review as a visitor |
| `check-values.mjs` | exit 0: 7,499 of 7,530 values match and 31 are latest prices a newer interval replaced during the run |
| The validator on the three tables | exit 0 each |
| A screenshot of the capacity view, from the stand-in | looked at (kept out of git). The names were right-aligned like numbers; now left-aligned |

## Errors and decisions

- **Error, mine, in a look and not in the tables:** my first reading of the party totals used pandas' `comment="#"` and came 17 buyers short, because names can hold a `#`. The builder and the loader count and skip the header's lines instead. It is the fault session 95 reported, met again.
- **Error, mine, caught by the validator:** a status of "merged" and "in force" is not in the standard's list for entities. The merge flag is its own column.
- **Decision: no model.** You asked for rules. A model would merge more and explain less; every merge here can be read off its row.
- **Decision: sellers are not merged by name.** A seller is a filer with one company identifier.
- **Decision: the three tables are not loaded,** only the first 25 of each list inside the summary. The full lists are for a person, in Redivis's internal dataset.
- **Decision: the summary file for the check is refused inside the repository.** `warehouse/supabase/eqr_fixture.py` writes only under `runs/` or outside the repository.

## For Samuel

1. **The doubtful pairs:** 1,281 to rule on, most-filed first. The first few dozen carry most of the rows. There is no list of accepted pairs yet; when you have one, the builder reading it is a small change.
2. **`suffix_left_off`** (the second point above): keep or drop.
3. **A table of parents,** if "who is buying" should mean corporate families.
4. **Not in any cloud:** the three tables are only in `warehouse/output` on this machine until step 1 is run.
