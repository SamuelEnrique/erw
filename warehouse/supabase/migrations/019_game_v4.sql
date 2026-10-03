-- Energy Research Warehouse (ERW), session 66.
--
-- Battery game v4 (site/lib/battery.ts, RULES_VERSION): a play's preset ends "-v4", and on Hard it names the add-ons
-- that were on just before the version, each a word of lowercase letters (the first: "solar", the rooftop array), so
-- the leaderboard ranks version 4 plays only against version 4 plays with the same rules and add-ons:
--
--     normal:13.5-5-90-v4
--     hard:13.5-5-90-r20-d0.11-v4
--     hard:13.5-5-90-r20-d0.11-solar-v4
--
-- Presets written before stay valid and keep their own boards: no version ("v2 rules") and "-v3" ("v3 rules"), neither
-- with add-ons. The server writes only presets lib/battery.ts's presetOf builds and reads only those parsePreset
-- accepts; this check is the database's own floor under it. Constraints only: no column, no table, no grant changes.
--
-- Written in session 66 and NOT applied by it: apply it at the finish step, before the v4 site is deployed (until then
-- the database refuses a v4 play, and the page says the play was not stored).
alter table public.game_scores drop constraint if exists game_scores_preset_check;
alter table public.game_scores add constraint game_scores_preset_check check (preset ~ '^(easy|normal|hard):[0-9.]+-[0-9.]+-[0-9]+(-r[0-9]+-d[0-9.]+)?(-v3|(-[a-z]+)*-v4)?$');
alter table public.game_plays drop constraint if exists game_plays_preset_check;
alter table public.game_plays add constraint game_plays_preset_check check (preset ~ '^(easy|normal|hard):[0-9.]+-[0-9.]+-[0-9]+(-r[0-9]+-d[0-9.]+)?(-v3|(-[a-z]+)*-v4)?$');
