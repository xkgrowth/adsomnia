# Adsomnia Execution Agents

This folder contains specialized agent definitions for the Talk-to-Data project. Each agent has a specific domain of expertise and knows when to defer to other agents.

## Agent Roster

| Agent | File | Primary Domain |
|-------|------|----------------|
| 📋 **Project Coordinator** | `project-coordinator.md` | Timeline, sprints, client sync |
| 🧠 **LLM Agent Architect** | `llm-agent-architect.md` | Intent, NLU, prompts, conversations |
| 🔌 **Everflow Integration Lead** | `everflow-integration-lead.md` | API wrapper, payloads, data |
| ⚙️ **Backend Engineer** | `backend-engineer.md` | FastAPI, workflows, business logic |
| 💬 **Chat Interface Developer** | `chat-interface-developer.md` | UI, auth, all user interactions |
| ⏰ **Scheduler & Alerts** | `scheduler-alerts-specialist.md` | Cron jobs, WF4, WF5, notifications |
| ✅ **QA & UAT Coordinator** | `qa-uat-coordinator.md` | Testing, validation, handover |

## How to Invoke Agents

Reference agents in your prompts using `@agent-name`:

```
@backend-engineer implement the WF2 workflow following the spec in agents/workflows/WF2_top_performing_lps.md
```

```
@everflow-integration-lead what's the correct payload format for the reporting entity endpoint?
```

```
@project-coordinator update sprint planning - WF2 is complete
```

## Agent Activation by Week

| Week | Primary Agents | Focus |
|------|---------------|-------|
| **Week 1** | `@backend-engineer`, `@everflow-integration-lead`, `@chat-interface-developer` | Foundation, WF2, WF3 |
| **Week 2** | `@llm-agent-architect`, `@backend-engineer`, `@everflow-integration-lead` | WF6, WF1 |
| **Week 3** | `@scheduler-alerts-specialist`, `@backend-engineer` | WF4, WF5 |
| **Week 4** | `@qa-uat-coordinator`, `@project-coordinator` | UAT, Handoff |

## Agent Chaining Rules

Agents should defer to specialists:

- **API payload questions** → `@everflow-integration-lead`
- **LLM/prompt questions** → `@llm-agent-architect`
- **UI/frontend questions** → `@chat-interface-developer`
- **Scheduled job questions** → `@scheduler-alerts-specialist`
- **Testing/UAT questions** → `@qa-uat-coordinator`
- **Timeline/scope questions** → `@project-coordinator`
- **Python architecture** → `@backend-engineer`

## Key Cross-References

Each agent should reference these shared documents:

- `ARCHITECTURE.md` - System design
- `agents/workflows/WF*.md` - Workflow specifications
- `agents/api/everflow_api_reference.md` - API documentation
- `agents/shared/agent_context.md` - Agent behavior patterns
- `agents/shared/error_handling.md` - Error patterns

