# Session 3140: chain 178's seventh session (its 3140): the fresh audit's instruments; the push

Personal laptop, second window, 6 November 2026, 14:38 to 14:46 UTC. Opus 5.5. Branch `wip/3140-policy` cut from `wip/3139-policy`.

## What it did

- `warehouse/policy/fields.py`, the instrument rules (the fresh audit's largest class, 9): an order on a petition; a scoping period before its sessions; a hearing's notice, a technical conference, an open house, meetings in the plural; an environmental review's schedule; a general permit as an approval (proposed when its title begins "Proposed"); an award only with its words in the title or beside a sum of money. A test with the nine rows' titles and action lines, and the NRC's "order imposing procedures" kept an application's notice.
- `site/data/policy/monitor.json` rebuilt; the fresh audit's file records the session.
- Pushed; the related tests started for the landing request.

## What it found

- Class 5 on the fresh sample: 80 of 80 (71 before); on the first sample unchanged (14 of 14). A first version read three NRC application notices as orders (their action line's "order imposing procedures"); caught by comparing every row of both samples, fixed before the commit. `test_policy_fields.py` 17 passed.

## Decisions made without you

- **A general permit is an approval** in the instrument vocabulary (an agency granting what the permit allows), rather than a new instrument.

## For Samuel's ruling

- None new.

## Cost

- Model: none (USD 0.00).
