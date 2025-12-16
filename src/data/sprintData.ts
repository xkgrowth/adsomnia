/**
 * Sprint Planning Data for Adsomnia "Talk-to-Data" Automation Agent
 * 
 * This file contains all sprint data and user stories.
 * Update this file as the project progresses to reflect current status.
 * 
 * Status values: 'open' | 'in-progress' | 'blocked' | 'done'
 */

export type UserStoryStatus = 'open' | 'in-progress' | 'blocked' | 'done';

export interface UserStory {
  id: string;
  title: string;
  status: UserStoryStatus;
  workflow?: string;
  assignee?: string;
  priority?: 'critical' | 'high' | 'medium' | 'low';
}

export interface Epic {
  id: string;
  title: string;
  description?: string;
  phase: string;
  userStories: UserStory[];
}

export interface Sprint {
  number: number;
  name: string;
  theme: string;
  focus: string;
  startDate: string;
  endDate: string;
  epics: Epic[];
}

export interface ProjectMeta {
  name: string;
  client: string;
  startDate: string;
  targetEndDate: string;
  sprintDurationDays: number;
}

// Project metadata
export const projectMeta: ProjectMeta = {
  name: "Adsomnia Talk-to-Data Agent",
  client: "Adsomnia",
  startDate: "2025-12-16",
  targetEndDate: "2026-01-12",
  sprintDurationDays: 7,
};

// Sprint configuration
export const sprints: Sprint[] = [
  {
    number: 1,
    name: "Foundation & Read-Only",
    theme: "The Analyst",
    focus: "API integration, data retrieval capabilities",
    startDate: "2025-12-16",
    endDate: "2025-12-22",
    epics: [
      {
        id: "1.1",
        title: "Core Infrastructure",
        phase: "Foundation",
        description: "Set up the foundational architecture and API client",
        userStories: [
          {
            id: "US-1.1.1",
            title: "Set up Next.js + FastAPI project structure",
            status: "in-progress",
            priority: "critical",
          },
          {
            id: "US-1.1.2",
            title: "Implement Everflow API wrapper client",
            status: "open",
            priority: "critical",
          },
          {
            id: "US-1.1.3",
            title: "Configure environment variables and secrets management",
            status: "open",
            priority: "high",
          },
          {
            id: "US-1.1.4",
            title: "Set up authentication layer for chat interface",
            status: "open",
            priority: "high",
          },
        ],
      },
      {
        id: "1.2",
        title: "WF2: Top-Performing Landing Pages",
        phase: "The Analyst",
        description: "Identify best converting LPs for offers/geos",
        userStories: [
          {
            id: "US-1.2.1",
            title: "Implement entity report API integration",
            status: "open",
            workflow: "WF2",
            priority: "critical",
          },
          {
            id: "US-1.2.2",
            title: "Build LP performance calculation logic",
            status: "open",
            workflow: "WF2",
            priority: "high",
          },
          {
            id: "US-1.2.3",
            title: "Create natural language response templates",
            status: "open",
            workflow: "WF2",
            priority: "medium",
          },
          {
            id: "US-1.2.4",
            title: "Handle edge cases: insufficient data, no results",
            status: "open",
            workflow: "WF2",
            priority: "medium",
          },
        ],
      },
      {
        id: "1.3",
        title: "WF3: Export Reports",
        phase: "The Analyst",
        description: "CSV export for fraud, scrub, and general stats",
        userStories: [
          {
            id: "US-1.3.1",
            title: "Implement report export API endpoints",
            status: "open",
            workflow: "WF3",
            priority: "critical",
          },
          {
            id: "US-1.3.2",
            title: "Build natural language date parsing",
            status: "open",
            workflow: "WF3",
            priority: "high",
          },
          {
            id: "US-1.3.3",
            title: "Create download link handling in UI",
            status: "open",
            workflow: "WF3",
            priority: "high",
          },
          {
            id: "US-1.3.4",
            title: "Support multiple report types (fraud, scrub, variance)",
            status: "open",
            workflow: "WF3",
            priority: "medium",
          },
        ],
      },
    ],
  },
  {
    number: 2,
    name: "Monitoring & Create",
    theme: "The Watchdog",
    focus: "Performance monitoring, asset creation with safety checks",
    startDate: "2025-12-23",
    endDate: "2025-12-29",
    epics: [
      {
        id: "2.1",
        title: "WF6: Weekly Performance Summaries",
        phase: "The Watchdog",
        description: "High-level snapshots filtered by Advertiser_Internal",
        userStories: [
          {
            id: "US-2.1.1",
            title: "Implement aggregation by geo/offer",
            status: "open",
            workflow: "WF6",
            priority: "high",
          },
          {
            id: "US-2.1.2",
            title: "Build text summary generator with insights",
            status: "open",
            workflow: "WF6",
            priority: "high",
          },
          {
            id: "US-2.1.3",
            title: "Add Advertiser_Internal label filter",
            status: "open",
            workflow: "WF6",
            priority: "critical",
          },
          {
            id: "US-2.1.4",
            title: "Create week-over-week comparison feature",
            status: "open",
            workflow: "WF6",
            priority: "medium",
          },
        ],
      },
      {
        id: "2.2",
        title: "WF1: Generate Tracking Links",
        phase: "The Watchdog",
        description: "Create tracking links with mandatory safety confirmations",
        userStories: [
          {
            id: "US-2.2.1",
            title: "Implement offer visibility check API",
            status: "open",
            workflow: "WF1",
            priority: "critical",
          },
          {
            id: "US-2.2.2",
            title: "Build user confirmation dialog for approvals",
            status: "open",
            workflow: "WF1",
            priority: "critical",
          },
          {
            id: "US-2.2.3",
            title: "Implement tracking link generation endpoint",
            status: "open",
            workflow: "WF1",
            priority: "high",
          },
          {
            id: "US-2.2.4",
            title: "Add audit logging for all write operations",
            status: "open",
            workflow: "WF1",
            priority: "high",
          },
          {
            id: "US-2.2.5",
            title: "Handle edge cases: blocked partners, invalid IDs",
            status: "open",
            workflow: "WF1",
            priority: "medium",
          },
        ],
      },
      {
        id: "2.3",
        title: "LLM Agent Enhancement",
        phase: "Core",
        description: "Improve intent classification and entity extraction",
        userStories: [
          {
            id: "US-2.3.1",
            title: "Implement intent classification for all workflows",
            status: "open",
            priority: "critical",
          },
          {
            id: "US-2.3.2",
            title: "Build entity extraction (offer_id, affiliate_id, dates)",
            status: "open",
            priority: "high",
          },
          {
            id: "US-2.3.3",
            title: "Add context-aware response generation",
            status: "open",
            priority: "medium",
          },
        ],
      },
    ],
  },
  {
    number: 3,
    name: "Alerting & Automation",
    theme: "The Alerter",
    focus: "Scheduled monitoring and proactive notifications",
    startDate: "2025-12-30",
    endDate: "2026-01-05",
    epics: [
      {
        id: "3.1",
        title: "WF4: Default LP Alert",
        phase: "The Alerter",
        description: "Daily check for traffic to default landing pages",
        userStories: [
          {
            id: "US-3.1.1",
            title: "Set up APScheduler for daily job execution",
            status: "open",
            workflow: "WF4",
            priority: "critical",
          },
          {
            id: "US-3.1.2",
            title: "Implement Default LP detection logic",
            status: "open",
            workflow: "WF4",
            priority: "high",
          },
          {
            id: "US-3.1.3",
            title: "Build in-app notification system for alerts",
            status: "open",
            workflow: "WF4",
            priority: "high",
          },
          {
            id: "US-3.1.4",
            title: "Add configurable thresholds (click count)",
            status: "open",
            workflow: "WF4",
            priority: "medium",
          },
        ],
      },
      {
        id: "3.2",
        title: "WF5: Paused Partner Check",
        phase: "The Alerter",
        description: "Week-over-week comparison for volume drops",
        userStories: [
          {
            id: "US-3.2.1",
            title: "Implement period comparison logic",
            status: "open",
            workflow: "WF5",
            priority: "critical",
          },
          {
            id: "US-3.2.2",
            title: "Build delta calculation and threshold filtering",
            status: "open",
            workflow: "WF5",
            priority: "high",
          },
          {
            id: "US-3.2.3",
            title: "Create aggregated alert messages",
            status: "open",
            workflow: "WF5",
            priority: "high",
          },
          {
            id: "US-3.2.4",
            title: "Add exclusion lists for known seasonal drops",
            status: "open",
            workflow: "WF5",
            priority: "low",
          },
        ],
      },
      {
        id: "3.3",
        title: "Scheduler Infrastructure",
        phase: "Infrastructure",
        description: "Robust job scheduling with Redis queue",
        userStories: [
          {
            id: "US-3.3.1",
            title: "Configure Redis for job queue management",
            status: "open",
            priority: "high",
          },
          {
            id: "US-3.3.2",
            title: "Implement retry logic for failed jobs",
            status: "open",
            priority: "medium",
          },
          {
            id: "US-3.3.3",
            title: "Add job monitoring and logging",
            status: "open",
            priority: "medium",
          },
        ],
      },
    ],
  },
  {
    number: 4,
    name: "UAT & Handoff",
    theme: "Go Live",
    focus: "Testing, documentation, training, and deployment",
    startDate: "2026-01-06",
    endDate: "2026-01-12",
    epics: [
      {
        id: "4.1",
        title: "Quality Assurance",
        phase: "Testing",
        description: "Comprehensive testing of all workflows",
        userStories: [
          {
            id: "US-4.1.1",
            title: "Write unit tests for all workflow logic",
            status: "open",
            priority: "critical",
          },
          {
            id: "US-4.1.2",
            title: "Conduct integration tests with Everflow API",
            status: "open",
            priority: "critical",
          },
          {
            id: "US-4.1.3",
            title: "Perform end-to-end conversation flow testing",
            status: "open",
            priority: "high",
          },
          {
            id: "US-4.1.4",
            title: "Load test for concurrent user handling",
            status: "open",
            priority: "medium",
          },
        ],
      },
      {
        id: "4.2",
        title: "User Acceptance Testing",
        phase: "UAT",
        description: "Client testing and feedback incorporation",
        userStories: [
          {
            id: "US-4.2.1",
            title: "Deploy to UAT environment",
            status: "open",
            priority: "critical",
          },
          {
            id: "US-4.2.2",
            title: "Conduct UAT sessions with client",
            status: "open",
            priority: "critical",
          },
          {
            id: "US-4.2.3",
            title: "Address feedback and bug fixes",
            status: "open",
            priority: "high",
          },
          {
            id: "US-4.2.4",
            title: "Obtain sign-off for production release",
            status: "open",
            priority: "critical",
          },
        ],
      },
      {
        id: "4.3",
        title: "Documentation & Handoff",
        phase: "Handoff",
        description: "Complete documentation and knowledge transfer",
        userStories: [
          {
            id: "US-4.3.1",
            title: "Write API documentation for all endpoints",
            status: "open",
            priority: "high",
          },
          {
            id: "US-4.3.2",
            title: "Create user guide for chat interface",
            status: "open",
            priority: "high",
          },
          {
            id: "US-4.3.3",
            title: "Prepare deployment runbook",
            status: "open",
            priority: "high",
          },
          {
            id: "US-4.3.4",
            title: "Conduct training session with client team",
            status: "open",
            priority: "critical",
          },
        ],
      },
    ],
  },
];

// Helper functions for calculating metrics
export function calculateSprintMetrics(sprint: Sprint) {
  const allStories = sprint.epics.flatMap(e => e.userStories);
  const done = allStories.filter(s => s.status === 'done').length;
  const inProgress = allStories.filter(s => s.status === 'in-progress').length;
  const blocked = allStories.filter(s => s.status === 'blocked').length;
  const open = allStories.filter(s => s.status === 'open').length;
  const total = allStories.length;
  const progress = total > 0 ? Math.round((done / total) * 100) : 0;

  return { done, inProgress, blocked, open, total, progress };
}

export function calculateOverallMetrics() {
  const allStories = sprints.flatMap(s => s.epics.flatMap(e => e.userStories));
  const done = allStories.filter(s => s.status === 'done').length;
  const inProgress = allStories.filter(s => s.status === 'in-progress').length;
  const blocked = allStories.filter(s => s.status === 'blocked').length;
  const open = allStories.filter(s => s.status === 'open').length;
  const total = allStories.length;
  const progress = total > 0 ? Math.round((done / total) * 100) : 0;

  return { done, inProgress, blocked, open, total, progress };
}

export function getCurrentSprint(): Sprint | undefined {
  const today = new Date();
  return sprints.find(s => {
    const start = new Date(s.startDate);
    const end = new Date(s.endDate);
    return today >= start && today <= end;
  });
}

export function getSprintByNumber(num: number): Sprint | undefined {
  return sprints.find(s => s.number === num);
}







