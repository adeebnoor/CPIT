# 4.5.6 — use configured alternatives consistently

The 4.5.5 live test ended with a quota rejection. Inspection showed that the
3.5-specific source/audit routes tried only 3.5 Flash and Flash Lite, although
the application's automatic route already included 3.6 Flash.

All stages can now reach that existing configured alternative after their
preferred model. Exhausted models are remembered for the current job and not
requested again by subsequent stages. A mixed quota/capacity failure is no
longer misreported as every model having exhausted quota.

This does not provision quota, change billing, add credentials/accounts, or
override provider limits. Availability must be established by a real provider
response. Lecture release still requires all content/role/readability checks
and a separate semantic audit.
