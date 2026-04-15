# Risk Register — Test Agent

| Risk | Probability | Impact | Mitigation | Status |
|---|---|---|---|---|
| Learning curve for deploying sub-agents into Microsoft Teams | Medium | Medium | Research Teams bot framework and Azure Bot Service early; prototype before committing to architecture | Open |
| Teams bot registration and Azure service requirements unknown | Medium | Low | Create a research task to identify all dependencies before starting Phase 2 | Open |
| No target dates set for either milestone — schedule baseline does not exist | Medium | Medium | Owner to set Phase 1 and Phase 2 target dates in milestones.md. Until then, PM agent cannot produce schedule-based health ratings. | Open |
| Phase 1 completed work is not reflected in Planner — PM tooling will report false-zero progress on all future automated runs | Medium | Medium | Backfill completed tasks in Planner. After backfill, mark tasks complete so completion rate reflects actual state. | Open |
| Executor agents lack Bash/Write/Edit permissions — cannot execute CLI commands or update project docs autonomously | Medium | High | Investigate Claude Code subagent permission settings before Run 3. | Open |
