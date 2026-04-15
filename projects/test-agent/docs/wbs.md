# Work Breakdown Structure — Test Agent

## Phase 1: CLI + Agent System

- 1.1 Core Infrastructure
  - 1.1.1 Auth module (MSAL client credentials)
  - 1.1.2 GraphClient (async HTTP, ETag, retry)
  - 1.1.3 Pydantic models (Plan, Task, Bucket, Assignment)
  - 1.1.4 Configuration (pydantic-settings, .env)
  - 1.1.5 Exception hierarchy

- 1.2 Services
  - 1.2.1 PlanService (CRUD)
  - 1.2.2 TaskService (CRUD + details, checklists, attachments)
  - 1.2.3 BucketService (CRUD)

- 1.3 CLI
  - 1.3.1 Plans commands
  - 1.3.2 Tasks commands (including checklist and attach)
  - 1.3.3 Buckets commands
  - 1.3.4 Groups commands
  - 1.3.5 Error handling wrapper

- 1.4 Agent System
  - 1.4.1 PM Agent specification + implementation
  - 1.4.2 Executor Agent specification + implementation
  - 1.4.3 Orchestrator specification + implementation
  - 1.4.4 Project onboarding skill

## Phase 2: Teams Bot Integration

- 2.1 Research
  - 2.1.1 Investigate Teams bot framework and Azure Bot Service requirements
  - 2.1.2 Identify required Azure services and permissions

- 2.2 Bot Development
  - 2.2.1 Teams bot registration and setup
  - 2.2.2 Conversational onboarding flow
  - 2.2.3 Integration with existing onboarding skill
