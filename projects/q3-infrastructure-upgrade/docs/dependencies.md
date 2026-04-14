# Dependencies — Q3 Infrastructure Upgrade

## Inbound Dependencies (things this project depends on)

| ID | Dependency | Source | Required By | Status | Owner |
|----|-----------|--------|-------------|--------|-------|
| D1 | SecOps firewall rule review complete — required before Azure connectivity can be opened | SecOps Project | 2026-05-30 | Pending | Tomasz Kowalski (tracking) |
| D2 | Hardware PO processed by Procurement | Procurement team | 2026-04-30 | In Progress | Marcus Williams |
| D3 | Azure vCPU quota increase approved (ticket #AZ-4421) | Microsoft Azure | 2026-04-28 | In Progress | David Park |
| D4 | CTO sign-off on srv-dc03 AD migration plan | CTO (James Okafor) | Before wave 2 cutover (Aug 2026) | Not started | Priya Nair |
| D5 | NetStore vendor response on support extension | NetStore vendor | 2026-04-28 | In Progress | Anita Patel |

## Outbound Dependencies (projects waiting on this project)

| ID | Project | Waiting For | Expected Date |
|----|---------|-------------|---------------|
| D6 | CRM Migration Project | Wave 1 migration complete (server hosting CRM DB migrated) | 2026-07-31 (M3) |
| D7 | DR/Backup Strategy Project | Final Azure topology confirmed | 2026-06-30 (M2) |
