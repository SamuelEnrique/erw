-- Energy Research Warehouse (ERW), session 289.
--
-- Battery game v5 (site/lib/battery.ts, RULES_VERSION): a play's preset ends "-v5", with Hard's add-ons before it as in
-- v4, so the leaderboard ranks version 5 plays only against version 5 plays with the same mode, battery and add-ons.
-- The default backup reserve is 25 percent since v5 (Samuel's ruling of 14 October 2026):
--
--     easy:13.5-5-90-v5
--     hard:13.5-5-90-r25-d0.11-v5
--     hard:13.5-5-90-r25-d0.11-solar-v5
--
-- Presets written before stay valid and keep their own boards: none ("v2 rules"), "-v3", and "-v4" with its add-ons.
-- Constraints only: no column, no table, no grant changes.
--
-- Written in session 289 and NOT applied by it (a code machine writes no warehouse data, and the games branch is not
-- landed): apply it before the v5 site is deployed. Until then the database refuses a v5 play, and the page says the
-- play was not stored.
alter table public.game_scores drop constraint if exists game_scores_preset_check;
alter table public.game_scores add constraint game_scores_preset_check check (preset ~ '^(easy|normal|hard):[0-9.]+-[0-9.]+-[0-9]+(-r[0-9]+-d[0-9.]+)?(-v3|(-[a-z]+)*-v4|(-[a-z]+)*-v5)?$');
alter table public.game_plays drop constraint if exists game_plays_preset_check;
alter table public.game_plays add constraint game_plays_preset_check check (preset ~ '^(easy|normal|hard):[0-9.]+-[0-9.]+-[0-9]+(-r[0-9]+-d[0-9.]+)?(-v3|(-[a-z]+)*-v4|(-[a-z]+)*-v5)?$');
