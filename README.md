# Adsomnia "Talk-to-Data" Automation Agent

> An LLM-powered automation agent that enables natural language interaction with Everflow marketing data.

## 🎯 Project Overview

This agent transforms complex Everflow API operations into simple conversational queries. Users can ask questions like *"Which LP is best for Offer X?"* and receive instant, actionable insights.

### Core Capabilities

| Phase | Capability | Workflows |
|-------|------------|-----------|
| **The Analyst** | Read-only data retrieval | WF2 (Top LPs), WF3 (Export Reports) |
| **The Watchdog** | Monitoring & asset creation | WF6 (Summaries), WF1 (Tracking Links) |
| **The Alerter** | Proactive monitoring & alerts | WF4 (Default LP Alert), WF5 (Paused Partner) |

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Chat Interface                        │
│              (Password Protected UI)                     │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│                   LLM Agent Layer                        │
│         (Natural Language → Intent Parsing)              │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│              Workflow Orchestrator                       │
│    ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐     │
│    │ WF1 │ │ WF2 │ │ WF3 │ │ WF4 │ │ WF5 │ │ WF6 │     │
│    └─────┘ └─────┘ └─────┘ └─────┘ └─────┘ └─────┘     │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│              Everflow API Wrapper                        │
│            (Standardized API Client)                     │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
              [Everflow API]
```

## 📁 Project Structure

```
adsomnia/
├── .cursorrules              # AI assistant context
├── README.md                 # This file
├── ARCHITECTURE.md           # Detailed system design
├── docs/
│   ├── workflows/            # Individual workflow specs
│   │   ├── WF1_generate_tracking_links.md
│   │   ├── WF2_top_performing_lps.md
│   │   ├── WF3_export_reports.md
│   │   ├── WF4_default_lp_alert.md
│   │   ├── WF5_paused_partner_check.md
│   │   └── WF6_weekly_summaries.md
│   ├── api/
│   │   └── everflow_api_reference.md
│   └── shared/
│       ├── agent_context.md
│       └── error_handling.md
├── src/                      # Source code (to be created)
├── tests/                    # Test suite (to be created)
└── requirements.txt          # Dependencies (to be created)
```

## 🚀 Quick Start

```bash
# Clone the repository
git clone git@github.com:xkgrowth/adsomnia.git
cd adsomnia

# Set up environment (instructions in ARCHITECTURE.md)
# ...

# Configure environment variables
cp .env.example .env
# Edit .env with your Everflow API key
```

## 🔐 Security

- **Authentication**: Password-protected interface with separate auth layer
- **Data Handling**: Ephemeral processing only - no data storage
- **API Security**: Dedicated Everflow API key, environment-based secrets
- **Approved APIs**: Only Everflow and LLM Provider endpoints

## 📅 Timeline

| Week | Focus | Deliverables |
|------|-------|--------------|
| 1 | Foundation + Read-Only | API Wrapper, WF2, WF3 |
| 2 | Monitoring & Create | WF6, WF1 (with safety checks) |
| 3 | Alerting | WF4, WF5 (scheduled jobs) |
| 4 | UAT & Handoff | Testing, Documentation, Training |

## 📚 Documentation

- **[ARCHITECTURE.md](./ARCHITECTURE.md)** - System design and technical decisions
- **[docs/](./docs/)** - Workflow specifications and reference docs
- **[docs/api/](./docs/api/)** - Everflow API reference

## 🤝 Client

**Adsomnia** - Affiliate Marketing Platform

---

*Built by blablabuild • December 2025*






