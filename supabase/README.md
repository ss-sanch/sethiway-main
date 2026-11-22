# SethiWay member beta

The beta uses Supabase email authentication and stores watchlists, workspace preferences and paper portfolios per account. Member watchlist quotes use SethiStock's cached public snapshots. Macro topics link to the relevant SethiMacro pages. The paper portfolio still uses labelled illustrative prices, FX and benchmark returns. The owner-only member preview is separate from real saved member records.

## Deploy the beta

1. Review changes in both repositories' `account-workspace-beta` branches. The frontend expects the member-account migration and the owner-session telemetry endpoint. Keep a record of both deployed revisions before rollout.
2. Configure the official SethiWay origin and the account and recovery redirect URLs in Supabase Auth. Keep public registration disabled in Auth for the private beta. Provision the owner and test member by invitation when the site and email delivery are ready.
3. Review the existing grants on `traffic_logs` and `markowitz_telemetry` before rollout. The optimiser currently writes telemetry directly from the browser. Preserve that write path when restricting reads, or migrate ingestion to the backend before removing its write permissions.
4. Apply the member accounts migration. Assign the confirmed owner's Auth user ID to the single row in `sethiway_members_private.owner_account` through the database admin path. Deploy the SethiStock backend, then the frontend. The existing telemetry login continues to accept its legacy credential during rollout.
5. Confirm the invite and password-reset links on the official origin. Verify a member can save stocks and settings, see them in a second browser, and cannot access Admin or another account's rows. Verify the owner can open member metrics and diagnostics. Confirm the public hub and guest stock tools still work.
6. If a frontend rollback is needed, redeploy the saved pre-beta frontend. Retain the account tables so saved data survives the rollback.

Verified members are confirmed non-anonymous accounts excluding the owner. Active members are verified accounts with a signed-in visit on one of the past 30 UTC calendar days. Recorded browsers are distinct IDs in page-view logs and include signed-out visits.
