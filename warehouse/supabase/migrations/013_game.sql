-- Energy Research Warehouse (ERW): Supabase, migration 013 (session 38): the home battery game (/play/battery).
--
-- game_scores: the public leaderboard. Level date (the ERCOT operating day played), an optional nickname, the score
-- and the perfect-foresight score (USD, both recomputed by the server route from the actions and the real prices),
-- and the time. No email, no account, no IP.
-- game_plays: the research record of each finished play, stored and never shown: a random session id, the level date,
-- the actions (1 charge, 0 idle, -1 discharge, one per 15-minute interval) and the score. No IP, no nickname, and no
-- column that joins it to game_scores.
-- check: true for the ERW's own scripted checks (site/scripts), so they can be left out of the leaderboard and the
-- research data.
-- The anon key may insert both and read game_scores; it can never read game_plays, update or delete. Idempotent.

create table if not exists public.game_scores (
  id bigserial primary key,
  level_date date not null,
  nickname text check (nickname is null or nickname ~ '^[A-Za-z0-9]{3,16}$'),
  score numeric(12, 4) not null check (abs(score) < 100000),
  optimal_score numeric(12, 4) not null check (abs(optimal_score) < 100000),
  "check" boolean not null default false,
  ts timestamptz not null default now()
);
create index if not exists game_scores_level on public.game_scores (level_date, score desc);

create table if not exists public.game_plays (
  id bigserial primary key,
  session_id uuid not null,
  level_date date not null,
  actions smallint[] not null check (array_length(actions, 1) between 92 and 100 and actions <@ array[-1, 0, 1]::smallint[]),
  score numeric(12, 4) not null check (abs(score) < 100000),
  "check" boolean not null default false,
  ts timestamptz not null default now()
);

alter table public.game_scores enable row level security;
alter table public.game_plays enable row level security;

drop policy if exists anon_insert on public.game_scores;
create policy anon_insert on public.game_scores for insert to anon with check (true);
drop policy if exists anon_read on public.game_scores;
create policy anon_read on public.game_scores for select to anon using (true);
drop policy if exists anon_insert on public.game_plays;
create policy anon_insert on public.game_plays for insert to anon with check (true);

grant insert (level_date, nickname, score, optimal_score, "check") on public.game_scores to anon;
grant select (id, level_date, nickname, score, optimal_score, "check", ts) on public.game_scores to anon;
grant usage, select on sequence public.game_scores_id_seq to anon;
grant insert (session_id, level_date, actions, score, "check") on public.game_plays to anon;
grant usage, select on sequence public.game_plays_id_seq to anon;
revoke update, delete, truncate on public.game_scores from anon, authenticated;
revoke select, update, delete, truncate on public.game_plays from anon, authenticated;
