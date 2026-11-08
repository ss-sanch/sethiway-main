# Member accounts preview

The first release adds email accounts, a synced ticker watchlist and member metrics and a member preview in the existing admin dashboard. The member preview uses sample data and stays inside My Workspace. The existing admin page stays at `admin.html`. The public portfolio and separate portfolio editing tools keep their current routes and access controls.

## Before opening registration

1. The member UI lives in the existing SethiWay site. Verify that the configured Supabase project serves the existing site and that `public.traffic_logs` has `visitor_id`, `action` and `created_at`.
2. Configure email confirmation, an email delivery provider, the site URL and the two callback URLs. Allow the deployed `account.html` URL and its `?recovery=1` variant. Test both email journeys on the deployed origin.
3. Apply the migration after reviewing the existing API grants and policies. Deploy the matching SethiStock backend change before the frontend so the current admin page can load diagnostics with the owner session or the existing vault credential. In the SQL editor, insert the verified owner's Auth user ID into `sethiway_members_private.owner_account (user_id)`. This is a single-row table and is only writable by a privileged database operator.
4. Test two independent member accounts, an owner account and a signed-out browser. Confirm that the owner totals exclude the owner, ordinary members cannot access the owner RPC, and switching accounts clears the previous member's saved tickers.
5. Review legacy API grants before opening registration, particularly `markowitz_telemetry`, which currently has row-level security disabled in production. The portfolio editing tools still use the existing vault credential.

Verified members are current confirmed accounts other than the owner. Active members are verified accounts with a signed-in visit on one of the past 30 UTC calendar days. Recorded browsers are distinct IDs in existing page-view logs over a rolling 30-day window. Historical browser IDs do not distinguish members from guests and existing page-view coverage varies by tool.

To roll back the frontend, redeploy the saved pre-accounts ref. Retain the member tables during a frontend rollback so existing member data stays available for a later redeploy.
