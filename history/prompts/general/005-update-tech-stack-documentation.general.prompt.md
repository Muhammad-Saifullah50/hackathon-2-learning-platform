---
id: 005
title: Update Tech Stack Documentation
stage: general
date: 2026-03-14
surface: agent
model: claude-sonnet-4.5
feature: none
branch: master
user: saifullah
command: none
labels: ["documentation", "tech-stack", "constitution", "agents-md"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - .specify/memory/constitution.md
 - AGENTS.md
tests:
 - none
---

## Prompt

this is the tech stack
## **Technology Summary**

| Layer | Technology | Purpose |
| ----- | ----- | ----- |
| AI Coding Agents | Claude Code, Goose(Claude Code Router) | Execute your Skills to build the application |
| Frontend | Next.js \+ Monaco | User interface with embedded code editor |
| Backend | FastAPI \+ OpenAI SDK | AI-powered tutoring agents as microservices |
| Auth | Better Auth | Authentication framework |
| Service Mesh | Dapr | State management, pub/sub, service invocation |
| Messaging | Kafka on Kubernetes | Asynchronous event-driven communication |
| Database | Neon PostgreSQL | User data, progress, code submissions |
| API Gateway | Kong API Gateway on Kubernetes | Routes traffic and handles JWT authentication |
| AI Context | MCP Servers | Give AI agents real-time access to data |
| Orchestration | Kubernetes | Deploy and manage all containerized services |
| Continuous Delivery | Argo CD \+ GitHub Actions | Argo CD is tool for Continuous Delivery (CD) on Kubernetes using the GitOps approach, and it works exceptionally well with Helm and GitHub Actions |
| Documentation | Docusaurus | Auto-generated documentation site |

update it where necessary in tthe constituiton, claude.md and agents.md only and only if necessary

## Response snapshot

Updated tech stack documentation in constitution.md and AGENTS.md to reflect the complete technology stack including:
- Service Mesh (Dapr)
- Messaging (Kafka on Kubernetes)
- API Gateway (Kong on Kubernetes)
- AI Context (MCP Servers)
- Orchestration (Kubernetes)
- Continuous Delivery (Argo CD + GitHub Actions)
- Documentation (Docusaurus)
- AI Coding Agents (Claude Code, Goose)

CLAUDE.md was not updated as it focuses on development workflow and agent instructions rather than tech stack details.

## Outcome

- ✅ Impact: Tech stack documentation now accurately reflects the full architecture including service mesh, messaging, orchestration, and CI/CD tooling
- 🧪 Tests: No tests required (documentation update)
- 📁 Files: Updated 2 files (constitution.md, AGENTS.md)
- 🔁 Next prompts: Consider creating ADR for tech stack decisions if not already documented
- 🧠 Reflection: Documentation now provides complete visibility into the platform's infrastructure and tooling choices

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A (documentation update)
- Prompt variant (if applicable): none
- Next experiment (smallest change to try): Validate that all mentioned technologies have corresponding setup documentation or skills
