# Session 291 report: the battery game takes the brand

14 October 2026, unattended, on samueloldlaptop (the code machine), the fourth session of the afternoon chain. Branch `wip/games-v2`, pushed, **not landed**. Model spend USD 0. No pull, no warehouse data written.

## Read these first

- **`/play/battery` draws inside `<Brand>`** (ruling 15): white page, the serif titles, the sans text, mono figures in tables, square corners, no motion, no green. Charging is ink, selling cardinal, everywhere (buttons, the chart's moves, the house's wire).
- **The canvas reads the brand's tokens from its wrapper.** Until now it read the site's old palette from the page root (cream and the old rule colour) and wrote three `rgba` colours of its own; it now writes no colour, and draws in IBM Plex Sans and Source Serif 4 at 12 px or more.
- **Cardinal does its three jobs only:** a link, a control in its active state (Start, a held Sell, Play again), the highlighted series (the emergency's spiked price). The status banners, warnings and the reserve line moved to ink and grey.
- **Direct labels:** the moves under the chart are two named rows ("buy" in ink, "sell" in cardinal); the replay names its two lines at their ends with their earnings, and the reserve line; its legend box is gone.
- **Impeccable `detect`: no findings** (exit 0).

## What to review

Screenshots: https://github.com/SamuelEnrique/erw/tree/wip/games-v2/docs/reviews/games-2026-10-14/291 (22 before, 22 after, the same screens).

1. The pick screen: `before/01-easy-pick-1280.png` against `after/01-easy-pick-1280.png`.
2. Easy playing at 390 px: `before/03-easy-playing-390.png` against `after/03-easy-playing-390.png`.
3. Hard in the emergency: `before/07-hard-status-2-1280.png` against `after/07-hard-status-2-1280.png`.
4. The end: `after/08-hard-done-1280.png`.

Locally: `C:\Users\lossa\Documents\erw-279\site`, `npx next start -p 3289`, unlock at http://localhost:3289/internal/unlock?token=<INTERNAL_COSTS_TOKEN>, then http://localhost:3289/play/battery .

## What was done

- `page.tsx`: the page wrapped in `<Brand>`; every paragraph and list of the rules at the 68-character measure (the brand's `max-w-3xl` rule).
- `Game.tsx`:
  - tokens read from `.brand-a` (`css()`), fonts from the brand's `--font-sans` and `--font-serif` (`face()`, never under 12 px); the vpp hour on fog, the outage hatched in the rule colour (brand section 6), the old forecast band on fog;
  - the mode picker drawn as the shared picker's segments (`components/tool/Choose.tsx`'s look: the mode in view filled ink), as buttons with `aria-pressed` so a play is not cut off by a link;
  - buttons `type="button"`, so the brand's control rule applies; the held control fills (ink to buy, cardinal to sell);
  - the house: no animation (it had a flowing wire), a square battery filled in ink, 12 px labels;
  - fleet map squares, the state of charge in ink, the money in the serif as a headline number, the day-at-a-glance figures in the serif;
  - the share card on white with an ink rule, its figures in the brand's faces (no cardinal band);
  - axis numbers above their grid lines; at 390 px the money sits under the charge bar.
- Tests: sessions 50 (no motion left, so nothing for reduced motion), 289 (the picker), 290 (the table's heads) follow; `check-battery-game.mjs` reads the picker's `aria-pressed`.

## Checks

| Check | Exit | Notes |
|---|---|---|
| `scripts/precheck.py` | 0 | |
| `tsc`, `eslint` | 0, 0 | |
| `node scripts/test-battery.mjs` | 0 | its Part B (no played price printed outside the library's labelled text) still passes |
| Tests of sessions 50, 56, 66, 111, 289, 290 | 0 | 57 |
| `npm run build` (worktree) | 0 | |
| `check-values.mjs`, Games pages | 0 | 105 of 105 |
| Screenshots after, 1280 and 390 | 0 | 22, no sideways overflow, no page error (the 390 px browser check the prompt asks for) |
| Impeccable `detect --json` on `Game.tsx` and `page.tsx` | 0 | `[]` |

## Decisions made without you

- **Buy is ink, sell is cardinal**, the brand's first two series colours, in every place the game shows a move. The held Sell button is cardinal as a control in its active state; the held Charge button is ink.
- **The status banners are ink on fog**, not cardinal: the brand gives cardinal no warning job. The spiked price stays cardinal (the highlighted series).
- **The mode picker is buttons drawn like the shared picker**, not `ToolPicker` itself: its links would reload the page mid-play.
- **No change to `tokens.css` or any shared component**: the game uses the brand's rules as they stand.
- **Impeccable ran as `detect` only** (no `critique`: it asks questions and writes `.impeccable/`, which an unattended session does not do).

## For Samuel's ruling

- The house drawing: kept (static now). It is the game's one illustration; the brand says nothing of illustrations.

## Files

- New: `docs/reviews/games-2026-10-14/291/`, this report.
- Changed: `site/app/play/battery/Game.tsx`, `site/app/play/battery/page.tsx`, `site/scripts/check-battery-game.mjs`, `tests/test_session50.py`, `tests/test_session289.py`, `tests/test_session290.py`.
