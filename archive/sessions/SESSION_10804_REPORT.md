# Session 10804 report (chain 740, lab-desktop window 3): the note, the cross-check, the replication

- **What a reader sees:** nothing new on the page (not landed).
- **`docs/methods/forecast.md` section 13** (main, internal): what the datacenter computes, its defaults and sources, the states held, twelve decisions with what the other choice would give, the cross-check, the check keys.
- **Cross-check** (`site/scripts/dc-crosscheck.mjs`, `docs/reviews/impact-datacenter-crosscheck-2026-11-26.json`, branch): JLARC's "about $9 million to $15.5 million" for a typical USD 250 to 325 million Virginia datacenter is reproduced (USD 9.04 to 15.52 million at the lowest and highest rates; 9.84 to 12.79 at the average). Alabama's Huntsville release ("$297.3 million" over 30 years) is not comparable: the model holds no Alabama abatement or property rate; its sales tax before exemptions (290.3 million) and income tax (13.0 million) are stated with that cause. LED's 1.9 indirect jobs per operational job beside Virginia's 2.389.
- **Replication** (`replication/impact/datacenter/`, branch): `replicate.py`, written from the note, agrees with the page on every figure of its cases; `replicate_datacenter.do` (not run: no Stata on the machine).
- **Commits:** the cross-check and the replication (branch); the note (main; one push rejected by the remote, the retry passed).
- **Needs the key:** nothing.
- **Decisions made without you:** the cross-check's Alabama case is kept beside the model with its cause, not dropped and not tuned.
- **For Samuel's ruling:** nothing new.
