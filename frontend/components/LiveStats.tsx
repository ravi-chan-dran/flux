"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import type { AgentConfig } from "./AgentAvatar";

/**
 * LiveStats Props
 */
interface LiveStatsProps {
  phase: string;
  phaseColor?: string;
  activeAgent: AgentConfig | null;
  iteration: number;
  maxIterations: number;
  qualityScore?: number;
  qualityHistory?: number[];
  startTime: Date | null;
  estimatedCompletion?: string;
  completedAgents?: string[];
}

/**
 * Phase display names and colors
 */
const PHASE_INFO: Record<string, { name: string; color: string }> = {
  initialize: { name: "Initialization", color: "#9D4EDD" },
  hypotheses: { name: "Ideation", color: "#9D4EDD" },
  research: { name: "Research", color: "#FFA500" },
  experiments: { name: "Design", color: "#14B8A6" },
  critique: { name: "Critique", color: "#EF4444" },
  complete: { name: "Synthesis", color: "#6366F1" },
};

/**
 * LiveStats Component
 * 
 * Right sidebar showing live research stats:
 * - Current phase with color
 * - Active agent with pulsing indicator
 * - Iteration progress with circular ring
 * - Quality score with color-coded bar
 * - Time elapsed (updating every second)
 * - Estimated remaining time
 * - Mini timeline of completed agents
 * - Quality trend sparkline
 * - Animated number changes
 * - Background pulse when active
 */
export default function LiveStats({
  phase,
  phaseColor,
  activeAgent,
  iteration,
  maxIterations,
  qualityScore,
  qualityHistory = [],
  startTime,
  estimatedCompletion,
  completedAgents = [],
}: LiveStatsProps) {
  const [elapsedTime, setElapsedTime] = useState(0);

  // Update elapsed time every second
  useEffect(() => {
    if (!startTime) return;

    const interval = setInterval(() => {
      const elapsed = Math.floor((Date.now() - startTime.getTime()) / 1000);
      setElapsedTime(elapsed);
    }, 1000);

    return () => clearInterval(interval);
  }, [startTime]);

  // Format time as MM:SS
  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  const phaseInfo = PHASE_INFO[phase] || { name: phase, color: phaseColor || "#06B6D4" };
  const iterationProgress = ((iteration + 1) / maxIterations) * 100;

  // Determine quality score color
  const getQualityColor = (score: number) => {
    if (score >= 8) return { color: "#10B981", label: "Excellent" };
    if (score >= 6) return { color: "#F59E0B", label: "Good" };
    return { color: "#EF4444", label: "Needs Work" };
  };

  return (
    <aside className="w-1/5 bg-background-light border-l border-gray-800 p-4 space-y-4 overflow-y-auto">
      {/* Header */}
      <h3 className="text-sm font-semibold text-gray-400 uppercase mb-4">
        Live Stats
      </h3>

      {/* Background Pulse Animation */}
      {activeAgent && (
        <motion.div
          className="absolute inset-0 pointer-events-none"
          animate={{
            opacity: [0, 0.03, 0],
          }}
          transition={{
            duration: 2,
            repeat: Infinity,
            ease: "easeInOut",
          }}
          style={{
            background: `radial-gradient(circle at center, ${activeAgent.color}, transparent)`,
          }}
        />
      )}

      {/* Current Phase Card */}
      <div className="card backdrop-blur-sm bg-background/50 relative overflow-hidden">
        <motion.div
          className="absolute inset-0 opacity-10"
          animate={{
            opacity: [0.05, 0.15, 0.05],
          }}
          transition={{
            duration: 3,
            repeat: Infinity,
          }}
          style={{ backgroundColor: phaseInfo.color }}
        />
        <p className="text-xs text-gray-500 mb-1 relative z-10">Current Phase</p>
        <p
          className="text-xl font-bold relative z-10"
          style={{ color: phaseInfo.color }}
        >
          {phaseInfo.name}
        </p>
      </div>

      {/* Active Agent Card */}
      {activeAgent && (
        <div className="card backdrop-blur-sm bg-background/50">
          <p className="text-xs text-gray-500 mb-2">Active Agent</p>
          <div className="flex items-center gap-3">
            <motion.div
              className="text-3xl"
              animate={{
                scale: [1, 1.1, 1],
              }}
              transition={{
                duration: 1.5,
                repeat: Infinity,
              }}
            >
              {activeAgent.emoji}
            </motion.div>
            <div className="flex-1">
              <p
                className="text-sm font-semibold"
                style={{ color: activeAgent.color }}
              >
                {activeAgent.name}
              </p>
              <p className="text-xs text-gray-500">{activeAgent.role}</p>
            </div>
            <motion.div
              className="w-2 h-2 rounded-full"
              style={{ backgroundColor: activeAgent.color }}
              animate={{
                opacity: [0.3, 1, 0.3],
              }}
              transition={{
                duration: 1,
                repeat: Infinity,
              }}
            />
          </div>
        </div>
      )}

      {/* Iteration Progress Card */}
      <div className="card backdrop-blur-sm bg-background/50">
        <p className="text-xs text-gray-500 mb-3">Progress</p>
        <div className="flex items-center gap-4">
          {/* Circular Progress Ring */}
          <div className="relative w-16 h-16">
            <svg className="transform -rotate-90" width="64" height="64">
              {/* Background Circle */}
              <circle
                cx="32"
                cy="32"
                r="28"
                stroke="#374151"
                strokeWidth="6"
                fill="none"
              />
              {/* Progress Circle */}
              <motion.circle
                cx="32"
                cy="32"
                r="28"
                stroke="#06B6D4"
                strokeWidth="6"
                fill="none"
                strokeDasharray={`${(iterationProgress / 100) * 175.93} 175.93`}
                initial={{ strokeDasharray: "0 175.93" }}
                animate={{
                  strokeDasharray: `${(iterationProgress / 100) * 175.93} 175.93`,
                }}
                transition={{ duration: 0.5 }}
              />
            </svg>
            <div className="absolute inset-0 flex items-center justify-center">
              <span className="text-xs font-bold text-primary-400">
                {Math.round(iterationProgress)}%
              </span>
            </div>
          </div>

          {/* Orbit Text */}
          <div>
            <p className="text-2xl font-bold text-primary-400">
              <AnimatedNumber value={iteration + 1} />
            </p>
            <p className="text-xs text-gray-500">of {maxIterations} Orbits</p>
          </div>
        </div>
      </div>

      {/* Quality Score Card */}
      {qualityScore !== undefined && qualityScore > 0 && (
        <div className="card backdrop-blur-sm bg-background/50">
          <p className="text-xs text-gray-500 mb-2">Quality Score</p>
          <div className="flex items-end gap-2 mb-3">
            <motion.span
              key={qualityScore}
              className="text-3xl font-bold"
              style={{ color: getQualityColor(qualityScore).color }}
              initial={{ scale: 1.2, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ duration: 0.3 }}
            >
              <AnimatedNumber value={qualityScore} decimals={1} />
            </motion.span>
            <span className="text-gray-500 mb-1">/10.0</span>
          </div>

          {/* Color-coded Progress Bar */}
          <div className="w-full bg-gray-700 rounded-full h-2 mb-2 overflow-hidden">
            <motion.div
              className="h-full rounded-full"
              style={{
                backgroundColor: getQualityColor(qualityScore).color,
              }}
              initial={{ width: "0%" }}
              animate={{ width: `${(qualityScore / 10) * 100}%` }}
              transition={{ duration: 0.5 }}
            />
          </div>

          <p className="text-xs" style={{ color: getQualityColor(qualityScore).color }}>
            {getQualityColor(qualityScore).label}
          </p>

          {/* Quality Trend Sparkline */}
          {qualityHistory.length > 1 && (
            <div className="mt-3 pt-3 border-t border-gray-700">
              <p className="text-xs text-gray-500 mb-2">Trend</p>
              <Sparkline data={qualityHistory} color={getQualityColor(qualityScore).color} />
            </div>
          )}
        </div>
      )}

      {/* Time Elapsed Card */}
      <div className="card backdrop-blur-sm bg-background/50">
        <p className="text-xs text-gray-500 mb-1">Time Elapsed</p>
        <p className="text-2xl font-mono font-bold text-gray-300">
          {formatTime(elapsedTime)}
        </p>
      </div>

      {/* Estimated Remaining Time */}
      {estimatedCompletion && (
        <div className="card backdrop-blur-sm bg-background/50">
          <p className="text-xs text-gray-500 mb-1">Est. Time Remaining</p>
          <p className="text-xl font-mono text-gray-400">{estimatedCompletion}</p>
        </div>
      )}

      {/* Completed Agents Mini Timeline */}
      {completedAgents.length > 0 && (
        <div className="card backdrop-blur-sm bg-background/50">
          <p className="text-xs text-gray-500 mb-3">Iteration Progress</p>
          <div className="flex flex-wrap gap-2">
            {completedAgents.map((agentName, idx) => (
              <motion.div
                key={idx}
                className="flex items-center gap-1 px-2 py-1 bg-green-500/20 rounded-full"
                initial={{ scale: 0, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ delay: idx * 0.1 }}
              >
                <span className="text-green-400 text-xs">✓</span>
                <span className="text-xs text-green-300">{agentName}</span>
              </motion.div>
            ))}
          </div>
        </div>
      )}
    </aside>
  );
}

/**
 * Animated Number Component
 * Counts up to target value with smooth animation
 */
function AnimatedNumber({
  value,
  decimals = 0,
}: {
  value: number;
  decimals?: number;
}) {
  const [displayValue, setDisplayValue] = useState(value);

  useEffect(() => {
    const duration = 500; // ms
    const steps = 30;
    const increment = (value - displayValue) / steps;
    let currentStep = 0;

    const timer = setInterval(() => {
      currentStep++;
      setDisplayValue((prev) => {
        const next = prev + increment;
        if (currentStep >= steps) {
          clearInterval(timer);
          return value;
        }
        return next;
      });
    }, duration / steps);

    return () => clearInterval(timer);
  }, [value]);

  return <>{displayValue.toFixed(decimals)}</>;
}

/**
 * Sparkline Chart Component
 * Shows quality score trend
 */
function Sparkline({ data, color }: { data: number[]; color: string }) {
  if (data.length < 2) return null;

  const width = 100;
  const height = 30;
  const padding = 2;

  const max = Math.max(...data);
  const min = Math.min(...data);
  const range = max - min || 1;

  const points = data
    .map((value, index) => {
      const x = (index / (data.length - 1)) * (width - 2 * padding) + padding;
      const y =
        height - padding - ((value - min) / range) * (height - 2 * padding);
      return `${x},${y}`;
    })
    .join(" ");

  return (
    <svg
      width={width}
      height={height}
      className="w-full"
      style={{ maxWidth: "200px" }}
    >
      <polyline
        points={points}
        fill="none"
        stroke={color}
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      {/* Points */}
      {data.map((value, index) => {
        const x = (index / (data.length - 1)) * (width - 2 * padding) + padding;
        const y =
          height - padding - ((value - min) / range) * (height - 2 * padding);
        return (
          <circle
            key={index}
            cx={x}
            cy={y}
            r="2"
            fill={color}
          />
        );
      })}
    </svg>
  );
}

