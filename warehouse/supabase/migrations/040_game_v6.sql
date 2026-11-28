-- Energy Research Warehouse (ERW), session 11407 (chain 770, a ready branch for Samuel's ruling, not landed by it).
--
-- Battery game v6 (site/lib/battery.ts, RULES_VERSION): the battery ends the day as full as it began (the play audit's
-- finding 3, docs/reviews/play-model-audit-2026-11-26.md). A play's preset ends "-v6", with Hard's add-ons before it
-- as in v4 and v5, so the leaderboard ranks version 6 plays only against version 6 plays:
--
--     easy:13.5-5-90-v6
--     hard:13.5-5-90-r25-d0.11-v6
--     hard:13.5-5-90-r25-d0.11-solar-v6
--
-- Presets written before stay valid and keep their own boards: none ("v2 rules"), "-v3", and "-v4" and "-v5" with
-- their add-ons. Constraints only: no column, no table, no grant changes.
--
-- Written in session 11407 and NOT applied by it (a code machine writes no warehouse data): apply it before the v6
-- site is deployed. Until then the database refuses a v6 play, and the page says the play was not stored. The number
-- 040 is the next free one on origin/main on 28 November 2026; the desk renumbers it at landing if another took it.
alter table public.game_scores drop constraint if exists game_scores_preset_check;
alter table public.game_scores add constraint game_scores_preset_check check (preset ~ '^(easy|normal|hard):[0-9.]+-[0-9.]+-[0-9]+(-r[0-9]+-d[0-9.]+)?(-v3|(-[a-z]+)*-v4|(-[a-z]+)*-v5|(-[a-z]+)*-v6)?$');
alter table public.game_plays drop constraint if exists game_plays_preset_check;
alter table public.game_plays add constraint game_plays_preset_check check (preset ~ '^(easy|normal|hard):[0-9.]+-[0-9.]+-[0-9]+(-r[0-9]+-d[0-9.]+)?(-v3|(-[a-z]+)*-v4|(-[a-z]+)*-v5|(-[a-z]+)*-v6)?$');
