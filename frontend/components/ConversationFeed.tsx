"use client";

import { useEffect, useRef, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import AgentAvatar, { AGENT_CONFIGS } from "./AgentAvatar";
import type { AgentMessage } from "@/lib/types";

/**
 * ConversationFeed Props
 */
interface ConversationFeedProps {
  messages: AgentMessage[];
  activeAgent: string;
  isWaiting?: boolean;
}

/**
 * ConversationFeed Component
 * 
 * Live-updating message feed with:
 * - Agent avatars and colored speech bubbles
 * - Slide-in animations for new messages
 * - Auto-scroll with manual scroll detection
 * - Special cards for sources, hypotheses, quality scores
 * - Typing indicator
 * - Glassmorphism styling
 * - Color coding by agent
 */
export default function ConversationFeed({
  messages,
  activeAgent,
  isWaiting = false,
}: ConversationFeedProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [isUserScrolling, setIsUserScrolling] = useState(false);
  const [showNewMessageButton, setShowNewMessageButton] = useState(false);
  const lastMessageCountRef = useRef(messages.length);

  // Auto-scroll to latest message
  const scrollToBottom = (behavior: ScrollBehavior = "smooth") => {
    messagesEndRef.current?.scrollIntoView({ behavior });
  };

  // Check if user is scrolling manually
  const handleScroll = () => {
    if (!containerRef.current) return;
    
    const { scrollTop, scrollHeight, clientHeight } = containerRef.current;
    const isNearBottom = scrollHeight - scrollTop - clientHeight < 100;
    
    setIsUserScrolling(!isNearBottom);
    setShowNewMessageButton(!isNearBottom && messages.length > 0);
  };

  // Auto-scroll when new message arrives
  useEffect(() => {
    if (messages.length > lastMessageCountRef.current && !isUserScrolling) {
      scrollToBottom();
    }
    lastMessageCountRef.current = messages.length;
  }, [messages.length, isUserScrolling]);

  // Format timestamp as relative time
  const formatRelativeTime = (timestamp: string) => {
    const now = new Date().getTime();
    const messageTime = new Date(timestamp).getTime();
    const diffSeconds = Math.floor((now - messageTime) / 1000);

    if (diffSeconds < 10) return "just now";
    if (diffSeconds < 60) return `${diffSeconds} seconds ago`;
    const diffMinutes = Math.floor(diffSeconds / 60);
    if (diffMinutes < 60) return `${diffMinutes} minute${diffMinutes > 1 ? "s" : ""} ago`;
    const diffHours = Math.floor(diffMinutes / 60);
    return `${diffHours} hour${diffHours > 1 ? "s" : ""} ago`;
  };

  return (
    <div className="relative flex-1 flex flex-col">
      {/* Scrollable Messages Container */}
      <div
        ref={containerRef}
        onScroll={handleScroll}
        className="flex-1 overflow-y-auto p-6 space-y-4"
      >
        <AnimatePresence initial={false}>
          {messages.map((message, index) => {
            const agent = AGENT_CONFIGS[message.agent];
            const isActive = message.agent === activeAgent;

            return (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: index * 0.05 }}
                className="flex items-start gap-4"
              >
                {/* Agent Avatar */}
                <div className="flex-shrink-0 mt-2">
                  <AgentAvatar
                    agent={agent || AGENT_CONFIGS["The Flow Master"]}
                    active={isActive}
                    size="sm"
                    showLabel={false}
                  />
                </div>

                {/* Message Content */}
                <div className="flex-1 min-w-0">
                  {/* Agent Name and Timestamp */}
                  <div className="flex items-center gap-2 mb-2">
                    <span
                      className="font-semibold text-sm"
                      style={{ color: agent?.color || "#06B6D4" }}
                    >
                      {message.agent}
                    </span>
                    <span className="text-xs text-gray-500">
                      {formatRelativeTime(message.timestamp)}
                    </span>
                  </div>

                  {/* Speech Bubble */}
                  <motion.div
                    className={`relative p-4 rounded-lg backdrop-blur-sm ${
                      isActive ? "animate-pulse-border" : ""
                    }`}
                    style={{
                      backgroundColor: `${agent?.color || "#06B6D4"}15`,
                      borderLeft: `3px solid ${agent?.color || "#06B6D4"}`,
                    }}
                  >
                    <p className="text-gray-200 leading-relaxed">
                      {message.message}
                    </p>

                    {/* Metadata Cards */}
                    {message.metadata && Object.keys(message.metadata).length > 0 && (
                      <div className="mt-4 space-y-3">
                        {/* Sources Card */}
                        {message.metadata.sources && message.metadata.sources.length > 0 && (
                          <SourcesCard sources={message.metadata.sources} />
                        )}

                        {/* Hypotheses Card */}
                        {message.metadata.hypotheses && message.metadata.hypotheses.length > 0 && (
                          <HypothesesCard hypotheses={message.metadata.hypotheses} />
                        )}

                        {/* Quality Score Card */}
                        {message.metadata.quality_score !== undefined && (
                          <QualityScoreCard
                            score={message.metadata.quality_score}
                            previousScore={
                              index > 0 &&
                              messages[index - 1].metadata?.quality_score !== undefined
                                ? messages[index - 1].metadata!.quality_score
                                : undefined
                            }
                          />
                        )}
                      </div>
                    )}
                  </motion.div>
                </div>
              </motion.div>
            );
          })}
        </AnimatePresence>

        {/* Typing Indicator */}
        {isWaiting && activeAgent && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="flex items-start gap-4"
          >
            <div className="flex-shrink-0 mt-2">
              <AgentAvatar
                agent={AGENT_CONFIGS[activeAgent] || AGENT_CONFIGS["The Flow Master"]}
                active={true}
                size="sm"
                showLabel={false}
              />
            </div>
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-2">
                <span
                  className="font-semibold text-sm"
                  style={{ color: AGENT_CONFIGS[activeAgent]?.color || "#06B6D4" }}
                >
                  {activeAgent}
                </span>
              </div>
              <div className="p-4 rounded-lg backdrop-blur-sm bg-gray-800/50">
                <TypingIndicator />
              </div>
            </div>
          </motion.div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* New Messages Button */}
      <AnimatePresence>
        {showNewMessageButton && (
          <motion.button
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 20 }}
            onClick={() => {
              setIsUserScrolling(false);
              scrollToBottom();
            }}
            className="absolute bottom-6 left-1/2 transform -translate-x-1/2 px-4 py-2 bg-primary-500 hover:bg-primary-600 text-white rounded-full shadow-lg flex items-center gap-2 transition-colors"
          >
            <span>↓</span>
            <span className="text-sm font-medium">New messages</span>
          </motion.button>
        )}
      </AnimatePresence>
    </div>
  );
}

/**
 * Sources Card Component
 */
function SourcesCard({ sources }: { sources: any[] }) {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div className="p-3 bg-background/50 backdrop-blur-sm rounded-lg border border-gray-700">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="flex items-center justify-between w-full text-left"
      >
        <div className="flex items-center gap-2">
          <span className="text-amber-400">📚</span>
          <span className="text-sm font-semibold text-gray-200">
            Sources Found ({sources.length})
          </span>
        </div>
        <span className="text-gray-400">{isExpanded ? "▼" : "▶"}</span>
      </button>

      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="mt-3 space-y-2 overflow-hidden"
          >
            {sources.map((source, idx) => (
              <div key={idx} className="p-2 bg-background/30 rounded text-sm">
                <a
                  href={source.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-primary-400 hover:text-primary-300 font-medium"
                >
                  {source.title}
                </a>
                <p className="text-gray-400 text-xs mt-1">
                  {source.authors?.join(", ")} • {source.year}
                  {source.citation_count && ` • ${source.citation_count} citations`}
                </p>
              </div>
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

/**
 * Hypotheses Card Component
 */
function HypothesesCard({ hypotheses }: { hypotheses: any[] }) {
  return (
    <div className="p-3 bg-background/50 backdrop-blur-sm rounded-lg border border-gray-700">
      <div className="flex items-center gap-2 mb-3">
        <span className="text-cyan-400">💡</span>
        <span className="text-sm font-semibold text-gray-200">
          Hypotheses ({hypotheses.length})
        </span>
      </div>
      <ol className="space-y-2 list-decimal list-inside">
        {hypotheses.map((hypothesis, idx) => (
          <li key={idx} className="text-sm text-gray-300">
            <span>{hypothesis.text}</span>
            {hypothesis.confidence && (
              <span
                className={`ml-2 px-2 py-0.5 rounded-full text-xs font-medium ${
                  hypothesis.confidence > 0.8
                    ? "bg-green-500/20 text-green-400"
                    : hypothesis.confidence > 0.5
                    ? "bg-yellow-500/20 text-yellow-400"
                    : "bg-red-500/20 text-red-400"
                }`}
              >
                {Math.round(hypothesis.confidence * 100)}% confidence
              </span>
            )}
          </li>
        ))}
      </ol>
    </div>
  );
}

/**
 * Quality Score Card Component
 */
function QualityScoreCard({
  score,
  previousScore,
}: {
  score: number;
  previousScore?: number;
}) {
  const improvement =
    previousScore !== undefined ? score - previousScore : 0;

  return (
    <div className="p-3 bg-background/50 backdrop-blur-sm rounded-lg border border-gray-700">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-2xl">🎯</span>
          <div>
            <div className="text-sm font-semibold text-gray-200">
              Quality Score
            </div>
            <div className="flex items-baseline gap-2">
              <span className="text-2xl font-bold text-primary-400">
                {score.toFixed(1)}
              </span>
              <span className="text-gray-500">/10.0</span>
            </div>
          </div>
        </div>
        {improvement !== 0 && (
          <div
            className={`flex items-center gap-1 px-2 py-1 rounded ${
              improvement > 0
                ? "bg-green-500/20 text-green-400"
                : "bg-red-500/20 text-red-400"
            }`}
          >
            <span>{improvement > 0 ? "↑" : "↓"}</span>
            <span className="text-sm font-medium">
              {Math.abs(improvement).toFixed(1)}
            </span>
          </div>
        )}
      </div>
    </div>
  );
}

/**
 * Typing Indicator Component
 */
function TypingIndicator() {
  return (
    <div className="flex items-center gap-1">
      {[0, 1, 2].map((i) => (
        <motion.div
          key={i}
          className="w-2 h-2 bg-primary-400 rounded-full"
          animate={{
            y: [0, -8, 0],
            opacity: [0.5, 1, 0.5],
          }}
          transition={{
            duration: 1,
            repeat: Infinity,
            delay: i * 0.15,
          }}
        />
      ))}
    </div>
  );
}

