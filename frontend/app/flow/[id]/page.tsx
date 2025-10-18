"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter, useSearchParams } from "next/navigation";
import { useResearchStream, ConnectionStatus } from "@/lib/api";
import AgentAvatar, { AGENT_CONFIGS } from "@/components/AgentAvatar";
import ConversationFeed from "@/components/ConversationFeed";
import PhaseProgress from "@/components/PhaseProgress";
import LiveStats from "@/components/LiveStats";
import ConnectionStatusOverlay from "@/components/ConnectionStatus";

export default function FlowPage() {
  const params = useParams();
  const searchParams = useSearchParams();
  const router = useRouter();
  
  const researchId = params.id as string;
  const question = searchParams.get("question") || "Research question not provided";
  
  const [showCelebration, setShowCelebration] = useState(false);
  const [showMobileStats, setShowMobileStats] = useState(false);
  const [celebrationDismissed, setCelebrationDismissed] = useState(false);

  // Use the research stream hook
  const {
    messages,
    currentPhase,
    activeAgent,
    iteration,
    maxIterations,
    qualityScore,
    qualityHistory,
    connectionStatus,
    error,
    startTime,
    reconnect,
  } = useResearchStream(researchId, question, {
    onPhaseChange: (phase) => {
      console.log("Phase changed:", phase);
    },
    onIterationComplete: (iter, quality) => {
      console.log(`Orbit ${iter} complete. Quality: ${quality}`);
    },
    onComplete: (finalState) => {
      console.log("Research complete!", finalState);
      setShowCelebration(true);
    },
    onError: (err) => {
      console.error("Stream error:", err);
    },
  });

  // Auto-dismiss celebration after 3 seconds
  useEffect(() => {
    if (showCelebration) {
      const timer = setTimeout(() => {
        setCelebrationDismissed(true);
      }, 3000);
      return () => clearTimeout(timer);
    }
  }, [showCelebration]);

  // Open paper in new tab
  const openPaperInNewTab = () => {
    window.open(`/papers/${researchId}`, '_blank');
  };

  return (
    <main className="min-h-screen bg-background flex flex-col">
      {/* Fixed Header */}
      <header className="sticky top-0 z-50 bg-background-light border-b border-gray-800 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <h1 className="text-2xl font-bold glow-text">FLUX</h1>
            <div className="h-6 w-px bg-gray-700"></div>
            <p className="text-gray-300 max-w-2xl truncate">{question}</p>
          </div>

          <div className="flex items-center gap-4">
            {/* Live Indicator */}
            {connectionStatus === ConnectionStatus.CONNECTED && (
              <div className="flex items-center gap-2 px-4 py-2 bg-red-500/20 border border-red-500 rounded-lg">
                <span className="w-3 h-3 bg-red-500 rounded-full animate-pulse"></span>
                <span className="text-red-400 font-semibold">LIVE</span>
              </div>
            )}

            {connectionStatus === ConnectionStatus.COMPLETE && (
              <div className="flex items-center gap-2 px-4 py-2 bg-green-500/20 border border-green-500 rounded-lg">
                <span className="w-3 h-3 bg-green-500 rounded-full"></span>
                <span className="text-green-400 font-semibold">COMPLETE</span>
              </div>
            )}

            {connectionStatus === ConnectionStatus.RECONNECTING && (
              <div className="flex items-center gap-2 px-4 py-2 bg-yellow-500/20 border border-yellow-500 rounded-lg">
                <span className="w-3 h-3 bg-yellow-500 rounded-full animate-pulse"></span>
                <span className="text-yellow-400 font-semibold">RECONNECTING...</span>
              </div>
            )}

            {/* Iteration Counter */}
            <div className="text-gray-400">
              Orbit <span className="text-primary-400 font-bold">{iteration + 1}</span> / {maxIterations}
            </div>
          </div>
        </div>
      </header>

      {/* Main Content - Three Column Layout */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Sidebar - Agent Avatars */}
        <aside className="w-1/5 bg-background-light border-r border-gray-800 p-4 overflow-y-auto">
          <h3 className="text-sm font-semibold text-gray-400 mb-4 uppercase">Research Team</h3>
          <div className="space-y-6">
            {Object.values(AGENT_CONFIGS).map((agent) => {
              const isActive = agent.name === activeAgent;
              
              return (
                <AgentAvatar
                  key={agent.name}
                  agent={agent}
                  active={isActive}
                  size="md"
                  showLabel={true}
                />
              );
            })}
          </div>
        </aside>

        {/* Center Column - Phase Progress & Conversation Feed */}
        <main className="flex-1 flex flex-col overflow-hidden">
          {/* Phase Progress */}
          <PhaseProgress
            currentPhase={currentPhase}
            progress={Math.round(((iteration + 1) / maxIterations) * 100)}
            iteration={iteration}
            maxIterations={maxIterations}
          />

          {/* Conversation Feed */}
          {connectionStatus === ConnectionStatus.CONNECTING && (
            <div className="flex-1 flex items-center justify-center">
              <div className="text-center py-12">
                <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
                <p className="text-gray-400 mt-4">Connecting to research stream...</p>
              </div>
            </div>
          )}

          {connectionStatus === ConnectionStatus.ERROR && (
            <div className="flex-1 flex items-center justify-center">
              <div className="text-center py-12">
                <div className="text-6xl mb-4">❌</div>
                <p className="text-red-400 mb-4">Connection Error</p>
                <p className="text-gray-400 mb-6">{error}</p>
                <button onClick={reconnect} className="btn-primary">
                  Retry Connection
                </button>
              </div>
            </div>
          )}

          {connectionStatus !== ConnectionStatus.CONNECTING && connectionStatus !== ConnectionStatus.ERROR && (
            <ConversationFeed
              messages={messages}
              activeAgent={activeAgent}
              isWaiting={connectionStatus === ConnectionStatus.CONNECTED}
            />
          )}
        </main>

        {/* Right Sidebar - Live Stats */}
        <LiveStats
          phase={currentPhase}
          activeAgent={AGENT_CONFIGS[activeAgent] || null}
          iteration={iteration}
          maxIterations={maxIterations}
          qualityScore={qualityScore}
          qualityHistory={qualityHistory}
          startTime={startTime}
        />
      </div>

      {/* Celebration Overlay - Auto-dismisses after 3 seconds */}
      {showCelebration && !celebrationDismissed && (
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 animate-slide-up">
          <div className="text-center p-8 bg-background-light rounded-2xl border-2 border-primary-500 shadow-2xl">
            <div className="text-8xl mb-6 animate-bounce">🎉</div>
            <h2 className="text-4xl font-bold text-primary-400 mb-4">Research Complete!</h2>
            <p className="text-gray-300 mb-2">
              Final Quality Score: {qualityScore.toFixed(1)}/10.0
            </p>
            <p className="text-sm text-gray-500 mb-6">
              Celebration will auto-dismiss in 3 seconds...
            </p>
            <div className="flex gap-4 justify-center">
              <button
                onClick={() => setCelebrationDismissed(true)}
                className="px-6 py-3 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-all"
              >
                Dismiss
              </button>
              <button
                onClick={openPaperInNewTab}
                className="btn-primary text-lg"
              >
                View Paper (New Tab) →
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Floating View Paper Button - Shows after completion */}
      {connectionStatus === ConnectionStatus.COMPLETE && (
        <div className="fixed bottom-8 right-8 z-40 flex flex-col gap-3">
          <button
            onClick={openPaperInNewTab}
            className="btn-primary text-lg px-6 py-4 shadow-2xl hover:scale-105 transition-transform flex items-center gap-3"
            title="Open research paper in new tab"
          >
            📄 View Paper
            <span className="text-xs opacity-75">(New Tab)</span>
          </button>
          <button
            onClick={() => router.push('/')}
            className="px-6 py-3 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-all text-sm"
          >
            ← Back to Home
          </button>
        </div>
      )}

      {/* Connection Status Overlay */}
      <ConnectionStatusOverlay
        status={connectionStatus as any}
        error={error ? new Error(error) : null}
        onRetry={reconnect}
        connectionQuality="good"
      />
    </main>
  );
}

