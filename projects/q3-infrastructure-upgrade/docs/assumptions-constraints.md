# Assumptions & Constraints — Q3 Infrastructure Upgrade

## Assumptions

| ID | Assumption | Owner | Review Date |
|----|-----------|-------|-------------|
| A1 | Azure EA credits of $150K are available and approved for this project | Lisa Tanaka | 2026-04-30 |
| A2 | Business will accept two 4-hour maintenance windows on Sunday nights for cutover activities | Marcus Williams | 2026-05-15 |
| A3 | All legacy application vendors will provide Azure-compatible licenses at no additional cost | Priya Nair | 2026-05-31 |
| A4 | IT Ops team will be available for the 2-week stable-run period (Sept 15–30) without major competing workload | Anita Patel | 2026-09-01 |
| A5 | SecOps will complete firewall rule review by May 30, 2026, unblocking Azure connectivity setup | Marcus Williams | 2026-05-30 |
| A6 | Azure vCPU quota increase (ticket #AZ-4421) will be approved by April 28, 2026 | David Park | 2026-04-28 |
| A7 | Procurement will process the hardware PO by April 30, 2026, with hardware delivered within 6 weeks | Tomasz Kowalski | 2026-05-15 |

## Constraints

| ID | Constraint | Impact |
|----|-----------|--------|
| C1 | Total budget is fixed at $380K — no budget uplift available | All scope changes must be evaluated for cost impact; any overrun >$20K requires CTO approval |
| C2 | Project must complete by September 30, 2026 | No schedule extension available; this aligns with the corporate Q3 fiscal close |
| C3 | Cutover windows limited to Sunday nights (4-hour window) | Wave migrations must be planned to complete within a single maintenance window per wave |
| C4 | Azure resources must be deployed in West Europe region (data residency requirement) | vCPU quota constraint (I3) must be resolved before provisioning |
| C5 | srv-dc03 AD migration requires explicit CTO sign-off before execution | Adds sign-off lead time to wave 2 planning; must be initiated by July 15 at the latest |
