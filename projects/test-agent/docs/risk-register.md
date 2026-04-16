# Risk Register — Test Agent

| Risk | Probability | Impact | Mitigation | Status |
|---|---|---|---|---|
| Learning curve for deploying sub-agents into Microsoft Teams | Medium | Medium | Research Teams bot framework and Azure Bot Service early; prototype before committing to architecture | Open |
| Teams bot registration and Azure service requirements unknown | Medium | Low | Create a research task to identify all dependencies before starting Phase 2 | Open |
| No target dates set for either milestone — schedule baseline does not exist | Medium | Medium | Owner to set Phase 1 and Phase 2 target dates in milestones.md. Until then, PM agent cannot produce schedule-based health ratings. | Open |
| Phase 1 completed work is not reflected in Planner — PM tooling will report false-zero progress on all future automated runs | Medium | Medium | Backfill completed tasks in Planner. After backfill, mark tasks complete so completion rate reflects actual state. | Open |
| config.yaml bucket_ids have not been updated after Run 2 bucket restructure instructions — live Planner bucket structure is unknown and may diverge from config.yaml | High | Medium | Owner to confirm current live bucket state in Planner (via planner buckets list --plan-id WWclzqKzu0y9Abfr3qx4yZcAFNzi) and update config.yaml to match. No new bucket create_task instructions should be issued until the live state is confirmed. | Open |
| Unknown 7th task exists in Planner — created between Run 1 and Run 3 with no documentation in project files | High | Low | Owner to identify the 7th task (via planner tasks list --plan-id WWclzqKzu0y9Abfr3qx4yZcAFNzi) and either: (a) add context to its description, (b) assign it to the correct bucket, or (c) delete it if erroneous. | Open |
| Executor agents lack Bash/Write/Edit permissions — cannot execute CLI commands or update project docs autonomously | Medium | High | Investigate Claude Code subagent permission settings before Run 3. | Open |
