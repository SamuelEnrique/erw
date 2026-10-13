# TasteSkill audit of /cost-of-power/battery, session 211 (an audit only)

The skill: `redesign-existing-projects` from https://github.com/Leonxlnx/taste-skill, installed at the user level of
Claude Code on the old laptop (`~/.claude/skills/redesign-existing-projects/SKILL.md`, copied, not symlinked; the one
skill of the repository, for the `claude-code` agent; `npx skills add ... -g -y --copy`, exit 0, no prompt). It is a
checklist in seven parts (typography, color and surfaces, layout, interactivity, content, components, iconography, code
quality, strategic omissions) and a list of "upgrade techniques". It was read against the page's code on
`wip/203-brand-battery` (page.tsx, brand.css, BatteryForm.tsx, Scenarios.tsx, the shared ScenarioBlock.tsx and
ToolPage.tsx, app/layout.tsx) and the page as built, in the internal view, at 1280 and 390 px
(`runs/session211/shots/before_1280.png`, `before390_390.png`). No question asked; no file of its own written.

The rule of the chain prompt: apply only what is new against Impeccable's audit of session 208
(`runs/session208/impeccable_audit.md`) and keeps `docs/brand.md` (direction A, light only, no animation, every number
unchanged). A suggestion the brand forbids is listed as rejected, with the reason.

## What it flags, and what became of each

| # | The skill's item | On this page | Impeccable 208 | Outcome |
|---|---|---|---|---|
| 1 | Default fonts or Inter everywhere; swap to Geist, Outfit, Satoshi | Source Serif 4, IBM Plex Sans, IBM Plex Mono (the brand's three) | not raised (passes) | passes; the swap is rejected: the brand names the families |
| 2 | Headlines lack presence: tighter letter-spacing, lower line-height | h1 36 px serif 600, line height 1.15 | not raised | rejected: the brand says no letter-spacing, and sets the line heights |
| 3 | Body text too wide (about 65 characters) | notes and the lead at most 68ch (`brand.css`) | not raised | passes |
| 4 | Only 400 and 700 weights | 400, 500, 600 in use | not raised | passes |
| 5 | Numbers in a proportional font; no tabular figures | `lining-nums tabular-nums` on the page; mono in table cells | not raised | passes |
| 6 | All-caps subheaders | the headline labels' `uppercase` is undone by the brand sheet | not raised | passes |
| 7 | Orphaned words: `text-wrap: balance` or `pretty` | neither was set | **not raised** | **new; applied**: titles balanced, paragraphs, captions and the fields' notes set pretty (`brand.css`). Line breaks only, no number |
| 8 | Pure black, oversaturated accents, more than one accent, warm and cool greys mixed, the "AI gradient" | white page, cardinal only (saturation about 73 percent), warm greys; the chart's blue is a series color the brand lists | not raised | passes |
| 9 | Generic shadows, flat design with no texture, even gradients, noise overlays, background imagery | none of them; the one gradient is the fade at a scrolling table's edge (an affordance) | not raised | rejected where it asks for texture, noise, shadows or imagery: the brand says "no shadow, no gradient, no texture" |
| 10 | A dark section in a light page | the table headers' cardinal bands are undone by the brand sheet; the active segment of a control is cardinal (the brand's job for it) | not raised | passes |
| 11 | Everything centered; three equal card columns | left-aligned; the three headline numbers are a row of three figures, not feature cards | not raised | rejected for the headline row: three figures on one rule is the page's form, not a feature row |
| 12 | `height: 100vh` | none | not raised | passes |
| 13 | No max-width container | `main` is `max-w-6xl` (`app/layout.tsx`) | not raised | passes |
| 14 | Uniform border radius; "vary the radius" | the brand's corners are square; **the sensitivity chart's bars carried rounded ends** (`borderRadius: 4px` on each bar, in the shared block) | **not raised** | **new; applied** for the square half: the bars' ends are square on this page (`brand.css`, by the bar's own inline style, as the colors are). Varying the radius is rejected: section 3 of the brand |
| 15 | No overlap or depth; asymmetric padding; broken grid | none | not raised | rejected: the brand's steps and its "no shadow" |
| 16 | Inconsistent vertical rhythm in side-by-side elements | **the three headline numbers sat on different lines**: the middle label ("A bad month: the 10th percentile, last 36 months") wraps to two lines at 1280 px, so its number sat one line below the other two (session 208's screenshot shows it) | **not raised** | **new; applied**: the row is a grid whose three children share its rows (`grid-template-rows: subgrid`), so the label, the number and the note of each column sit on the same three lines. No number changes |
| 17 | No hover state on buttons | every button has one (the fog background; the one action one step darker) | not raised | passes |
| 18 | No pressed feedback (`scale(0.98)`); transitions of 200 to 300 ms; smooth scroll; staggered entry, spring physics, scroll-driven reveals | none | not raised | rejected, all of them: the brand's "No motion. A change the reader makes is shown at once" |
| 19 | Missing focus ring | a 2 px ink outline on every link and control | raised as passing | passes |
| 20 | No loading, empty or error states | the page is server-rendered; "not held" cells and "No month is held" are the empty states; a number typed outside a field's bounds is clamped without a message | not raised | for Samuel's ruling (a message is words): see below |
| 21 | Dead links; no current page in the navigation | the one `#` link is the panel's anchor to the scenarios; the three tabs carry `aria-current` and the ink-over-cardinal rule | not raised | passes |
| 22 | Fake round numbers, placeholder names, Lorem Ipsum, AI copy cliches, exclamation marks, Title Case | real data; sentence case; none of the words | not raised | passes |
| 23 | Generic card (border, shadow, white); one filled plus one ghost button | the panels are fog with a rule-colored edge; the form's one action is filled, the Resets are outlined | not raised | passes; a text-style Reset would be a change of the control's form, for the ruling if wanted |
| 24 | Accordion FAQ; modals; pill badges; carousels; avatars; footer link farm | one disclosure ("The chart as a table", the keyboard's and the screen reader's copy of the chart); nothing else of the list | not raised | passes |
| 25 | Lucide or Feather icons; cliche metaphors; missing favicon | no icon on the page; the site has its mark as the icon | not raised | passes |
| 26 | Div soup | `header`, `nav`, `aside`, `section`, `figure`, `table`, `fieldset`, `details` | not raised | passes |
| 27 | Inline styles mixed with classes | the shared block's two chart colors and the white of an active segment are inline literals | **raised**, P3 (theming; waits for the brand's approval, three tests hold the literals) | already caught; not changed here |
| 28 | Hardcoded pixel widths | the sidebar's 290 px, the tables' minimum widths, the year chart's 600 px on a phone, the chart's 280 px label column | not raised | kept: each is a floor below which a table or a chart cannot be read, and the frame scrolls inside itself |
| 29 | Missing alt text | the year chart is `role="img"` with its label; each year carries a `title` | not raised | passes |
| 30 | Arbitrary z-index | none | not raised | passes |
| 31 | Commented-out dead code | `Contract.tsx` on disk, imported by nothing | known (session 208, decision 3) | kept: CLAUDE.md rule 3 (no deleting); the session 208 report says why |
| 32 | Missing meta tags | the page sets its title; the site's layout sets the description | not raised | passes |
| 33 | No legal links; no way back; no form validation | Terms and Privacy in the footer; the tabs and the header lead back; the number fields carry `min`, `max` and `step` | not raised | passes |
| 34 | No "skip to content" link | **the site's layout has none** (`app/layout.tsx`) | not raised | for Samuel's ruling: a site-wide change, not this page's |
| 35 | No custom 404 page | the site has no `not-found.tsx` | not raised | for Samuel's ruling: site-wide |
| 36 | No cookie consent | the page sets no cookie for a visitor (the internal view's is the owner's) | not raised | passes |
| 37 | The chart titles are spans, not headings; the grid list names five grids a visitor cannot open | (Impeccable's own findings) | raised, P3 | not in this checklist |
| 38 | Every Reset reads "Reset" (one name for twelve controls) | the brand's section 7 asks for a Reset "named for its field" | not raised (Impeccable said every control has a name; it did not say they are the same name) | **new; applied**: `aria-label="Reset <the field's label>"` on the shared block's Reset, one attribute; what is drawn is unchanged |

## New against Impeccable 208, in one list

Applied (four, none moves a number, none adds motion, color or texture):

1. The headline row's three columns share their rows (16).
2. The sensitivity bars' ends are square (14).
3. Titles balanced, text set pretty (7).
4. A field's Reset is named for its field (38).

Rejected, with the reason:

- The font swap (1), letter-spacing (2), texture, noise, shadows, imagery and gradients (9), overlap and asymmetry (15), pressed feedback, transitions, smooth scroll and every "upgrade technique" (18), a varied radius (14): each against a line of `docs/brand.md`.
- The three headline numbers as something other than three columns (11): the row is the page's form, not a feature row.
- The pixel floors of the tables and the charts (28).

For Samuel's ruling (words or structure, or the whole site):

- A line under a number field when a typed value is clamped to its bounds (20).
- A "skip to content" link in the site's layout (34), and a custom 404 page (35).
- A text-style Reset instead of an outlined button (23), if the panel should be quieter.

## What Impeccable 208 caught that this checklist did not

The colors as literals (27, shared), the chart titles as spans, the grid list beside its one line, the 32 px touch
targets (fixed in 208), and the "no step held" wording of a row with no movement (fixed in 208).

## Check of the fixes

See the session report: the page rebuilt, 51 checked numbers identical before and after the fixes at 1280 and 390 px,
`check-values` and `check-battery-scenarios` on the build.
