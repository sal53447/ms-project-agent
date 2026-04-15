# Requirements — Test Agent

## Functional Requirements

### Phase 1 — CLI + Agent System

- FR-1: CLI must support full CRUD for plans, buckets, tasks, checklists, and attachments via MS Graph API
- FR-2: Multi-agent system with three roles: Orchestrator (coordination), PM Agent (assessment + instructions), Executor (single-instruction execution)
- FR-3: Project onboarding workflow that creates config.yaml, project documents, and validates Planner connection
- FR-4: Q&A bucket in Planner for human-agent communication

### Phase 2 — Teams Bot

- FR-5: Teams bot that accepts natural language project descriptions
- FR-6: Bot triggers the onboarding workflow to create a project in Planner from the conversation
- FR-7: Bot confirms project creation back to the user in the Teams channel

## Non-Functional Requirements

- NFR-1: App-only (client credentials) authentication — no user sign-in required for backend operations
- NFR-2: Handle Graph API throttling (429) and ETag conflicts (409/412) with retry logic
- NFR-3: All service methods async for future scalability

> Phase 2 requirements are preliminary and will be refined after dependency research.
