# Motion proofs of the hunt's strong drafts of 14 October 2026 (session 286)

Energy Research Warehouse (ERW). Session 274's pipeline (`motion/specs.mjs`, `motion/render.mjs`), run on the two drafts
that session 286 verified as strong (`docs/reviews/findings-verified-2026-10-13.md`, blocks 29 and 30). Nothing was
posted anywhere. Both drafts are still drafts on `/internal/findings`: a proof is not an approval.

| Proof | Draft | Motion type | Seconds |
|---|---|---|---|
| `scan-hunt-7a9b1b9695e1` | PJM's evening ramp, 2,484 to 3,805 MW per hour, 2019 to 2025 | draw-on | 15 |
| `scan-hunt-4aa7db84eaa1` | ERCOT's demand growth that weather does not explain, 7.8 to 24.2 percent above the 2019 to 2021 base, 2022 to 2025 | draw-on | 15 |

Each in two sizes (1080x1350 and 1080x1080), with a still of its last frame. The specs are in `specs/`, here and not in
`motion/specs/`, whose set of seven proofs session 274's tests hold.

## How they were made

1. The draft's card (`runs/hunt/2026-10-14/<id>.json`, the hunt's own file) with its `id` set to the draft's id (every
   hunt card's id is `hunt_pattern`), then `node specs.mjs <file>`.
2. Words changed in the two specs after the first render, each because the still showed a fault. No number changed:
   every value in a spec is the card's chart value, which is the draft's CSV value for that year (`tests/test_session286.py`).
   - Both: the end label's unit removed (`series[0].unit`), because the line beneath it already gives the unit and the
     two together ran off the frame ("3,805 MW per").
   - ERCOT: the title "DEMAND GROWTH THAT WEATHER DOES NOT EXPLAIN: ERCOT (ITS DATACENTER MARKETS: DALLAS, AUSTIN AND SAN
     ANTONIO)" set to "ERCOT'S DEMAND GROWTH", and the subtitle shortened to "Dallas, Austin and San Antonio: the year's
     energy above the 2019 to 2021 base that temperature does not explain, 24.2 percent in 2025, up from 7.8 percent in
     2022." (the same two numbers and years): at six lines the title pushed the axis and the source line off the frame.
     The axis words "percent above the 2019 to 2021 base" set to "percent above base" (the subtitle names the base).
3. Rendered with the packages session 274 installed in its worktree (`../erw-274/motion`, Remotion 4.0.535): this
   checkout has no `node_modules` under `motion/`, and the code there differs from main's only in line endings.

The card's own line "The direction holds in 3 of the 3 full years after 2022." is not in the ERCOT proof's shorter subtitle; the
PJM proof keeps the card's subtitle whole.
