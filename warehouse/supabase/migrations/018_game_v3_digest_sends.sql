-- Energy Research Warehouse (ERW), session 63.
--
-- 1. Battery game v3 (site/lib/battery.ts, RULES_VERSION): a play's preset carries "-v3" at its end, so the leaderboard
--    ranks version 3 plays (the $5 start, Hard's grid emergency) only against version 3 plays. Presets written before
--    stay valid and keep their own boards ("v2 rules").
alter table public.game_scores drop constraint if exists game_scores_preset_check;
alter table public.game_scores add constraint game_scores_preset_check check (preset ~ '^(easy|normal|hard):[0-9.]+-[0-9.]+-[0-9]+(-r[0-9]+-d[0-9.]+)?(-v3)?$');
alter table public.game_plays drop constraint if exists game_plays_preset_check;
alter table public.game_plays add constraint game_plays_preset_check check (preset ~ '^(easy|normal|hard):[0-9.]+-[0-9.]+-[0-9]+(-r[0-9]+-d[0-9.]+)?(-v3)?$');

-- 2. The digest guard (warehouse/news/email_digest.py): one row per email issue sent. Before the first message goes
--    out the sender claims (kind, day) and (kind, issue) by inserting the row; a second send the same day, or of the
--    same issue, finds the row and is skipped, a manual dispatch included. A claim whose send failed before any
--    message went out is deleted, so a retry can send; once one message has gone out the claim stays.
--    day: the UTC date of the send (for the Roundup, three hours earlier, so a retry before 03:00 UTC on Monday counts
--    as Sunday's). Service key only: row-level security on, no policy, nothing granted to anon or authenticated.
create table if not exists public.digest_sends (
  id bigserial primary key,
  kind text not null check (kind in ('daily', 'roundup')),
  day date not null,
  issue text not null,
  status text not null default 'claimed' check (status in ('claimed', 'sent', 'partial')),
  claimed_at timestamptz not null default now(),
  sent_at timestamptz,
  recipients integer,
  run_id text,
  unique (kind, day),
  unique (kind, issue)
);
alter table public.digest_sends enable row level security;
revoke all on public.digest_sends from anon, authenticated;
revoke all on sequence public.digest_sends_id_seq from anon, authenticated;
