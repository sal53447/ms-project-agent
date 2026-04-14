# Project Definition — Q3 Infrastructure Upgrade

## Overview

Q3 Infrastructure Upgrade is a cross-functional initiative to modernize on-premises server infrastructure and migrate remaining workloads to Azure. The project targets completion by September 30, 2026 (end of Q3).

## Goals

1. Decommission all 14 end-of-life physical servers.
2. Complete migration of the remaining 30% of workloads still running on legacy hardware to Azure or replacement hardware.
3. Consolidate storage infrastructure with a target 40% reduction in per-TB cost.
4. Upgrade the network switching layer.
5. Achieve a 2-week stable-run period with zero P1 incidents before project close.
6. Hand over a complete RunBook to the IT Ops team.

## Success Criteria

- All 14 legacy servers decommissioned by September 30, 2026.
- Azure migration complete with <200ms latency for internal applications.
- Storage consolidation delivers ≥40% reduction in per-TB cost.
- Zero P1 incidents during the 2-week stable-run period (September 15–30).
- RunBook documentation complete and signed off by IT Ops Lead.

## Scope

### In Scope

- Decommission of 14 identified end-of-life physical servers.
- Azure workload migration (final 30% of legacy workloads).
- Storage infrastructure consolidation (replacement of NetStore array).
- Network switching layer upgrade.
- AD replication migration (srv-dc03).
- RunBook documentation.

### Out of Scope

- Network perimeter security refresh (covered by a separate SecOps project).
- End-user device upgrades.
- Application-layer code changes unless directly required for Azure compatibility.
- Any workloads already migrated in prior phases.

## Background

The organization completed two prior phases of cloud migration. This project covers the final legacy hardware cohort. The existing servers are past vendor support dates, creating operational risk. The initiative was approved by the CTO in Q1 2026 with a total budget of $380K.
