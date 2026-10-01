-- Energy Research Warehouse (ERW): Supabase, migration 014 (session 50): the home battery game v2.
--
-- game_scores gains preset and difficulty: the leaderboard ranks only plays under the same rules (lib/battery.ts
-- presetOf: the difficulty, the battery's usable kWh, kW and round-trip percent, and on Hard the reserve and the
-- degradation cost). Every row before v2 was played on Normal with the default battery, so the defaults fill them.
-- game_plays gains the same two and the settings (JSON), for the research record. No new table; no personal data.
-- The anon key may insert the new columns and read them on game_scores, as before. Idempotent.

alter table public.game_scores add column if not exists preset text not null default 'normal:13.5-5-90';
alter table public.game_scores add column if not exists difficulty text not null default 'normal';
alter table public.game_plays add column if not exists preset text not null default 'normal:13.5-5-90';
alter table public.game_plays add column if not exists difficulty text not null default 'normal';
alter table public.game_plays add column if not exists settings jsonb;

alter table public.game_scores drop constraint if exists game_scores_preset_check;
alter table public.game_scores add constraint game_scores_preset_check check (preset ~ '^(easy|normal|hard):[0-9.]+-[0-9.]+-[0-9]+(-r[0-9]+-d[0-9.]+)?$');
alter table public.game_scores drop constraint if exists game_scores_difficulty_check;
alter table public.game_scores add constraint game_scores_difficulty_check check (difficulty in ('easy', 'normal', 'hard'));
alter table public.game_plays drop constraint if exists game_plays_preset_check;
alter table public.game_plays add constraint game_plays_preset_check check (preset ~ '^(easy|normal|hard):[0-9.]+-[0-9.]+-[0-9]+(-r[0-9]+-d[0-9.]+)?$');
alter table public.game_plays drop constraint if exists game_plays_difficulty_check;
alter table public.game_plays add constraint game_plays_difficulty_check check (difficulty in ('easy', 'normal', 'hard'));

create index if not exists game_scores_level_preset on public.game_scores (level_date, preset, score desc);

grant insert (preset, difficulty) on public.game_scores to anon;
grant select (preset, difficulty) on public.game_scores to anon;
grant insert (preset, difficulty, settings) on public.game_plays to anon;
