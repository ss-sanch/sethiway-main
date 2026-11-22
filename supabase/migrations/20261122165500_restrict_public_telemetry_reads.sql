-- SethiQuant and the traffic logger submit events without returning rows.
-- The SethiStock admin endpoint reads both tables with the service role.
revoke select, update, delete, truncate, references, trigger
    on public.traffic_logs, public.markowitz_telemetry
    from public, anon, authenticated;

drop policy if exists "Allow anonymous reads" on public.traffic_logs;

alter table public.markowitz_telemetry enable row level security;

create policy "Allow telemetry inserts"
    on public.markowitz_telemetry for insert
    to anon, authenticated
    with check (true);
