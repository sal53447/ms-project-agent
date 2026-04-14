# Risk Register — Q3 Infrastructure Upgrade

| ID | Risk | Probability | Impact | Score | Owner | Mitigation | Status |
|----|------|-------------|--------|-------|-------|------------|--------|
| R1 | Azure budget overrun — cloud cost estimates could be off by ~30% | Medium | High | High | Lisa Tanaka (FinOps) | Weekly cost review with FinOps; $20K contingency reserve held; Azure Cost Management alerts set at 80% of monthly budget | Open |
| R2 | Legacy app compatibility — 3 undocumented applications may not work on new OS or Azure | Medium | High | High | Priya Nair (Lead Architect) | Discovery sprint planned for May; app owners identified and engaged; rollback plan per app | Open |
| R3 | Key personnel availability — Lead Architect (Priya Nair) allocated to 2 other concurrent projects | Medium | Medium | Medium | Marcus Williams (PM) | Escalation path defined with CTO; backup architect identified; weekly capacity check in status meeting | Open |
| R4 | Supply chain delays for physical hardware (switches and storage array) | Low | High | Medium | Tomasz Kowalski (Network Eng) | PO already raised; 6-week buffer built into schedule; alternative vendor identified if primary delays | Open |
| R5 | NetStore storage array EOL announcement — vendor may withdraw support before migration completes | Medium | Medium | Medium | Anita Patel (IT Ops) | Confirmed support extension request submitted; decommission accelerated in wave 1 if needed | Open |
| R6 | Maintenance window business impact — 4-hour Sunday cutover windows may face resistance | Low | Medium | Low | Marcus Williams (PM) | Pre-approved by CTO; communication plan to department heads 2 weeks in advance | Open |

## Risk Matrix

```
Impact  │ High  │  R2, R1   │  R4       │           │
        │ Med   │  R3       │  R5       │           │
        │ Low   │           │  R6       │           │
        └───────┴──────────────────────────────────
                  Low         Med         High
                              Probability
```
