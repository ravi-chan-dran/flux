"use client";

import { motion } from "framer-motion";
import { useState } from "react";

/**
 * Agent configuration type
 */
export interface AgentConfig {
  name: string;
  emoji: string;
  color: string;
  role: string;
}

/**
 * All 6 FLUX agents with their configurations
 */
export const AGENT_CONFIGS: Record<string, AgentConfig> = {
  "The Flow Master": {
    name: "The Flow Master",
    emoji: "🧑‍💼",
    color: "#9D4EDD", // purple
    role: "Research Orchestrator",
  },
  "The Current": {
    name: "The Current",
    emoji: "💡",
    color: "#00D9FF", // cyan
    role: "Hypothesis Generator",
  },
  "The Source": {
    name: "The Source",
    emoji: "📚",
    color: "#FFA500", // amber
    role: "Knowledge Searcher",
  },
  "The Channel": {
    name: "The Channel",
    emoji: "🔬",
    color: "#06FFA5", // teal
    role: "Experiment Designer",
  },
  "The Filter": {
    name: "The Filter",
    emoji: "🛡️",
    color: "#FF4444", // red
    role: "Quality Critic",
  },
  "The Confluence": {
    name: "The Confluence",
    emoji: "✍️",
    color: "#6366F1", // indigo
    role: "Research Synthesizer",
  },
};

/**
 * Size variants for the avatar
 */
const SIZE_VARIANTS = {
  sm: {
    container: 32,
    emoji: "text-base",
    label: "text-xs",
  },
  md: {
    container: 48,
    emoji: "text-2xl",
    label: "text-sm",
  },
  lg: {
    container: 64,
    emoji: "text-4xl",
    label: "text-base",
  },
};

/**
 * AgentAvatar Props
 */
interface AgentAvatarProps {
  agent: AgentConfig;
  active?: boolean;
  size?: "sm" | "md" | "lg";
  showLabel?: boolean;
  className?: string;
}

/**
 * Animated Agent Avatar Component
 *
 * Features:
 * - Circular avatar with agent emoji
 * - Active state with pulsing glow and rotating ring
 * - Hover tooltip
 * - Optional label
 * - Size variants (sm/md/lg)
 * - Smooth Framer Motion animations
 */
export default function AgentAvatar({
  agent,
  active = false,
  size = "md",
  showLabel = false,
  className = "",
}: AgentAvatarProps) {
  const [isHovered, setIsHovered] = useState(false);
  const sizeConfig = SIZE_VARIANTS[size];

  return (
    <div className={`flex flex-col items-center gap-2 ${className}`}>
      {/* Avatar Container */}
      <div className="relative group">
        {/* Rotating Ring (Active Only) */}
        {active && (
          <motion.div
            className="absolute inset-0 rounded-full"
            style={{
              border: `2px solid ${agent.color}`,
              width: sizeConfig.container + 8,
              height: sizeConfig.container + 8,
              top: -4,
              left: -4,
            }}
            animate={{
              rotate: 360,
              scale: [1, 1.05, 1],
            }}
            transition={{
              rotate: {
                duration: 3,
                repeat: Infinity,
                ease: "linear",
              },
              scale: {
                duration: 2,
                repeat: Infinity,
                ease: "easeInOut",
              },
            }}
          />
        )}

        {/* Main Avatar Circle */}
        <motion.div
          className="relative flex items-center justify-center rounded-full cursor-pointer overflow-hidden"
          style={{
            width: sizeConfig.container,
            height: sizeConfig.container,
            backgroundColor: active ? `${agent.color}40` : `${agent.color}20`,
          }}
          animate={{
            scale: active ? 1.1 : 1,
            opacity: active ? 1 : 0.7,
            filter: active ? "grayscale(0%)" : "grayscale(30%)",
          }}
          whileHover={{
            scale: active ? 1.15 : 1.05,
            opacity: 1,
            filter: "grayscale(0%)",
          }}
          transition={{
            duration: 0.3,
            ease: "easeOut",
          }}
          onHoverStart={() => setIsHovered(true)}
          onHoverEnd={() => setIsHovered(false)}
        >
          {/* Pulsing Glow Effect (Active Only) */}
          {active && (
            <motion.div
              className="absolute inset-0 rounded-full"
              style={{
                boxShadow: `0 0 20px ${agent.color}, 0 0 40px ${agent.color}80`,
              }}
              animate={{
                opacity: [0.5, 1, 0.5],
              }}
              transition={{
                duration: 2,
                repeat: Infinity,
                ease: "easeInOut",
              }}
            />
          )}

          {/* Emoji */}
          <span className={`relative z-10 ${sizeConfig.emoji}`}>
            {agent.emoji}
          </span>
        </motion.div>

        {/* Hover Tooltip */}
        {isHovered && (
          <motion.div
            className="absolute z-50 px-3 py-2 bg-gray-900 border rounded-lg shadow-xl pointer-events-none"
            style={{
              borderColor: agent.color,
              top: sizeConfig.container + 8,
              left: "50%",
              transform: "translateX(-50%)",
              minWidth: "max-content",
            }}
            initial={{ opacity: 0, y: -5 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -5 }}
            transition={{ duration: 0.2 }}
          >
            <div className="text-white text-sm font-semibold mb-1">
              {agent.name}
            </div>
            <div className="text-gray-400 text-xs">{agent.role}</div>
            {/* Tooltip Arrow */}
            <div
              className="absolute w-2 h-2 bg-gray-900 border-t border-l transform rotate-45"
              style={{
                borderColor: agent.color,
                top: -5,
                left: "50%",
                marginLeft: -4,
              }}
            />
          </motion.div>
        )}
      </div>

      {/* Label (Optional) */}
      {showLabel && (
        <motion.div
          className={`text-center ${sizeConfig.label} font-medium transition-colors`}
          style={{
            color: active ? agent.color : "#9CA3AF",
          }}
          animate={{
            opacity: active ? 1 : 0.7,
          }}
        >
          {agent.name}
        </motion.div>
      )}
    </div>
  );
}

/**
 * Example usage:
 *
 * import AgentAvatar, { AGENT_CONFIGS } from '@/components/AgentAvatar';
 *
 * <AgentAvatar
 *   agent={AGENT_CONFIGS["The Flow Master"]}
 *   active={true}
 *   size="md"
 *   showLabel={true}
 * />
 */

