# Decision Log — Q3 Infrastructure Upgrade

| ID | Date | Decision | Rationale | Made By | Alternatives Considered |
|----|------|----------|-----------|---------|------------------------|
| DEC-001 | 2026-04-14 | Azure West Europe selected as target region | Data residency requirement; existing Azure footprint already in West Europe | Sarah Chen (CTO) | UK South (rejected: higher latency for primary users); North Europe (rejected: data residency constraint) |
| DEC-002 | 2026-04-14 | Two-wave migration approach selected (8 servers wave 1, 6 servers wave 2) | Reduces blast radius; allows lessons learned from wave 1 to inform wave 2; CRM Migration project can proceed after wave 1 | Priya Nair, Marcus Williams | Big bang single cutover (rejected: too high risk); three-wave approach (rejected: would push completion past Q3) |
| DEC-003 | 2026-04-14 | srv-dc03 AD migration deferred to wave 2 with mandatory CTO sign-off | AD replication is business-critical; requires dedicated planning and elevated governance | Sarah Chen (CTO) | Move srv-dc03 to wave 1 (rejected: insufficient planning time); keep srv-dc03 on legacy hardware (rejected: EOL risk) |
