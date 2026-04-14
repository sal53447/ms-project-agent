# Work Breakdown Structure — Q3 Infrastructure Upgrade

## 1. Project Management
- 1.1 Project kickoff and planning
- 1.2 Weekly status reporting
- 1.3 Stakeholder communication
- 1.4 Budget tracking and FinOps reviews
- 1.5 Risk and issue management
- 1.6 Project closure and handover

## 2. Discovery & Assessment (Target: May 15)
- 2.1 Infrastructure inventory audit (all 14 servers)
- 2.2 Legacy application discovery sprint (3 undocumented apps)
- 2.3 Azure compatibility assessment per workload
- 2.4 Storage assessment and vendor EOL impact analysis
- 2.5 Network topology review
- 2.6 Migration plan authoring and CTO sign-off

## 3. Azure Environment Provisioning (Target: June 30)
- 3.1 Azure subscription configuration (EA credits, RBAC, tagging)
- 3.2 Azure vCPU quota increase resolution (ticket #AZ-4421)
- 3.3 Network connectivity — ExpressRoute / VPN validation
- 3.4 SecOps firewall rule review integration (dependency: SecOps, May 30)
- 3.5 Landing zone and resource group structure deployment
- 3.6 Connectivity validation testing

## 4. Server Wave 1 Migration — 8 servers (Target: July 31)
- 4.1 Workload migration for 8 servers
- 4.2 Application testing and sign-off per workload
- 4.3 Storage array decommission (NetStore)
- 4.4 Wave 1 cutover (maintenance window)
- 4.5 Post-migration monitoring (72 hours)

## 5. Server Wave 2 Migration — 6 servers (Target: Aug 31)
- 5.1 srv-dc03 AD replication migration (requires CTO sign-off)
- 5.2 Workload migration for remaining 5 servers
- 5.3 Legacy hardware decommission (all 14 servers)
- 5.4 Network switching layer upgrade
- 5.5 Wave 2 cutover (maintenance window)
- 5.6 Post-migration monitoring (72 hours)

## 6. Stabilisation & Closure (Target: Sept 30)
- 6.1 2-week stable-run period monitoring (Sept 15–30)
- 6.2 RunBook documentation authoring
- 6.3 IT Ops handover and training
- 6.4 Azure cost baseline established
- 6.5 Storage cost reduction validated (≥40% target)
- 6.6 Project closure report
- 6.7 Lessons learned session
