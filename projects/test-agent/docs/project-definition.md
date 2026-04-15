# Project Definition — Test Agent

## Description

A software design project to build an AI agent system that controls Microsoft Planner for project management, and integrates with Microsoft Teams so users can onboard new projects through natural conversation.

## Goals

1. Build a working CLI + multi-agent system that manages MS Planner projects (create tasks, assess project health, execute PM instructions)
2. Extend the system with a Microsoft Teams bot that allows users to onboard projects through conversation in Teams channels

## Success Criteria

- The agent system can autonomously assess project health, generate instructions, and execute them against MS Planner
- Users can describe a project in a Teams conversation and have it automatically created and set up in Planner

## Scope

### In Scope

- CLI tooling for Planner CRUD operations (plans, tasks, buckets, checklists, attachments)
- Multi-agent system: Orchestrator, PM Agent, Executor agents
- Project onboarding workflow (config.yaml, project documents, Q&A bucket)
- Microsoft Teams bot for project onboarding conversations

### Out of Scope

- Teams integration for status updates, task assignment, or day-to-day task management (onboarding only)
- Mobile app or custom web UI
- Integration with project management tools other than MS Planner
