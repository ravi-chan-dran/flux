"use client";

import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

/**
 * Celebration intensity based on quality score
 */
const getCelebrationIntensity = (qualityScore: number): {
  confettiCount: number;
  duration: number;
  particleSpeed: number;
} => {
  if (qualityScore >= 9) {
    return { confettiCount: 60, duration: 4000, particleSpeed: 1.5 };
  } else if (qualityScore >= 7) {
    return { confettiCount: 40, duration: 3500, particleSpeed: 1.2 };
  } else {
    return { confettiCount: 25, duration: 3000, particleSpeed: 1.0 };
  }
};

/**
 * CelebrationAnimation Props
 */
interface CelebrationAnimationProps {
  qualityScore: number;
  iterationCount: number;
  totalTime: string; // e.g., "2:34"
  totalCost?: number;
  hypothesesCount?: number;
  experimentsCount?: number;
  sourcesCount?: number;
  onComplete?: () => void;
  onViewPaper?: () => void;
  skipCelebration?: boolean;
  enableSound?: boolean;
}

/**
 * CelebrationAnimation Component
 * 
 * Shows when research completes successfully:
 * - Confetti burst (proportional to quality)
 * - Animated checkmark with bounce
 * - Completion message with fade-in
 * - Quality score with counting animation
 * - Iteration count
 * - Stats cards (time, cost, hypotheses, etc.)
 * - Auto-fade after duration
 * - View Paper button
 * - Optional sound effect
 */
export default function CelebrationAnimation({
  qualityScore,
  iterationCount,
  totalTime,
  totalCost,
  hypothesesCount,
  experimentsCount,
  sourcesCount,
  onComplete,
  onViewPaper,
  skipCelebration = false,
  enableSound = false,
}: CelebrationAnimationProps) {
  const [show, setShow] = useState(true);
  const [animatedScore, setAnimatedScore] = useState(0);

  const intensity = getCelebrationIntensity(qualityScore);

  useEffect(() => {
    if (skipCelebration) {
      onComplete?.();
      return;
    }

    // Animate quality score counting up
    const duration = 1000;
    const steps = 50;
    const increment = qualityScore / steps;
    let currentStep = 0;

    const timer = setInterval(() => {
      currentStep++;
      setAnimatedScore((prev) => {
        const next = prev + increment;
        if (currentStep >= steps) {
          clearInterval(timer);
          return qualityScore;
        }
        return next;
      });
    }, duration / steps);

    // Play sound effect (if enabled and available)
    if (enableSound && typeof Audio !== "undefined") {
      try {
        // You can add a success sound file here
        // const audio = new Audio('/sounds/success.mp3');
        // audio.play();
      } catch (error) {
        console.log("Sound not available");
      }
    }

    // Auto-fade after duration
    const fadeTimer = setTimeout(() => {
      setShow(false);
      setTimeout(() => {
        onComplete?.();
      }, 500); // Wait for fade animation
    }, intensity.duration);

    return () => {
      clearInterval(timer);
      clearTimeout(fadeTimer);
    };
  }, [qualityScore, intensity.duration, onComplete, skipCelebration, enableSound]);

  if (skipCelebration) return null;

  return (
    <AnimatePresence>
      {show && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-[100] flex items-center justify-center bg-black/80 backdrop-blur-sm"
        >
          {/* Confetti Particles */}
          {[...Array(intensity.confettiCount)].map((_, i) => {
            const colors = ["#06B6D4", "#9D4EDD", "#FFA500", "#14B8A6", "#EF4444", "#6366F1"];
            const color = colors[i % colors.length];
            const startX = Math.random() * 100;
            const endX = startX + (Math.random() - 0.5) * 100;
            const rotation = Math.random() * 720 - 360;

            return (
              <motion.div
                key={i}
                className="absolute w-3 h-3 rounded-sm"
                style={{
                  backgroundColor: color,
                  left: `${startX}%`,
                  top: "-10%",
                }}
                animate={{
                  y: ["0vh", "110vh"],
                  x: [0, endX],
                  rotate: [0, rotation],
                  opacity: [1, 1, 0.5, 0],
                  scale: [1, 0.8, 0.6, 0.4],
                }}
                transition={{
                  duration: 2 * intensity.particleSpeed,
                  delay: Math.random() * 0.5,
                  ease: "easeOut",
                }}
              />
            );
          })}

          {/* Main Content */}
          <motion.div
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ delay: 0.2, type: "spring", bounce: 0.4 }}
            className="relative z-10 text-center px-4 max-w-2xl"
          >
            {/* Animated Checkmark */}
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.3, type: "spring", bounce: 0.6 }}
              className="mb-8 inline-block"
            >
              <motion.div
                className="w-32 h-32 rounded-full bg-green-500/20 border-4 border-green-500 flex items-center justify-center"
                animate={{
                  boxShadow: [
                    "0 0 0px rgba(34, 197, 94, 0.5)",
                    "0 0 40px rgba(34, 197, 94, 0.8)",
                    "0 0 0px rgba(34, 197, 94, 0.5)",
                  ],
                }}
                transition={{ duration: 2, repeat: Infinity }}
              >
                <motion.svg
                  width="64"
                  height="64"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="#22c55e"
                  strokeWidth="3"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  initial={{ pathLength: 0 }}
                  animate={{ pathLength: 1 }}
                  transition={{ delay: 0.5, duration: 0.6 }}
                >
                  <motion.path d="M20 6L9 17l-5-5" />
                </motion.svg>
              </motion.div>
            </motion.div>

            {/* Completion Message */}
            <motion.h1
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6 }}
              className="text-5xl font-bold text-white mb-4"
            >
              Research Complete!
            </motion.h1>

            {/* Quality Score */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.8 }}
              className="mb-6"
            >
              <div className="text-gray-400 text-sm mb-2">Quality Score</div>
              <div className="flex items-baseline justify-center gap-2">
                <motion.span
                  className="text-6xl font-bold"
                  style={{
                    color:
                      qualityScore >= 8
                        ? "#22c55e"
                        : qualityScore >= 6
                        ? "#f59e0b"
                        : "#ef4444",
                  }}
                >
                  {animatedScore.toFixed(1)}
                </motion.span>
                <span className="text-3xl text-gray-500">/10.0</span>
              </div>
            </motion.div>

            {/* Iteration Count */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 1.0 }}
              className="text-xl text-gray-300 mb-8"
            >
              Completed in{" "}
              <span className="font-bold text-primary-400">{iterationCount}</span>{" "}
              {iterationCount === 1 ? "orbit" : "orbits"}
            </motion.div>

            {/* Stats Cards */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 1.2 }}
              className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8"
            >
              {/* Total Time */}
              <div className="bg-background/50 backdrop-blur-sm rounded-lg p-4 border border-gray-700">
                <div className="text-2xl mb-1">⏱️</div>
                <div className="text-sm text-gray-400">Time</div>
                <div className="text-lg font-bold text-white">{totalTime}</div>
              </div>

              {/* Cost */}
              {totalCost !== undefined && (
                <div className="bg-background/50 backdrop-blur-sm rounded-lg p-4 border border-gray-700">
                  <div className="text-2xl mb-1">💰</div>
                  <div className="text-sm text-gray-400">Cost</div>
                  <div className="text-lg font-bold text-white">
                    ${totalCost.toFixed(2)}
                  </div>
                </div>
              )}

              {/* Hypotheses */}
              {hypothesesCount !== undefined && (
                <div className="bg-background/50 backdrop-blur-sm rounded-lg p-4 border border-gray-700">
                  <div className="text-2xl mb-1">💡</div>
                  <div className="text-sm text-gray-400">Hypotheses</div>
                  <div className="text-lg font-bold text-white">{hypothesesCount}</div>
                </div>
              )}

              {/* Experiments */}
              {experimentsCount !== undefined && (
                <div className="bg-background/50 backdrop-blur-sm rounded-lg p-4 border border-gray-700">
                  <div className="text-2xl mb-1">🔬</div>
                  <div className="text-sm text-gray-400">Experiments</div>
                  <div className="text-lg font-bold text-white">{experimentsCount}</div>
                </div>
              )}

              {/* Sources */}
              {sourcesCount !== undefined && (
                <div className="bg-background/50 backdrop-blur-sm rounded-lg p-4 border border-gray-700">
                  <div className="text-2xl mb-1">📚</div>
                  <div className="text-sm text-gray-400">Sources</div>
                  <div className="text-lg font-bold text-white">{sourcesCount}</div>
                </div>
              )}
            </motion.div>

            {/* View Paper Button */}
            <motion.button
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 1.4 }}
              onClick={onViewPaper}
              className="btn-primary text-lg px-8 py-4 shadow-2xl shadow-primary-500/50"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              📄 View Research Paper
            </motion.button>

            {/* Skip indicator */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 2 }}
              className="mt-6 text-xs text-gray-500"
            >
              Auto-closing in {Math.ceil((intensity.duration - 2000) / 1000)}s...
            </motion.div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

/**
 * Usage Example:
 * 
 * <CelebrationAnimation
 *   qualityScore={8.5}
 *   iterationCount={2}
 *   totalTime="2:34"
 *   totalCost={0.45}
 *   hypothesesCount={5}
 *   experimentsCount={3}
 *   sourcesCount={12}
 *   onComplete={() => console.log("Celebration complete")}
 *   onViewPaper={() => router.push(`/papers/${id}`)}
 *   skipCelebration={false}
 *   enableSound={false}
 * />
 */

