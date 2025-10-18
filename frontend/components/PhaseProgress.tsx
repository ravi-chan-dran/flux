"use client";

import { motion } from "framer-motion";

/**
 * Phase configuration with colors
 */
const PHASES = [
  { name: "Ideation", color: "#9D4EDD", emoji: "💡" },
  { name: "Research", color: "#FFA500", emoji: "📚" },
  { name: "Design", color: "#14B8A6", emoji: "🔬" },
  { name: "Critique", color: "#EF4444", emoji: "🛡️" },
  { name: "Synthesis", color: "#6366F1", emoji: "✍️" },
];

/**
 * Phase mapping from backend phase names to indices
 */
const PHASE_MAP: Record<string, number> = {
  initialize: 0,
  hypotheses: 0,
  research: 1,
  experiments: 2,
  critique: 3,
  complete: 4,
};

/**
 * PhaseProgress Props
 */
interface PhaseProgressProps {
  currentPhase: string;
  progress: number; // 0-100
  iteration: number;
  maxIterations: number;
  estimatedTime?: string;
}

/**
 * PhaseProgress Component
 * 
 * Visual phase timeline showing:
 * - 5 phases with color coding
 * - Completed, current, and future states
 * - Progress ring around current phase
 * - Orbital iteration indicator
 * - Overall progress bar
 * - Smooth animations
 * - Responsive mobile layout
 */
export default function PhaseProgress({
  currentPhase,
  progress,
  iteration,
  maxIterations,
  estimatedTime,
}: PhaseProgressProps) {
  const currentPhaseIndex = PHASE_MAP[currentPhase] ?? 0;

  return (
    <div className="bg-background-light border-b border-gray-800 p-6">
      {/* Header with Progress Percentage */}
      <div className="flex justify-between items-center mb-6">
        <h3 className="text-sm font-semibold text-gray-400 uppercase">
          Research Phase
        </h3>
        <div className="flex items-center gap-4">
          <span className="text-sm text-gray-500">
            {Math.round((currentPhaseIndex / (PHASES.length - 1)) * 100)}% Complete
          </span>
          {estimatedTime && (
            <span className="text-xs text-gray-500">
              Est. {estimatedTime} remaining
            </span>
          )}
        </div>
      </div>

      {/* Phase Timeline - Desktop */}
      <div className="hidden md:block relative">
        <div className="flex justify-between items-start">
          {PHASES.map((phase, index) => {
            const isCompleted = index < currentPhaseIndex;
            const isCurrent = index === currentPhaseIndex;
            const isFuture = index > currentPhaseIndex;

            return (
              <div
                key={phase.name}
                className="flex flex-col items-center flex-1 relative"
              >
                {/* Phase Circle */}
                <motion.div
                  className="relative z-10"
                  initial={false}
                  animate={{
                    scale: isCurrent ? 1.2 : 1,
                  }}
                  transition={{ duration: 0.3 }}
                >
                  {/* Progress Ring for Current Phase */}
                  {isCurrent && (
                    <svg
                      className="absolute inset-0 -m-2"
                      width="56"
                      height="56"
                      style={{ transform: "rotate(-90deg)" }}
                    >
                      <circle
                        cx="28"
                        cy="28"
                        r="24"
                        stroke={phase.color}
                        strokeWidth="3"
                        fill="none"
                        strokeDasharray={`${(progress / 100) * 150.8} 150.8`}
                        className="transition-all duration-500"
                      />
                    </svg>
                  )}

                  {/* Phase Circle */}
                  <motion.div
                    className={`w-12 h-12 rounded-full flex items-center justify-center text-xl font-bold transition-all ${
                      isCompleted
                        ? "bg-green-500 text-white"
                        : isCurrent
                        ? "text-white"
                        : "bg-gray-700 text-gray-400"
                    }`}
                    style={{
                      backgroundColor: isCurrent ? phase.color : undefined,
                    }}
                    animate={
                      isCurrent
                        ? {
                            boxShadow: [
                              `0 0 0px ${phase.color}`,
                              `0 0 20px ${phase.color}`,
                              `0 0 0px ${phase.color}`,
                            ],
                          }
                        : {}
                    }
                    transition={{
                      duration: 2,
                      repeat: isCurrent ? Infinity : 0,
                    }}
                  >
                    {isCompleted ? "✓" : phase.emoji}
                  </motion.div>
                </motion.div>

                {/* Phase Label */}
                <span
                  className={`text-xs mt-3 font-medium transition-colors ${
                    isCurrent
                      ? "font-semibold"
                      : "text-gray-500"
                  }`}
                  style={{ color: isCurrent ? phase.color : undefined }}
                >
                  {phase.name}
                </span>
              </div>
            );
          })}
        </div>

        {/* Connecting Lines */}
        <div className="absolute top-6 left-0 right-0 h-1 bg-gray-700 -z-0">
          <motion.div
            className="h-full bg-gradient-to-r from-green-500 to-primary-500"
            initial={{ width: "0%" }}
            animate={{
              width: `${(currentPhaseIndex / (PHASES.length - 1)) * 100}%`,
            }}
            transition={{ duration: 0.5 }}
          />
        </div>
      </div>

      {/* Phase Timeline - Mobile (Vertical) */}
      <div className="md:hidden space-y-4">
        {PHASES.map((phase, index) => {
          const isCompleted = index < currentPhaseIndex;
          const isCurrent = index === currentPhaseIndex;

          return (
            <div key={phase.name} className="flex items-center gap-4">
              {/* Phase Circle */}
              <div className="relative">
                {isCurrent && (
                  <svg
                    className="absolute inset-0 -m-2"
                    width="48"
                    height="48"
                    style={{ transform: "rotate(-90deg)" }}
                  >
                    <circle
                      cx="24"
                      cy="24"
                      r="20"
                      stroke={phase.color}
                      strokeWidth="3"
                      fill="none"
                      strokeDasharray={`${(progress / 100) * 125.6} 125.6`}
                      className="transition-all duration-500"
                    />
                  </svg>
                )}

                <motion.div
                  className={`w-10 h-10 rounded-full flex items-center justify-center text-lg transition-all ${
                    isCompleted
                      ? "bg-green-500 text-white"
                      : isCurrent
                      ? "text-white"
                      : "bg-gray-700 text-gray-400"
                  }`}
                  style={{
                    backgroundColor: isCurrent ? phase.color : undefined,
                  }}
                  animate={
                    isCurrent
                      ? {
                          boxShadow: [
                            `0 0 0px ${phase.color}`,
                            `0 0 15px ${phase.color}`,
                            `0 0 0px ${phase.color}`,
                          ],
                        }
                      : {}
                  }
                  transition={{
                    duration: 2,
                    repeat: isCurrent ? Infinity : 0,
                  }}
                >
                  {isCompleted ? "✓" : phase.emoji}
                </motion.div>
              </div>

              {/* Phase Info */}
              <div className="flex-1">
                <div
                  className={`text-sm font-medium ${
                    isCurrent ? "font-semibold" : ""
                  }`}
                  style={{ color: isCurrent ? phase.color : "#9CA3AF" }}
                >
                  {phase.name}
                </div>
                {isCurrent && (
                  <div className="text-xs text-gray-500 mt-1">
                    {progress}% complete
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Orbital Iteration Indicator */}
      <div className="mt-6 flex items-center justify-center gap-3">
        <OrbitalAnimation />
        <span className="text-sm font-medium text-gray-400">
          Orbit <span className="text-primary-400 font-bold">{iteration + 1}</span> of{" "}
          {maxIterations}
        </span>
      </div>

      {/* Overall Progress Bar */}
      <div className="mt-4">
        <div className="w-full bg-gray-700 rounded-full h-2 overflow-hidden">
          <motion.div
            className="h-full bg-gradient-to-r from-purple-500 via-primary-500 to-indigo-500"
            initial={{ width: "0%" }}
            animate={{
              width: `${
                ((iteration * PHASES.length + currentPhaseIndex) /
                  (maxIterations * PHASES.length)) *
                100
              }%`,
            }}
            transition={{ duration: 0.5 }}
          />
        </div>
      </div>
    </div>
  );
}

/**
 * Orbital Animation Component
 * Shows dots circling in orbit
 */
function OrbitalAnimation() {
  return (
    <div className="relative w-8 h-8">
      {/* Center Dot */}
      <div className="absolute top-1/2 left-1/2 w-2 h-2 bg-primary-400 rounded-full transform -translate-x-1/2 -translate-y-1/2" />

      {/* Orbiting Dots */}
      {[0, 120, 240].map((rotation) => (
        <motion.div
          key={rotation}
          className="absolute top-1/2 left-1/2 w-1.5 h-1.5 bg-primary-300 rounded-full"
          style={{
            transformOrigin: "0 0",
          }}
          animate={{
            rotate: [rotation, rotation + 360],
            x: [12, 12],
            y: [-0.75, -0.75],
          }}
          transition={{
            duration: 3,
            repeat: Infinity,
            ease: "linear",
          }}
        />
      ))}
    </div>
  );
}

