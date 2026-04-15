# Decision Log — Test Agent

| Date | Decision | Rationale |
|---|---|---|
| 2026-04-15 | Teams integration scoped to onboarding only | Keep Phase 2 focused and achievable; full task management via Teams deferred |
| 2026-04-15 | Two-phase delivery: CLI+Agent first, Teams bot second | Phase 1 provides the foundation that Phase 2 builds on; no point starting the bot before the core works |
| 2026-04-15 | Plan hosted under the "IT" M365 group | Existing group with appropriate access |
| 2026-04-15 | config.yaml has empty agent fields (milestone_bucket, risk_bucket, requirements, decisions_log, stakeholders) | PM Agent assessment noted these are used for automated routing; populate after bucket structure is finalised |
| 2026-04-15 | Bucket strategy: phase-based organisation (Phase 1, Phase 2, Admin, Q&A) instead of workflow states | Planner already tracks task progress natively; buckets used for workflow states (To Do/Doing/Done) are redundant. Phase-based buckets improve readability by grouping related work. |
| 2026-04-15 | Added --bucket-id, --due-date, --start-date to CLI tasks update command | Required for agents to move tasks between buckets and set deadlines. Also fixed ETag prefetch on update. |
