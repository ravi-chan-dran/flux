/**
 * Example: How to use AgentAvatar in Live Theater Page
 * 
 * This file shows how to integrate the new AgentAvatar component
 * into the existing Live Theater page (app/flow/[id]/page.tsx)
 */

import AgentAvatar, { AGENT_CONFIGS } from '@/components/AgentAvatar';

/**
 * EXAMPLE 1: Replace the inline agent cards in the left sidebar
 * 
 * OLD CODE (in app/flow/[id]/page.tsx):
 * 
 * <div className="space-y-4">
 *   {AGENTS.map((agent) => {
 *     const isActive = agent.name === activeAgent;
 *     return (
 *       <div key={agent.name} className={...}>
 *         <div className="text-3xl">{agent.emoji}</div>
 *         <div className="flex-1 min-w-0">
 *           <p className="text-sm">{agent.name}</p>
 *           <p className="text-xs">{agent.role}</p>
 *         </div>
 *       </div>
 *     );
 *   })}
 * </div>
 * 
 * NEW CODE (using AgentAvatar):
 */

export function LeftSidebarWithAgentAvatar({ activeAgent }: { activeAgent: string }) {
  return (
    <aside className="w-1/5 bg-background-light border-r border-gray-800 p-4 overflow-y-auto">
      <h3 className="text-sm font-semibold text-gray-400 mb-4 uppercase">Research Team</h3>
      <div className="space-y-4">
        {Object.values(AGENT_CONFIGS).map((agent) => (
          <AgentAvatar
            key={agent.name}
            agent={agent}
            active={agent.name === activeAgent}
            size="md"
            showLabel={true}
          />
        ))}
      </div>
    </aside>
  );
}

/**
 * EXAMPLE 2: Use in a horizontal agent list
 */

export function HorizontalAgentList({ activeAgent }: { activeAgent: string }) {
  return (
    <div className="flex items-center gap-4 p-4 bg-background-light rounded-lg">
      {Object.values(AGENT_CONFIGS).map((agent) => (
        <AgentAvatar
          key={agent.name}
          agent={agent}
          active={agent.name === activeAgent}
          size="sm"
          showLabel={false}
        />
      ))}
    </div>
  );
}

/**
 * EXAMPLE 3: Large featured agent display
 */

export function FeaturedAgent({ agentName }: { agentName: string }) {
  const agent = AGENT_CONFIGS[agentName];
  
  if (!agent) return null;
  
  return (
    <div className="flex flex-col items-center p-6 bg-background-light rounded-lg">
      <AgentAvatar
        agent={agent}
        active={true}
        size="lg"
        showLabel={true}
      />
      <p className="text-gray-400 text-sm mt-4 text-center max-w-xs">
        {agent.role}
      </p>
    </div>
  );
}

/**
 * EXAMPLE 4: Message card with avatar
 */

export function MessageCardWithAvatar({ 
  message 
}: { 
  message: { agent: string; emoji: string; message: string; timestamp: string } 
}) {
  const agent = AGENT_CONFIGS[message.agent];
  
  if (!agent) {
    // Fallback if agent not found
    return null;
  }
  
  return (
    <div className="card flex items-start gap-4">
      <AgentAvatar
        agent={agent}
        active={false}
        size="sm"
        showLabel={false}
      />
      <div className="flex-1">
        <div className="flex items-center gap-2 mb-2">
          <span className="font-semibold" style={{ color: agent.color }}>
            {agent.name}
          </span>
          <span className="text-xs text-gray-500">
            {new Date(message.timestamp).toLocaleTimeString()}
          </span>
        </div>
        <p className="text-gray-300">{message.message}</p>
      </div>
    </div>
  );
}

/**
 * EXAMPLE 5: Mini agent indicator
 */

export function MiniAgentIndicator({ agentName }: { agentName: string }) {
  const agent = AGENT_CONFIGS[agentName];
  
  if (!agent) return null;
  
  return (
    <div className="inline-flex items-center gap-2 px-3 py-1.5 bg-background-light rounded-full">
      <AgentAvatar
        agent={agent}
        active={true}
        size="sm"
        showLabel={false}
      />
      <span className="text-sm font-medium text-gray-300">{agent.name}</span>
    </div>
  );
}

/**
 * EXAMPLE 6: Agent comparison / selection
 */

export function AgentSelector({ 
  selectedAgent, 
  onSelect 
}: { 
  selectedAgent: string;
  onSelect: (agentName: string) => void;
}) {
  return (
    <div className="grid grid-cols-3 gap-4">
      {Object.values(AGENT_CONFIGS).map((agent) => (
        <button
          key={agent.name}
          onClick={() => onSelect(agent.name)}
          className="p-4 bg-background-light rounded-lg hover:bg-background transition-colors"
        >
          <AgentAvatar
            agent={agent}
            active={agent.name === selectedAgent}
            size="md"
            showLabel={true}
          />
        </button>
      ))}
    </div>
  );
}

/**
 * BENEFITS OF USING AgentAvatar:
 * 
 * 1. ✅ Consistent styling across the app
 * 2. ✅ Built-in animations (glow, pulse, rotate)
 * 3. ✅ Hover tooltips automatically included
 * 4. ✅ Size variants (sm/md/lg) ready to use
 * 5. ✅ Active/inactive states handled
 * 6. ✅ Reusable agent configuration (AGENT_CONFIGS)
 * 7. ✅ Type-safe with TypeScript
 * 8. ✅ Accessible with proper hover states
 * 9. ✅ Smooth Framer Motion animations
 * 10. ✅ Less code duplication
 */

