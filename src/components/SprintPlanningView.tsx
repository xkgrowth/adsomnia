'use client';

import { useState, useEffect } from 'react';
import {
  sprints,
  projectMeta,
  calculateSprintMetrics,
  calculateOverallMetrics,
  getCurrentSprint,
  type Sprint,
  type Epic,
  type UserStory,
} from '@/data/sprintData';

// Icons
const RocketIcon = () => (
  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M15.59 14.37a6 6 0 01-5.84 7.38v-4.8m5.84-2.58a14.98 14.98 0 006.16-12.12A14.98 14.98 0 009.631 8.41m5.96 5.96a14.926 14.926 0 01-5.841 2.58m-.119-8.54a6 6 0 00-7.381 5.84h4.8m2.581-5.84a14.927 14.927 0 00-2.58 5.84m2.699 2.7c-.103.021-.207.041-.311.06a15.09 15.09 0 01-2.448-2.448 14.9 14.9 0 01.06-.312m-2.24 2.39a4.493 4.493 0 00-1.757 4.306 4.493 4.493 0 004.306-1.758M16.5 9a1.5 1.5 0 11-3 0 1.5 1.5 0 013 0z" />
  </svg>
);

const UsersIcon = () => (
  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M15 19.128a9.38 9.38 0 002.625.372 9.337 9.337 0 004.121-.952 4.125 4.125 0 00-7.533-2.493M15 19.128v-.003c0-1.113-.285-2.16-.786-3.07M15 19.128v.106A12.318 12.318 0 018.624 21c-2.331 0-4.512-.645-6.374-1.766l-.001-.109a6.375 6.375 0 0111.964-3.07M12 6.375a3.375 3.375 0 11-6.75 0 3.375 3.375 0 016.75 0zm8.25 2.25a2.625 2.625 0 11-5.25 0 2.625 2.625 0 015.25 0z" />
  </svg>
);

const ChevronIcon = ({ isOpen }: { isOpen: boolean }) => (
  <svg
    className={`w-5 h-5 transition-transform duration-300 ${isOpen ? 'rotate-180' : ''}`}
    fill="none"
    viewBox="0 0 24 24"
    stroke="currentColor"
    strokeWidth={2}
  >
    <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
  </svg>
);

const CheckCircleIcon = () => (
  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
  </svg>
);

const ClockIcon = () => (
  <svg className="w-4 h-4 animate-pulse" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" />
  </svg>
);

const AlertIcon = () => (
  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
  </svg>
);

const CircleIcon = () => (
  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
    <circle cx="12" cy="12" r="9" />
  </svg>
);

// Status icon selector
function getStatusIcon(status: string) {
  switch (status) {
    case 'done':
      return <CheckCircleIcon />;
    case 'in-progress':
      return <ClockIcon />;
    case 'blocked':
      return <AlertIcon />;
    default:
      return <CircleIcon />;
  }
}

// Glowing status dot
const StatusDot = ({ status }: { status: string }) => {
  const colors: Record<string, string> = {
    done: 'bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]',
    'in-progress': 'bg-amber-400 shadow-[0_0_8px_rgba(251,191,36,0.5)]',
    blocked: 'bg-rose-500 shadow-[0_0_8px_rgba(244,63,94,0.5)]',
    open: 'bg-cyan-400 shadow-[0_0_8px_rgba(34,211,238,0.5)]',
  };
  return <span className={`inline-block w-2 h-2 rounded-full ${colors[status] || colors.open}`} />;
};

// Status badge
const StatusBadge = ({ status }: { status: string }) => {
  const styles: Record<string, string> = {
    done: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
    'in-progress': 'bg-amber-500/20 text-amber-400 border-amber-500/30',
    blocked: 'bg-rose-500/20 text-rose-400 border-rose-500/30',
    open: 'bg-cyan-500/20 text-cyan-400 border-cyan-500/30',
  };
  const labels: Record<string, string> = {
    done: 'Done',
    'in-progress': 'In Progress',
    blocked: 'Blocked',
    open: 'Open',
  };
  return (
    <span className={`text-xs font-medium px-2 py-0.5 rounded-full border ${styles[status] || styles.open}`}>
      {labels[status] || 'Open'}
    </span>
  );
};

// Workflow badge
const WorkflowBadge = ({ workflow }: { workflow?: string }) => {
  if (!workflow) return null;
  return (
    <span className="px-2 py-0.5 text-xs font-mono bg-slate-700/50 text-slate-400 rounded">
      {workflow}
    </span>
  );
};

// Glowing progress bar with segments
function GlowingProgressBar({ 
  done, inProgress, blocked, open, total, size = 'default' 
}: { 
  done: number; 
  inProgress: number; 
  blocked: number; 
  open: number; 
  total: number;
  size?: 'default' | 'large';
}) {
  if (total === 0) return null;
  
  const donePercent = (done / total) * 100;
  const inProgressPercent = (inProgress / total) * 100;
  const blockedPercent = (blocked / total) * 100;
  const openPercent = (open / total) * 100;
  
  const heightClass = size === 'large' ? 'h-3' : 'h-2';
  
  return (
    <div className={`w-full bg-slate-800/50 rounded-full ${heightClass} overflow-hidden flex backdrop-blur-sm`}>
      {donePercent > 0 && (
        <div 
          className={`bg-gradient-to-r from-emerald-500 to-emerald-400 ${heightClass} transition-all duration-700 ease-out shadow-[0_0_10px_rgba(16,185,129,0.5)]`}
          style={{ width: `${donePercent}%` }}
        />
      )}
      {inProgressPercent > 0 && (
        <div 
          className={`bg-gradient-to-r from-amber-500 to-amber-400 ${heightClass} transition-all duration-700 ease-out shadow-[0_0_10px_rgba(245,158,11,0.5)]`}
          style={{ width: `${inProgressPercent}%` }}
        />
      )}
      {blockedPercent > 0 && (
        <div 
          className={`bg-gradient-to-r from-rose-500 to-rose-400 ${heightClass} transition-all duration-700 ease-out shadow-[0_0_10px_rgba(244,63,94,0.5)]`}
          style={{ width: `${blockedPercent}%` }}
        />
      )}
      {openPercent > 0 && (
        <div 
          className={`bg-gradient-to-r from-cyan-500 to-cyan-400 ${heightClass} transition-all duration-700 ease-out shadow-[0_0_10px_rgba(6,182,212,0.5)]`}
          style={{ width: `${openPercent}%` }}
        />
      )}
    </div>
  );
}

// Main component
export default function SprintPlanningView() {
  const [collapsedSprints, setCollapsedSprints] = useState<Set<number>>(new Set());
  const [collapsedEpics, setCollapsedEpics] = useState<Set<string>>(new Set());
  const currentSprint = getCurrentSprint();
  const overall = calculateOverallMetrics();

  const toggleSprint = (sprintNumber: number) => {
    setCollapsedSprints(prev => {
      const updated = new Set(prev);
      if (updated.has(sprintNumber)) {
        updated.delete(sprintNumber);
      } else {
        updated.add(sprintNumber);
      }
      return updated;
    });
  };

  const toggleEpic = (epicId: string) => {
    setCollapsedEpics(prev => {
      const updated = new Set(prev);
      if (updated.has(epicId)) {
        updated.delete(epicId);
      } else {
        updated.add(epicId);
      }
      return updated;
    });
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  };

  const formatShortDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  const sprintIcons = ['🎯', '⚡', '🗺️', '✨'];

  return (
    <div className="min-h-screen bg-slate-950 relative overflow-hidden">
      {/* Animated Background */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-1/2 -left-1/2 w-full h-full bg-gradient-to-br from-cyan-500/10 via-transparent to-transparent rounded-full blur-3xl animate-pulse" />
        <div className="absolute -bottom-1/2 -right-1/2 w-full h-full bg-gradient-to-tl from-violet-500/10 via-transparent to-transparent rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }} />
        <div className="absolute top-1/4 right-1/4 w-96 h-96 bg-emerald-500/5 rounded-full blur-3xl" />
        {/* Grid Pattern */}
        <div 
          className="absolute inset-0 opacity-[0.02]"
          style={{
            backgroundImage: `linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)`,
            backgroundSize: '50px 50px'
          }}
        />
      </div>

      <div className="relative z-10 max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12 lg:py-20">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 text-sm font-medium mb-6 backdrop-blur-sm">
            <RocketIcon />
            <span>4 Week Sprint Cycle</span>
          </div>
          <h1 className="text-5xl lg:text-6xl font-black text-transparent bg-clip-text bg-gradient-to-r from-white via-cyan-200 to-violet-200 mb-4 tracking-tight">
            Adsomnia
          </h1>
          <p className="text-xl text-slate-400 font-light">
            Sprint Planning Dashboard
          </p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <div className="group relative bg-slate-900/50 backdrop-blur-xl rounded-2xl p-6 border border-slate-800 hover:border-cyan-500/50 transition-all duration-300">
            <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/5 to-transparent rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity" />
            <div className="relative">
              <p className="text-3xl font-bold text-white mb-1">{overall.progress}%</p>
              <p className="text-sm text-slate-500 uppercase tracking-wider">Complete</p>
            </div>
          </div>
          <div className="group relative bg-slate-900/50 backdrop-blur-xl rounded-2xl p-6 border border-slate-800 hover:border-emerald-500/50 transition-all duration-300">
            <div className="absolute inset-0 bg-gradient-to-br from-emerald-500/5 to-transparent rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity" />
            <div className="relative">
              <p className="text-3xl font-bold text-emerald-400 mb-1">{overall.done}</p>
              <p className="text-sm text-slate-500 uppercase tracking-wider">Done</p>
            </div>
          </div>
          <div className="group relative bg-slate-900/50 backdrop-blur-xl rounded-2xl p-6 border border-dashed border-cyan-500/50 hover:border-amber-500/50 transition-all duration-300">
            <div className="absolute inset-0 bg-gradient-to-br from-amber-500/5 to-transparent rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity" />
            <div className="relative">
              <p className="text-3xl font-bold text-amber-400 mb-1">{overall.inProgress}</p>
              <p className="text-sm text-slate-500 uppercase tracking-wider">In Progress</p>
            </div>
          </div>
          <div className="group relative bg-slate-900/50 backdrop-blur-xl rounded-2xl p-6 border border-slate-800 hover:border-cyan-500/50 transition-all duration-300">
            <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/5 to-transparent rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity" />
            <div className="relative">
              <p className="text-3xl font-bold text-cyan-400 mb-1">{overall.open}</p>
              <p className="text-sm text-slate-500 uppercase tracking-wider">Open</p>
            </div>
          </div>
        </div>

        {/* Overall Progress */}
        <div className="bg-slate-900/50 backdrop-blur-xl rounded-2xl p-6 border border-slate-800 mb-8">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-semibold text-white">Overall Progress</h2>
            <span className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-violet-400">
              {overall.progress}%
            </span>
          </div>
          <GlowingProgressBar {...overall} size="large" />
          <div className="flex flex-wrap gap-6 mt-4 text-sm">
            <span className="flex items-center gap-2 text-emerald-400"><StatusDot status="done" /> Done</span>
            <span className="flex items-center gap-2 text-amber-400"><StatusDot status="in-progress" /> In Progress</span>
            <span className="flex items-center gap-2 text-rose-400"><StatusDot status="blocked" /> Blocked</span>
            <span className="flex items-center gap-2 text-cyan-400"><StatusDot status="open" /> Open</span>
          </div>
        </div>

        {/* Developer Guide */}
        <div className="bg-slate-900/50 backdrop-blur-xl rounded-2xl p-6 border border-slate-800 mb-8">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 rounded-lg bg-violet-500/20 text-violet-400">
              <UsersIcon />
            </div>
            <h2 className="text-lg font-semibold text-white">Developer Guide</h2>
          </div>
          <div className="text-slate-300">
            <p className="text-slate-300 mb-4">
              <span className="text-white font-semibold">Project Role:</span> LLM-powered automation agent for Everflow API integration
            </p>
            <p className="text-white font-semibold mb-3">Key Development Phases:</p>
            <ul className="space-y-2">
              <li className="flex items-start gap-2">
                <span>🟢</span>
                <span><span className="text-white font-medium">The Analyst</span> — Read-only data retrieval (WF2, WF3)</span>
              </li>
              <li className="flex items-start gap-2">
                <span>🟢</span>
                <span><span className="text-white font-medium">The Watchdog</span> — Monitoring & asset creation (WF1, WF6)</span>
              </li>
              <li className="flex items-start gap-2">
                <span>🟢</span>
                <span><span className="text-white font-medium">The Alerter</span> — Scheduled monitoring & alerts (WF4, WF5)</span>
              </li>
              <li className="flex items-start gap-2">
                <span>🟢</span>
                <span><span className="text-white font-medium">Safety First</span> — User confirmation required for write operations</span>
              </li>
              <li className="flex items-start gap-2">
                <span>🟢</span>
                <span><span className="text-white font-medium">Ephemeral Processing</span> — No data persistence, real-time only</span>
              </li>
              <li className="flex items-start gap-2">
                <span>🟢</span>
                <span><span className="text-white font-medium">Go-Live Target</span> — {formatDate(projectMeta.targetEndDate)}</span>
              </li>
            </ul>
          </div>
        </div>

        {/* Sprint Timeline */}
        <div className="bg-slate-900/50 backdrop-blur-xl rounded-2xl p-6 border border-slate-800 mb-8">
          <h2 className="text-lg font-semibold text-white mb-6">Sprint Timeline</h2>
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
            {sprints.map((sprint, index) => {
              const metrics = calculateSprintMetrics(sprint);
              const isCurrent = currentSprint?.number === sprint.number;
              const isComplete = metrics.progress === 100;
              
              return (
                <div 
                  key={sprint.number}
                  className={`relative p-4 rounded-xl border transition-all duration-300 ${
                    isComplete 
                      ? 'bg-emerald-500/10 border-emerald-500/30' 
                      : isCurrent 
                      ? 'bg-cyan-500/10 border-cyan-500/30 shadow-[0_0_30px_rgba(6,182,212,0.1)]' 
                      : 'bg-slate-800/50 border-slate-700'
                  }`}
                >
                  {isCurrent && (
                    <div className="absolute -top-2 right-4 px-2 py-0.5 bg-cyan-500 text-slate-900 text-[10px] font-bold uppercase tracking-wider rounded">
                      Now
                    </div>
                  )}
                  <div className="flex items-center gap-3 mb-3">
                    <div className={`p-2 rounded-lg ${
                      isComplete ? 'bg-emerald-500/20 text-emerald-400' : isCurrent ? 'bg-cyan-500/20 text-cyan-400' : 'bg-slate-700 text-slate-400'
                    }`}>
                      <span className="text-lg">{sprintIcons[index]}</span>
                    </div>
                    <div>
                      <p className={`font-semibold ${isComplete ? 'text-emerald-400' : isCurrent ? 'text-cyan-400' : 'text-slate-300'}`}>
                        Sprint {sprint.number}
                      </p>
                      <p className="text-xs text-slate-500">{formatShortDate(sprint.startDate)}</p>
                    </div>
                  </div>
                  <p className="text-sm text-slate-400 mb-3">{sprint.name}</p>
                  <div className="flex items-center gap-2">
                    <GlowingProgressBar {...metrics} />
                    <span className={`text-xs font-bold ${isComplete ? 'text-emerald-400' : isCurrent ? 'text-cyan-400' : 'text-slate-500'}`}>
                      {metrics.progress}%
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Sprint Details */}
        {sprints.map((sprint, index) => {
          const metrics = calculateSprintMetrics(sprint);
          const isCurrent = currentSprint?.number === sprint.number;
          const isCollapsed = collapsedSprints.has(sprint.number);

          return (
            <div 
              key={sprint.number} 
              className="bg-slate-900/50 backdrop-blur-xl rounded-2xl border border-slate-800 mb-6 overflow-hidden hover:border-slate-700 transition-all duration-300"
            >
              {/* Sprint Header */}
              <button
                onClick={() => toggleSprint(sprint.number)}
                className="w-full p-6 text-left hover:bg-slate-800/30 transition-all duration-300"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="p-3 rounded-xl bg-gradient-to-br from-cyan-500/20 to-violet-500/20 text-cyan-400">
                      <span className="text-2xl">{sprintIcons[index]}</span>
                    </div>
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <h2 className="text-xl font-bold text-white">
                          Sprint {sprint.number}: {sprint.name}
                        </h2>
                        {isCurrent && (
                          <span className="px-2 py-0.5 bg-cyan-500 text-slate-900 text-[10px] font-bold uppercase tracking-wider rounded">
                            Current
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-slate-500">
                        {formatShortDate(sprint.startDate)} — {formatShortDate(sprint.endDate)} • <span className="text-amber-400">{sprint.theme}</span>
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="text-right hidden sm:block">
                      <p className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-violet-400">
                        {metrics.progress}%
                      </p>
                      <p className="text-xs text-slate-500">{metrics.done}/{metrics.total} stories</p>
                    </div>
                    <div className="text-slate-500">
                      <ChevronIcon isOpen={!isCollapsed} />
                    </div>
                  </div>
                </div>
                <div className="mt-4">
                  <GlowingProgressBar {...metrics} />
                </div>
              </button>

              {/* Sprint Content */}
              {!isCollapsed && (
                <div className="px-6 pb-6 space-y-6">
                  {sprint.epics.length > 0 ? (
                    sprint.epics.map((epic) => {
                      const epicMetrics = {
                        done: epic.userStories.filter(s => s.status === 'done').length,
                        inProgress: epic.userStories.filter(s => s.status === 'in-progress').length,
                        blocked: epic.userStories.filter(s => s.status === 'blocked').length,
                        open: epic.userStories.filter(s => s.status === 'open').length,
                        total: epic.userStories.length,
                      };
                      const epicProgress = epicMetrics.total > 0 ? Math.round((epicMetrics.done / epicMetrics.total) * 100) : 0;
                      const isEpicCollapsed = collapsedEpics.has(epic.id);
                      
                      return (
                        <div 
                          key={epic.id} 
                          className="rounded-xl border border-slate-700/50 bg-slate-800/30 overflow-hidden"
                        >
                          {/* Epic Header */}
                          <div className="p-5 border-b border-slate-700/50">
                            <div className="flex items-start justify-between gap-4">
                              <div className="flex-1">
                                <div className="flex items-center gap-2 mb-2">
                                  <span className="text-xs font-mono text-cyan-400 bg-cyan-500/10 px-2 py-0.5 rounded">
                                    Epic {epic.id}
                                  </span>
                                  <span className="text-xs text-slate-500 uppercase tracking-wider">{epic.phase}</span>
                                </div>
                                <h4 className="text-lg font-semibold text-slate-200 mb-1">
                                  {epic.title}
                                </h4>
                                {epic.description && (
                                  <p className="text-sm text-slate-500">{epic.description}</p>
                                )}
                              </div>
                              <div className="text-right">
                                <span className="text-lg font-bold text-emerald-400">{epicProgress}%</span>
                                <div className="w-24 mt-2">
                                  <GlowingProgressBar {...epicMetrics} />
                                </div>
                              </div>
                            </div>
                          </div>
                          
                          {/* User Stories */}
                          <div className="p-5">
                            <button
                              onClick={() => toggleEpic(epic.id)}
                              className="w-full flex items-center justify-between text-left hover:bg-slate-700/20 rounded-lg p-2 -m-2 transition-colors mb-3"
                            >
                              <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                                User Stories ({epicMetrics.done}/{epic.userStories.length})
                              </span>
                              <ChevronIcon isOpen={!isEpicCollapsed} />
                            </button>
                            
                            {!isEpicCollapsed && (
                              <div className="space-y-2 mt-4">
                                {epic.userStories.map((story) => {
                                  const requiresOwner = story.priority === 'critical';
                                  return (
                                    <div
                                      key={story.id}
                                      className={`flex items-start gap-3 p-3 rounded-lg transition-all duration-200 ${
                                        story.status === 'done' 
                                          ? 'bg-emerald-500/5 border border-emerald-500/20' 
                                          : requiresOwner
                                          ? 'bg-violet-500/5 border border-violet-500/30 hover:border-violet-500/50'
                                          : 'bg-slate-700/20 border border-slate-700/50 hover:border-slate-600'
                                      }`}
                                    >
                                      <div className={`mt-0.5 ${
                                        story.status === 'done' ? 'text-emerald-400' 
                                        : story.status === 'in-progress' ? 'text-amber-400'
                                        : story.status === 'blocked' ? 'text-rose-400'
                                        : 'text-cyan-400'
                                      }`}>
                                        {getStatusIcon(story.status)}
                                      </div>
                                      <div className="flex-1 min-w-0">
                                        <div className="flex items-center gap-2 flex-wrap mb-1">
                                          <span className="text-xs font-mono text-slate-500 bg-slate-700/50 px-2 py-0.5 rounded">
                                            {story.id}
                                          </span>
                                          <StatusBadge status={story.status} />
                                          <WorkflowBadge workflow={story.workflow} />
                                          {requiresOwner && (
                                            <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-violet-500/20 text-violet-400 border border-violet-500/30">
                                              ⚡ CRITICAL
                                            </span>
                                          )}
                                        </div>
                                        <p className={`text-sm ${story.status === 'done' ? 'text-slate-500 line-through' : 'text-slate-300'}`}>
                                          {story.title}
                                        </p>
                                      </div>
                                    </div>
                                  );
                                })}
                              </div>
                            )}
                          </div>
                        </div>
                      );
                    })
                  ) : (
                    <p className="text-slate-500 italic text-center py-8">No epics found for this sprint.</p>
                  )}
                </div>
              )}
            </div>
          );
        })}

        {/* Footer */}
        <div className="text-center text-slate-600 text-sm mt-12">
          <p>Target Go-Live: <span className="text-cyan-400 font-semibold">{formatDate(projectMeta.targetEndDate)}</span></p>
          <p className="mt-2 text-slate-700">{projectMeta.client} • Built by blablabuild</p>
        </div>
      </div>
    </div>
  );
}
