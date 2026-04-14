# Requirements — Q3 Infrastructure Upgrade

## Functional Requirements

### FR-01: Server Decommission
All 14 identified end-of-life physical servers must be decommissioned by August 31, 2026 (M4). Each server must have its workloads validated as migrated or terminated before decommission.

### FR-02: Azure Workload Migration
All remaining legacy workloads (approximately 30% of total estate) must be migrated to Azure. Migrated workloads must meet a latency target of <200ms for internal applications.

### FR-03: Storage Consolidation
The existing NetStore storage array must be replaced. The replacement solution must achieve at least 40% reduction in per-TB cost compared to current spend.

### FR-04: Network Switching Upgrade
The network switching layer must be upgraded as part of this project. New switches must support the capacity requirements of the consolidated Azure-hybrid environment.

### FR-05: AD Replication Migration
The Active Directory replication role currently on srv-dc03 must be migrated to a supported platform. Migration plan requires CTO sign-off before execution.

### FR-06: RunBook Documentation
A complete operational RunBook must be authored and handed to the IT Ops team by project close (September 30, 2026). The RunBook must cover all migrated services and the new infrastructure topology.

## Non-Functional Requirements

### NFR-01: Availability
Cutover activities must be completed within pre-approved 4-hour maintenance windows (Sunday nights). Maximum unplanned downtime during migration: 2 hours per incident.

### NFR-02: Performance
Post-migration, internal application latency must not exceed 200ms (P95) as measured from the corporate network.

### NFR-03: Security
All migrated workloads must comply with existing security policies. Azure resources must be deployed within the approved Azure EA subscription with RBAC and tagging standards enforced.

### NFR-04: Stable-Run Period
A 2-week stable-run period (September 15–30) must complete with zero P1 incidents before the project is formally closed.

### NFR-05: Budget Compliance
Total project spend must not exceed $380K. Any forecast overrun must be escalated to the CTO within 5 business days of identification.
