"use client";

import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useRouter } from "next/navigation";

/**
 * Connection status types
 */
export type ConnectionStatusType =
  | "connecting"
  | "connected"
  | "reconnecting"
  | "error"
  | "complete";

/**
 * Connection quality indicator
 */
type ConnectionQuality = "good" | "slow" | "poor";

/**
 * ConnectionStatus Props
 */
interface ConnectionStatusProps {
  status: ConnectionStatusType;
  error?: Error | null;
  onRetry?: () => void;
  connectionQuality?: ConnectionQuality;
}

/**
 * ConnectionStatus Component
 * 
 * Overlay component for handling SSE connection states:
 * - connecting: Centered spinner
 * - connected: Transparent (shows quality indicator only)
 * - reconnecting: Top banner (dismissible)
 * - error: Centered error card with retry
 * - complete: Celebration animation
 * 
 * Features:
 * - Smooth animations (Framer Motion)
 * - Connection quality indicator
 * - Accessibility (keyboard focus)
 * - Event logging
 * - Non-intrusive when connected
 */
export default function ConnectionStatus({
  status,
  error,
  onRetry,
  connectionQuality = "good",
}: ConnectionStatusProps) {
  const router = useRouter();
  const [isDismissed, setIsDismissed] = useState(false);
  const [showCelebration, setShowCelebration] = useState(false);

  // Log connection events
  useEffect(() => {
    const timestamp = new Date().toISOString();
    console.log(`[${timestamp}] Connection Status: ${status}`, {
      error: error?.message,
      quality: connectionQuality,
    });
  }, [status, error, connectionQuality]);

  // Handle completion animation
  useEffect(() => {
    if (status === "complete") {
      setShowCelebration(true);
      const timer = setTimeout(() => {
        setShowCelebration(false);
      }, 3000);
      return () => clearTimeout(timer);
    }
  }, [status]);

  // Reset dismissal when status changes to reconnecting
  useEffect(() => {
    if (status === "reconnecting") {
      setIsDismissed(false);
    }
  }, [status]);

  return (
    <>
      {/* Connection Quality Indicator (top corner, always visible when connected) */}
      <AnimatePresence>
        {status === "connected" && (
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 20 }}
            className="fixed top-20 right-6 z-40"
          >
            <div className="flex items-center gap-2 px-3 py-2 bg-background-light/90 backdrop-blur-sm rounded-full border border-gray-700 shadow-lg">
              <motion.div
                className={`w-2 h-2 rounded-full ${
                  connectionQuality === "good"
                    ? "bg-green-500"
                    : connectionQuality === "slow"
                    ? "bg-yellow-500"
                    : "bg-red-500"
                }`}
                animate={{
                  scale: [1, 1.2, 1],
                  opacity: [1, 0.8, 1],
                }}
                transition={{
                  duration: 2,
                  repeat: Infinity,
                }}
              />
              <span className="text-xs text-gray-400">
                {connectionQuality === "good"
                  ? "Connected"
                  : connectionQuality === "slow"
                  ? "Slow"
                  : "Unstable"}
              </span>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Connecting Overlay */}
      <AnimatePresence>
        {status === "connecting" && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-background/95 backdrop-blur-sm z-50 flex items-center justify-center"
          >
            <div className="text-center">
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                className="inline-block w-16 h-16 border-4 border-gray-700 border-t-primary-500 rounded-full mb-6"
              />
              <p className="text-xl text-gray-300">Connecting to research stream...</p>
              <p className="text-sm text-gray-500 mt-2">
                Establishing secure connection
              </p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Reconnecting Banner */}
      <AnimatePresence>
        {status === "reconnecting" && !isDismissed && (
          <motion.div
            initial={{ y: -100, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            exit={{ y: -100, opacity: 0 }}
            className="fixed top-16 left-1/2 transform -translate-x-1/2 z-50 w-full max-w-md"
          >
            <div className="mx-4 bg-yellow-500/20 backdrop-blur-sm border border-yellow-500/50 rounded-lg p-4 shadow-lg">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <motion.div
                    animate={{ rotate: 360 }}
                    transition={{
                      duration: 1,
                      repeat: Infinity,
                      ease: "linear",
                    }}
                    className="w-5 h-5 border-2 border-yellow-500 border-t-transparent rounded-full"
                  />
                  <div>
                    <p className="text-sm font-semibold text-yellow-400">
                      Connection lost
                    </p>
                    <p className="text-xs text-yellow-300">
                      Reconnecting automatically...
                    </p>
                  </div>
                </div>
                <button
                  onClick={() => setIsDismissed(true)}
                  className="text-yellow-400 hover:text-yellow-300 transition-colors"
                  aria-label="Dismiss reconnection banner"
                >
                  ✕
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Error Overlay */}
      <AnimatePresence>
        {status === "error" && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-background/95 backdrop-blur-sm z-50 flex items-center justify-center p-6"
          >
            <motion.div
              initial={{ scale: 0.9, y: 20 }}
              animate={{ scale: 1, y: 0 }}
              exit={{ scale: 0.9, y: 20 }}
              className="card max-w-lg w-full bg-background-light border-red-500/50"
              role="dialog"
              aria-labelledby="error-title"
              aria-describedby="error-description"
            >
              {/* Error Icon */}
              <div className="flex justify-center mb-6">
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ delay: 0.1, type: "spring" }}
                  className="w-16 h-16 rounded-full bg-red-500/20 flex items-center justify-center"
                >
                  <span className="text-4xl">⚠️</span>
                </motion.div>
              </div>

              {/* Error Title */}
              <h2
                id="error-title"
                className="text-2xl font-bold text-red-400 text-center mb-3"
              >
                Connection Error
              </h2>

              {/* Error Message */}
              <p
                id="error-description"
                className="text-gray-300 text-center mb-6"
              >
                {error?.message || "Failed to connect to the research stream."}
              </p>

              {/* Error Details (if available) */}
              {error && error.message !== "Research not found" && (
                <details className="mb-6 p-3 bg-background/50 rounded-lg">
                  <summary className="text-xs text-gray-500 cursor-pointer hover:text-gray-400">
                    Technical Details
                  </summary>
                  <pre className="mt-2 text-xs text-gray-400 overflow-auto">
                    {error.stack || error.toString()}
                  </pre>
                </details>
              )}

              {/* Action Buttons */}
              <div className="flex gap-3">
                <button
                  onClick={() => router.push("/")}
                  className="flex-1 px-4 py-3 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors"
                  autoFocus
                >
                  ← Go Back
                </button>
                {onRetry && error?.message !== "Research not found" && (
                  <button
                    onClick={onRetry}
                    className="flex-1 px-4 py-3 btn-primary"
                  >
                    🔄 Retry Connection
                  </button>
                )}
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Celebration Overlay */}
      <AnimatePresence>
        {showCelebration && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center pointer-events-none"
          >
            <motion.div
              initial={{ scale: 0, rotate: -180 }}
              animate={{ scale: 1, rotate: 0 }}
              exit={{ scale: 0, rotate: 180 }}
              transition={{ type: "spring", duration: 0.6 }}
              className="text-center"
            >
              <motion.div
                animate={{
                  y: [0, -20, 0],
                }}
                transition={{
                  duration: 0.6,
                  repeat: 3,
                }}
                className="text-8xl mb-4"
              >
                🎉
              </motion.div>
              <motion.h2
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                className="text-4xl font-bold text-primary-400"
              >
                Research Complete!
              </motion.h2>
            </motion.div>

            {/* Confetti Effect */}
            {[...Array(20)].map((_, i) => (
              <motion.div
                key={i}
                className="absolute w-3 h-3 rounded-full"
                style={{
                  backgroundColor: [
                    "#06B6D4",
                    "#9D4EDD",
                    "#FFA500",
                    "#14B8A6",
                    "#EF4444",
                    "#6366F1",
                  ][i % 6],
                  left: `${Math.random() * 100}%`,
                  top: `${Math.random() * 100}%`,
                }}
                animate={{
                  y: [0, -50, 100, 200],
                  x: [(Math.random() - 0.5) * 100],
                  rotate: [0, 360],
                  opacity: [1, 1, 0],
                }}
                transition={{
                  duration: 2,
                  delay: Math.random() * 0.3,
                }}
              />
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}

/**
 * Usage Example:
 * 
 * <ConnectionStatus
 *   status={connectionStatus}
 *   error={error}
 *   onRetry={reconnect}
 *   connectionQuality="good"
 * />
 */

