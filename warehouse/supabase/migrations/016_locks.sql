-- Energy Research Warehouse (ERW), session 59: the data lock, so several machines (and GitHub's daily job) never write
-- the warehouse at once (docs/machines.md).
--
-- One row per lock name ('data'): who holds it, for what task, since when, until when. A holder renews it while it
-- works; a machine that closes, sleeps or crashes stops renewing, and the lock expires, so nothing can hold it forever.
-- Every function is security definer and callable only with the service key (warehouse/lock.py), never the site's anon
-- key. Idempotent.

create table if not exists public.erw_locks (
  name      text primary key,
  holder    text not null,
  task      text not null,
  token     uuid not null,
  acquired  timestamptz not null default now(),
  renewed   timestamptz not null default now(),
  expires   timestamptz not null
);
alter table public.erw_locks enable row level security;
revoke all on public.erw_locks from anon, authenticated;

-- take the lock if it is free or expired: returns the new token, or null when another holder has it
create or replace function public.erw_lock_acquire(p_name text, p_holder text, p_task text, p_minutes int)
returns uuid language plpgsql security definer set search_path = public as $$
declare t uuid := gen_random_uuid();
begin
  insert into public.erw_locks as l (name, holder, task, token, acquired, renewed, expires)
  values (p_name, p_holder, p_task, t, now(), now(), now() + make_interval(mins => p_minutes))
  on conflict (name) do update set holder = excluded.holder, task = excluded.task, token = excluded.token,
    acquired = excluded.acquired, renewed = excluded.renewed, expires = excluded.expires
  where l.expires < now();
  if exists (select 1 from public.erw_locks where name = p_name and token = t) then
    return t;
  end if;
  return null;
end $$;

-- extend a held lock: true if the token still holds it (not expired, not taken)
create or replace function public.erw_lock_renew(p_name text, p_token uuid, p_minutes int)
returns boolean language plpgsql security definer set search_path = public as $$
begin
  update public.erw_locks set renewed = now(), expires = now() + make_interval(mins => p_minutes)
  where name = p_name and token = p_token and expires >= now();
  return found;
end $$;

-- is the token the current, unexpired holder?
create or replace function public.erw_lock_check(p_name text, p_token uuid)
returns boolean language sql security definer set search_path = public as $$
  select exists (select 1 from public.erw_locks where name = p_name and token = p_token and expires >= now());
$$;

-- give the lock up: true if the token held it
create or replace function public.erw_lock_release(p_name text, p_token uuid)
returns boolean language plpgsql security definer set search_path = public as $$
begin
  delete from public.erw_locks where name = p_name and token = p_token;
  return found;
end $$;

-- who holds it (for status lines and a waiting machine's message)
create or replace function public.erw_lock_status(p_name text)
returns table (holder text, task text, acquired timestamptz, renewed timestamptz, expires timestamptz, expired boolean)
language sql security definer set search_path = public as $$
  select holder, task, acquired, renewed, expires, expires < now() from public.erw_locks where name = p_name;
$$;

revoke all on function public.erw_lock_acquire(text, text, text, int) from public, anon, authenticated;
revoke all on function public.erw_lock_renew(text, uuid, int) from public, anon, authenticated;
revoke all on function public.erw_lock_check(text, uuid) from public, anon, authenticated;
revoke all on function public.erw_lock_release(text, uuid) from public, anon, authenticated;
revoke all on function public.erw_lock_status(text) from public, anon, authenticated;
grant execute on function public.erw_lock_acquire(text, text, text, int) to service_role;
grant execute on function public.erw_lock_renew(text, uuid, int) to service_role;
grant execute on function public.erw_lock_check(text, uuid) to service_role;
grant execute on function public.erw_lock_release(text, uuid) to service_role;
grant execute on function public.erw_lock_status(text) to service_role;
