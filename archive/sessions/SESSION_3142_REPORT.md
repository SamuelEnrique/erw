# Session 3142: chain 178's ninth session (its 3142): the fresh audit's figures and scope

Personal laptop, second window, 6 November 2026, 14:44 to 14:48 UTC. Opus 5.5. Branch `wip/3142-policy` cut from `wip/3141-policy`.

## What it did

- `warehouse/policy/fields.py`: a notice without a summary is read for its figure over 4,000 characters, not 1,800; inside that read, a figure after a stated total's words comes first; the scope list gains an inventory under the Native American Graves Protection and Repatriation Act. Tests for both (`test_the_figures_of_the_fresh_audit`, the scope case).
- `site/data/policy/monitor.json` rebuilt; the fresh audit's file records the session.

## What it found

- Fresh sample: figures 12 of 12 (10 before), scope 80 of 80 (79 before); first sample: no figure changed. The wider read alone took a listed unit's figure over a stated total in session 3126's test (596 kW over 2,980 kW); the total's precedence fixed it before the commit.
- With 3140 to 3142, every class of the fresh audit holds on its 80. `test_policy_fields.py` and `test_policy_monitor_site.py` 22 passed.

## Decisions made without you

- **r26's figure is its first system's** (10,000 Dth/d of liquefaction, beside 120,000 Dth/d of vaporization): the rule takes the first size stated, and the record's words show both.

## For Samuel's ruling

- None new.

## Cost

- Model: none (USD 0.00).
