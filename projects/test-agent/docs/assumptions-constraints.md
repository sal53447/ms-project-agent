# Assumptions & Constraints — Test Agent

## Assumptions

- Azure app registration with required Graph API permissions (Tasks.ReadWrite.All, Group.Read.All, User.Read.All) is available and admin-consented
- Microsoft 365 tenant with Planner enabled
- Python 3.11+ and uv package manager available in the development environment
- Teams bot development will be possible with the current tenant's licensing

## Constraints

- Personal project — single developer, no dedicated budget
- App-only authentication only (no delegated/user sign-in flow)
- Teams integration limited to onboarding conversations (not full task management)
