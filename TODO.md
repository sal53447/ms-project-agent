# TODO

## Task Lifecycle: Human Updates in Planner

**Problem:** When a human marks a task as done (or changes progress) directly in Planner, what happens next? Currently nothing — no agent picks up on it. The PM Agent reads Planner state but only on manual runs. There's no reactive loop.

**Questions to answer:**
- Who detects that a task status changed? (Orchestrator on next run? A webhook? A scheduled poll?)
- When the PM Agent sees completed tasks, does it update milestones.md, close related risks, or trigger follow-up tasks?
- If a human marks a task as "in progress" (50%), does that change how the PM Agent prioritises?
- What about tasks the PM Agent created — if a human rejects or modifies them, how does the system reconcile?
- Is the current "run the orchestrator manually" model sufficient, or do we need event-driven triggers?

**Action:** Review the Orchestrator, PM Agent, and Executor specs to see if this lifecycle is covered. If not, design the feedback loop between human Planner activity and the agent system.
