begin;

create schema sethiway_members_private;
revoke all on schema sethiway_members_private from public, anon, authenticated;
grant usage on schema sethiway_members_private to authenticated;

-- A single owner is provisioned out of band by Auth user ID.
create table sethiway_members_private.owner_account (
    singleton boolean primary key default true check (singleton),
    user_id uuid not null unique references auth.users(id) on delete cascade
);
alter table sethiway_members_private.owner_account enable row level security;

create table public.sethiway_member_watchlist (
    user_id uuid not null default auth.uid() references auth.users(id) on delete cascade,
    ticker text not null check (ticker ~ '^[A-Z0-9.^=-]{1,20}$'),
    created_at timestamptz not null default now(),
    primary key (user_id, ticker)
);
alter table public.sethiway_member_watchlist enable row level security;
revoke all on public.sethiway_member_watchlist from public, anon, authenticated;
grant select, delete on public.sethiway_member_watchlist to authenticated;
grant insert (ticker) on public.sethiway_member_watchlist to authenticated;
create policy watchlist_read on public.sethiway_member_watchlist for select to authenticated
    using (user_id = (select auth.uid()) and (select auth.jwt() ->> 'is_anonymous') = 'false');
create policy watchlist_add on public.sethiway_member_watchlist for insert to authenticated
    with check (user_id = (select auth.uid()) and (select auth.jwt() ->> 'is_anonymous') = 'false');
create policy watchlist_remove on public.sethiway_member_watchlist for delete to authenticated
    using (user_id = (select auth.uid()) and (select auth.jwt() ->> 'is_anonymous') = 'false');

create table public.sethiway_member_activity (
    user_id uuid not null default auth.uid() references auth.users(id) on delete cascade,
    activity_day date not null default (now() at time zone 'UTC')::date,
    primary key (user_id, activity_day)
);
create index sethiway_member_activity_day_idx on public.sethiway_member_activity(activity_day);
alter table public.sethiway_member_activity enable row level security;
revoke all on public.sethiway_member_activity from public, anon, authenticated;
grant insert on public.sethiway_member_activity to authenticated;
create policy record_own_activity on public.sethiway_member_activity for insert to authenticated
    with check (
        user_id = (select auth.uid())
        and (select auth.jwt() ->> 'is_anonymous') = 'false'
        and activity_day = (now() at time zone 'UTC')::date
    );

create function public.sethiway_record_member_activity()
returns void language sql security invoker set search_path = '' as $$
    insert into public.sethiway_member_activity default values on conflict do nothing;
$$;

-- The privileged functions live outside the exposed API schema. Every call
-- checks the current owner identity and that the Auth session still exists.
create function sethiway_members_private.is_owner()
returns boolean language sql stable security definer set search_path = '' as $$
    select exists (
        select 1
        from sethiway_members_private.owner_account as owner
        join auth.sessions as session on session.user_id = owner.user_id
        join auth.users as account on account.id = owner.user_id
        where owner.user_id = (select auth.uid())
          and session.id::text = (select auth.jwt() ->> 'session_id')
          and account.email_confirmed_at is not null
          and coalesce(account.is_anonymous, false) = false
    );
$$;

create function sethiway_members_private.owner_metrics()
returns jsonb language plpgsql stable security definer set search_path = '' as $$
begin
    if not sethiway_members_private.is_owner() then
        raise exception 'Owner access required' using errcode = '42501';
    end if;
    return (
        with members as (
            select account.id
            from auth.users as account
            where account.email_confirmed_at is not null
              and coalesce(account.is_anonymous, false) = false
              and not exists (
                  select 1 from sethiway_members_private.owner_account owner where owner.user_id = account.id
              )
        )
        select jsonb_build_object(
            'verified_members', (select count(*) from members),
            'active_members', (
                select count(distinct activity.user_id)
                from public.sethiway_member_activity activity join members on members.id = activity.user_id
                where activity.activity_day >= (now() at time zone 'UTC')::date - 29
            ),
            'recorded_browsers', (
                select count(distinct nullif(visitor_id, ''))
                from public.traffic_logs
                where action = 'page_view' and created_at >= now() - interval '30 days'
            )
        )
    );
end;
$$;

create function public.sethiway_is_owner()
returns boolean language sql stable security invoker set search_path = '' as $$
    select sethiway_members_private.is_owner();
$$;

create function public.sethiway_owner_metrics()
returns jsonb language sql stable security invoker set search_path = '' as $$
    select sethiway_members_private.owner_metrics();
$$;

revoke all on function sethiway_members_private.is_owner(), sethiway_members_private.owner_metrics(),
    public.sethiway_record_member_activity(), public.sethiway_is_owner(), public.sethiway_owner_metrics()
    from public, anon, authenticated;
grant execute on function sethiway_members_private.is_owner(), sethiway_members_private.owner_metrics(),
    public.sethiway_record_member_activity(), public.sethiway_is_owner(), public.sethiway_owner_metrics()
    to authenticated;

commit;
