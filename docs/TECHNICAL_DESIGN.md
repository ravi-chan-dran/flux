# FLUX Technical Design Document

## Table of Contents
1. [Agent System Design](#agent-system-design)
2. [State Management](#state-management)
3. [LangGraph Workflow](#langgraph-workflow)
4. [API Design](#api-design)
5. [Real-Time Streaming](#real-time-streaming)
6. [Storage System](#storage-system)
7. [Error Handling & Resilience](#error-handling--resilience)
8. [Performance Optimization](#performance-optimization)

---

## Agent System Design

### Base Agent Architecture

```python
class BaseAgent(ABC):
    """Abstract base class for all research agents."""
    
    def __init__(self, name: str, role: str, emoji: str, color: str):
        self.name = name           # e.g., "The Current"
        self.role = role           # e.g., "Hypothesis Generator"
        self.emoji = emoji         # e.g., "💡"
        self.color = color         # e.g., "#06B6D4"
        self.bedrock_client = BedrockClient()
        self.system_prompt = self._build_system_prompt()
        self.conversation_history = []
    
    @abstractmethod
    async def execute(self, state: ResearchState) -> ResearchState:
        """Execute agent logic and update state."""
        pass
    
    async def invoke_model(
        self, 
        prompt: str,
        max_tokens: int = 4096,
        temperature: float = 0.7
    ) -> str:
        """Invoke LLM with retry logic."""
        return await self.bedrock_client.invoke(
            prompt=prompt,
            system_prompt=self.system_prompt,
            max_tokens=max_tokens,
            temperature=temperature
        )
```

### Agent Implementations

#### 1. Flow Master Agent
**Responsibility**: Orchestrate the research workflow

```python
class FlowMasterAgent(BaseAgent):
    async def execute(self, state: ResearchState) -> ResearchState:
        # Analyze current state
        hypotheses_count = len(state.get("hypotheses", []))
        sources_count = len(state.get("sources", []))
        experiments_count = len(state.get("experiments", []))
        
        # Determine next action based on state
        if hypotheses_count == 0:
            next_action = "current"  # Generate hypotheses
        elif sources_count == 0:
            next_action = "source"   # Search for research
        elif experiments_count == 0:
            next_action = "channel"  # Design experiments
        else:
            next_action = "filter"   # Quality check
        
        state["next_action"] = next_action
        state["phase"] = self._determine_phase(next_action)
        
        return state
```

#### 2. The Current (Hypothesis Generator)
**Responsibility**: Generate testable hypotheses

```python
class CurrentAgent(BaseAgent):
    async def execute(self, state: ResearchState) -> ResearchState:
        question = state["question"]
        
        # Build prompt for hypothesis generation
        prompt = f"""
        Generate 3-5 testable hypotheses for: {question}
        
        For each hypothesis:
        1. State the hypothesis clearly
        2. Explain the reasoning
        3. Confidence score (0-100)
        4. How to test it
        """
        
        # Invoke LLM
        response = await self.invoke_model(prompt, temperature=0.8)
        
        # Parse response into structured hypotheses
        hypotheses = self._parse_hypotheses(response)
        
        # Update state
        state["hypotheses"] = hypotheses
        state["phase"] = "ideation"
        
        return state
    
    def _parse_hypotheses(self, response: str) -> list[dict]:
        """Parse LLM response into structured hypothesis objects."""
        # Implementation uses regex/JSON parsing
        pass
```

#### 3. The Source (Research Searcher)
**Responsibility**: Search multiple academic sources

```python
class SourceAgent(BaseAgent):
    async def execute(self, state: ResearchState) -> ResearchState:
        question = state["question"]
        hypotheses = state.get("hypotheses", [])
        
        # Multi-source search
        results = await self._multi_source_search(question, hypotheses)
        
        # Synthesize findings
        synthesis = await self._synthesize_sources(results)
        
        # Update state
        state["sources"] = results
        state["synthesis"] = synthesis
        state["phase"] = "research"
        
        return state
    
    async def _multi_source_search(
        self, 
        question: str, 
        hypotheses: list
    ) -> list[dict]:
        """Search Semantic Scholar, ArXiv, and Tavily in parallel."""
        tasks = [
            search_semantic_scholar(question),
            search_arxiv(question),
            search_tavily(question)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Combine and deduplicate
        combined = self._combine_and_dedupe(results)
        
        return combined[:20]  # Top 20 sources
```

#### 4. The Channel (Experiment Designer)
**Responsibility**: Design experiments to test hypotheses

```python
class ChannelAgent(BaseAgent):
    async def execute(self, state: ResearchState) -> ResearchState:
        hypotheses = state.get("hypotheses", [])
        sources = state.get("sources", [])
        
        experiments = []
        
        for hypothesis in hypotheses:
            # Design experiment for each hypothesis
            experiment = await self._design_experiment(
                hypothesis, 
                sources
            )
            experiments.append(experiment)
        
        state["experiments"] = experiments
        state["phase"] = "design"
        
        return state
    
    async def _design_experiment(
        self, 
        hypothesis: dict,
        sources: list
    ) -> dict:
        """Design a single experiment."""
        prompt = f"""
        Design an experiment to test: {hypothesis['text']}
        
        Available research context:
        {self._format_sources(sources)}
        
        Provide:
        1. Experimental method
        2. Measurements to collect
        3. Success criteria
        4. Time/resource estimate
        5. Potential issues
        """
        
        response = await self.invoke_model(prompt)
        
        return self._parse_experiment(response, hypothesis['id'])
```

#### 5. The Filter (Quality Critic)
**Responsibility**: Evaluate research quality and decide iteration

```python
class FilterAgent(BaseAgent):
    async def execute(self, state: ResearchState) -> ResearchState:
        # Evaluate quality
        critique = await self._evaluate_quality(state)
        
        # Update state
        state["critiques"].append(critique)
        state["quality_score"] = critique["quality_score"]
        state["quality_history"].append(critique["quality_score"])
        
        # Decision: iterate or complete?
        should_iterate = should_continue_iteration(state)
        state["should_iterate"] = should_iterate
        
        if not should_iterate:
            state["stop_reason"] = self._determine_stop_reason(state)
        
        state["phase"] = "critique"
        
        return state
    
    async def _evaluate_quality(self, state: ResearchState) -> dict:
        """Comprehensive quality evaluation."""
        prompt = f"""
        Evaluate the research quality (0-10):
        
        Question: {state['question']}
        Hypotheses: {len(state['hypotheses'])}
        Sources: {len(state['sources'])}
        Experiments: {len(state['experiments'])}
        
        Iteration: {state['iteration']}
        
        Rate:
        1. Hypothesis quality
        2. Source relevance
        3. Experimental design
        4. Overall coherence
        5. Completeness
        
        Provide:
        - Overall score (0-10)
        - Issues found
        - Strengths
        - Recommendations
        """
        
        response = await self.invoke_model(prompt, temperature=0.3)
        
        return self._parse_critique(response)
```

#### 6. The Confluence (Paper Synthesizer)
**Responsibility**: Synthesize comprehensive research paper

```python
class ConfluenceAgent(BaseAgent):
    async def execute(self, state: ResearchState) -> ResearchState:
        # Write comprehensive paper
        paper = await self.write_paper(state)
        
        # Update state
        state["paper_draft"] = paper
        state["phase"] = "complete"
        state["stop_reason"] = "paper_complete"
        
        return state
    
    async def write_paper(self, state: ResearchState) -> str:
        """Generate full research paper."""
        prompt = self._build_writing_prompt(
            question=state["question"],
            hypotheses=state["hypotheses"],
            sources=state["sources"],
            experiments=state["experiments"],
            critiques=state["critiques"],
            quality_score=state["quality_score"]
        )
        
        # Long-form generation
        paper = await self.invoke_model(
            prompt, 
            max_tokens=8000,
            temperature=0.7
        )
        
        # Ensure proper structure
        if not self._has_required_sections(paper):
            paper = self._add_missing_sections(paper, state)
        
        return paper
```

---

## State Management

### ResearchState Type Definition

```python
from typing import TypedDict, NotRequired

class ResearchState(TypedDict):
    # Identity
    question: str
    research_id: str
    
    # Iteration Control
    iteration: int
    max_iterations: int
    quality_score: float
    quality_threshold: float
    quality_history: list[float]
    improvement_threshold: float
    
    # Flow Control
    phase: str  # "ideation", "research", "design", "critique", "complete"
    next_action: str  # "current", "source", "channel", "filter", "confluence"
    should_iterate: bool
    stop_reason: str
    
    # Research Data
    hypotheses: list[dict]
    sources: list[dict]
    experiments: list[dict]
    critiques: list[dict]
    paper_draft: str
    
    # Communication
    messages: list[dict]
    
    # Metadata
    started_at: str
    total_tokens_used: int
    total_cost: float
```

### State Evolution Functions

```python
def should_continue_iteration(state: ResearchState) -> bool:
    """Determine if another iteration is needed."""
    
    # Check iteration limit
    if state["iteration"] >= state["max_iterations"]:
        state["stop_reason"] = "max_iterations_reached"
        return False
    
    # Check quality threshold
    quality_score = state["quality_score"]
    quality_threshold = state["quality_threshold"]
    
    if quality_score >= quality_threshold:
        state["stop_reason"] = "quality_threshold_met"
        return False
    
    # Check improvement
    quality_history = state["quality_history"]
    if len(quality_history) >= 2:
        improvement = quality_history[-1] - quality_history[-2]
        improvement_threshold = state["improvement_threshold"]
        
        if improvement < improvement_threshold:
            state["stop_reason"] = "insufficient_improvement"
            return False
    
    # Continue iteration
    return True

def update_quality_score(state: ResearchState, new_score: float) -> ResearchState:
    """Update quality tracking."""
    state["quality_score"] = new_score
    state["quality_history"].append(new_score)
    return state
```

---

## LangGraph Workflow

### Graph Definition

```python
from langgraph.graph import StateGraph, END

def create_research_graph() -> StateGraph:
    """Build the orbital research workflow."""
    
    # Create state graph
    workflow = StateGraph(ResearchState)
    
    # Add agent nodes
    workflow.add_node("flow_master", flow_master_node)
    workflow.add_node("current", current_node)
    workflow.add_node("source", source_node)
    workflow.add_node("channel", channel_node)
    workflow.add_node("filter", filter_node)
    workflow.add_node("confluence", confluence_node)
    
    # Set entry point
    workflow.set_entry_point("flow_master")
    
    # Conditional routing from Flow Master
    workflow.add_conditional_edges(
        "flow_master",
        route_from_flow_master,
        {
            "current": "current",
            "source": "source",
            "channel": "channel",
            "filter": "filter",
            "confluence": "confluence",
        }
    )
    
    # All agents return to Flow Master (orbital)
    workflow.add_edge("current", "flow_master")
    workflow.add_edge("source", "flow_master")
    workflow.add_edge("channel", "flow_master")
    
    # Filter decides: iterate or finish
    workflow.add_conditional_edges(
        "filter",
        route_from_filter,
        {
            "flow_master": "flow_master",  # Another orbit
            "confluence": "confluence",     # Finish
        }
    )
    
    # Confluence completes the research
    workflow.add_edge("confluence", END)
    
    # Compile
    return workflow.compile()
```

### Node Wrappers

```python
async def flow_master_node(state: ResearchState) -> ResearchState:
    """Flow Master node wrapper."""
    logger.info("🧑‍💼 Flow Master analyzing state")
    
    result = await flow_master.execute(state)
    
    # Add message to state
    result["messages"].append(
        flow_master.format_message(
            f"Next action: {result['next_action']}",
            message_type="routing"
        )
    )
    
    return result

async def current_node(state: ResearchState) -> ResearchState:
    """The Current node wrapper."""
    logger.info("💡 The Current generating hypotheses")
    
    result = await current_agent.execute(state)
    
    # Add message
    hypotheses_count = len(result.get("hypotheses", []))
    result["messages"].append(
        current_agent.format_message(
            f"Generated {hypotheses_count} hypotheses",
            message_type="hypotheses",
            metadata={"count": hypotheses_count}
        )
    )
    
    return result
```

### Routing Functions

```python
def route_from_flow_master(
    state: ResearchState
) -> Literal["current", "source", "channel", "filter", "confluence"]:
    """Route from Flow Master based on state."""
    next_action = state.get("next_action", "current")
    
    valid_actions = ["current", "source", "channel", "filter", "confluence"]
    if next_action not in valid_actions:
        logger.warning(f"Invalid next_action '{next_action}', defaulting to 'filter'")
        return "filter"
    
    return next_action

def route_from_filter(
    state: ResearchState
) -> Literal["flow_master", "confluence"]:
    """Route from Filter: iterate or finish."""
    should_iterate = state.get("should_iterate", False)
    
    if should_iterate:
        # Increment iteration counter
        state["iteration"] += 1
        return "flow_master"
    else:
        return "confluence"
```

---

## API Design

### Endpoint Specifications

#### POST /api/research/start
**Purpose**: Initiate a new research session

**Request:**
```json
{
  "question": "What are the latest advances in quantum computing?",
  "max_iterations": 1,
  "quality_threshold": 8.0,
  "improvement_threshold": 0.5
}
```

**Response:**
```json
{
  "research_id": "research-abc123",
  "question": "What are the latest advances in quantum computing?",
  "status": "started",
  "message": "Research started successfully"
}
```

**Implementation:**
```python
@app.post("/api/research/start")
async def start_research(request: ResearchRequest):
    # Generate unique ID
    research_id = f"research-{uuid.uuid4().hex[:12]}"
    
    # Start background task
    background_tasks.add_task(
        run_research_background,
        research_id=research_id,
        question=request.question,
        max_iterations=request.max_iterations,
        quality_threshold=request.quality_threshold,
        improvement_threshold=request.improvement_threshold
    )
    
    return ResearchResponse(
        research_id=research_id,
        question=request.question,
        status="started",
        message="Research started successfully"
    )
```

#### GET /api/research/{research_id}/stream
**Purpose**: Stream research progress in real-time

**Response**: Server-Sent Events (SSE)
```
event: connected
data: {"research_id": "research-abc123", "message": "Connected to stream"}

event: agent_message
data: {"agent": "The Current", "emoji": "💡", "message": "Generated 3 hypotheses", ...}

event: iteration_complete
data: {"iteration": 0, "quality_score": 7.5, ...}

event: complete
data: {"research_id": "research-abc123", "stop_reason": "quality_threshold_met", ...}
```

**Implementation:**
```python
@app.get("/api/research/{research_id}/stream")
async def stream_research_progress(
    research_id: str,
    question: str = Query(..., description="Research question")
):
    async def event_generator():
        try:
            # Send connection confirmation
            yield {
                "event": "connected",
                "data": json.dumps({
                    "research_id": research_id,
                    "message": "Connected to stream"
                })
            }
            
            # Stream research execution
            async for event in stream_research(
                question=question,
                research_id=research_id,
                max_iterations=int(os.getenv("MAX_ITERATIONS", "1")),
                quality_threshold=float(os.getenv("QUALITY_THRESHOLD", "8.0")),
                improvement_threshold=float(os.getenv("IMPROVEMENT_THRESHOLD", "0.5"))
            ):
                yield {
                    "event": event["event_type"],
                    "data": json.dumps(event)
                }
                
                # Ping to keep connection alive
                await asyncio.sleep(0.1)
        
        except Exception as e:
            logger.error(f"Stream error: {e}")
            yield {
                "event": "error",
                "data": json.dumps({"error": str(e)})
            }
    
    return EventSourceResponse(event_generator())
```

#### GET /api/research/{research_id}/paper
**Purpose**: Retrieve completed research paper

**Response:**
```json
{
  "research_id": "research-abc123",
  "paper": "# Research Paper: Quantum Computing Advances\n\n## Abstract\n...",
  "metadata": {
    "question": "What are the latest advances in quantum computing?",
    "started_at": "2025-10-19T01:00:00Z",
    "completed_at": "2025-10-19T01:01:30Z",
    "total_iterations": 1,
    "final_quality_score": 8.5,
    "quality_history": [8.5],
    "stop_reason": "quality_threshold_met",
    "total_tokens_used": 12345,
    "total_cost": 0.0567
  },
  "conversation": [...],
  "state": {...}
}
```

**Implementation:**
```python
@app.get("/api/research/{research_id}/paper")
async def get_paper(research_id: str):
    try:
        # Load from storage
        paper_data = await load_paper(research_id)
        
        if not paper_data:
            raise HTTPException(
                status_code=404,
                detail=f"Research {research_id} not found"
            )
        
        return paper_data
    
    except StorageError as e:
        logger.error(f"Failed to load paper: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

#### GET /api/research/list
**Purpose**: List all completed research papers

**Response:**
```json
{
  "papers": [
    {
      "research_id": "research-abc123",
      "question": "What are the latest advances in quantum computing?",
      "completed_at": "2025-10-19T01:01:30Z",
      "quality_score": 8.5,
      "iterations": 1,
      "stop_reason": "quality_threshold_met",
      "sources_count": 15
    }
  ],
  "count": 1,
  "storage_info": {
    "storage_path": "/path/to/storage/papers",
    "paper_count": 1,
    "total_size_bytes": 51200,
    "total_size_mb": 0.05
  }
}
```

---

## Real-Time Streaming

### Frontend SSE Hook

```typescript
export function useResearchStream(researchId: string, question: string) {
  const [messages, setMessages] = useState<AgentMessage[]>([]);
  const [currentPhase, setCurrentPhase] = useState<string>('initialize');
  const [activeAgent, setActiveAgent] = useState<string>('');
  const [iteration, setIteration] = useState(0);
  const [qualityScore, setQualityScore] = useState(0);
  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>('connecting');
  const [error, setError] = useState<string | null>(null);
  
  const eventSourceRef = useRef<EventSource | null>(null);
  const callbacksRef = useRef({ onComplete, onError });
  
  const connect = useCallback(() => {
    const url = `${API_URL}/api/research/${researchId}/stream?question=${encodeURIComponent(question)}`;
    
    const es = new EventSource(url);
    eventSourceRef.current = es;
    
    es.onopen = () => {
      setConnectionStatus('connected');
    };
    
    es.addEventListener('agent_message', (e) => {
      const data = JSON.parse(e.data);
      setMessages(prev => [...prev, data]);
      setActiveAgent(data.agent || '');
      setCurrentPhase(data.phase || prev);
      setQualityScore(data.quality_score || 0);
    });
    
    es.addEventListener('complete', (e) => {
      const data = JSON.parse(e.data);
      setConnectionStatus('complete');
      callbacksRef.current?.onComplete?.(data);
    });
    
    es.onerror = () => {
      es.close();
      setConnectionStatus('error');
      // Implement reconnection logic
    };
    
  }, [researchId, question]);
  
  useEffect(() => {
    connect();
    return () => {
      eventSourceRef.current?.close();
    };
  }, [connect]);
  
  return {
    messages,
    currentPhase,
    activeAgent,
    iteration,
    qualityScore,
    connectionStatus,
    error,
    reconnect: connect
  };
}
```

### Reconnection Strategy

```typescript
// Exponential backoff
const reconnectDelays = [1000, 2000, 4000, 8000, 16000, 30000];

function attemptReconnect(attemptNumber: number) {
  if (attemptNumber >= maxReconnectAttempts) {
    setConnectionStatus('error');
    setError('Max reconnection attempts exceeded');
    return;
  }
  
  const delay = reconnectDelays[Math.min(attemptNumber, reconnectDelays.length - 1)];
  
  setTimeout(() => {
    logger.info(`Reconnection attempt ${attemptNumber + 1}/${maxReconnectAttempts}`);
    connect();
  }, delay);
}
```

---

## Storage System

### File Structure

```
backend/storage/papers/{research_id}/
├── paper.md              # Final research paper (Markdown)
├── metadata.json         # Research metadata
├── conversation.json     # Full agent conversation
└── state.json            # Complete research state
```

### Storage Operations

```python
async def save_paper(research_id: str, state: dict) -> dict[str, Path]:
    """Save research paper and metadata."""
    
    # Create research directory
    research_dir = PAPERS_DIR / research_id
    research_dir.mkdir(parents=True, exist_ok=True)
    
    # Prepare file paths
    paper_path = research_dir / "paper.md"
    metadata_path = research_dir / "metadata.json"
    conversation_path = research_dir / "conversation.json"
    state_path = research_dir / "state.json"
    
    # Extract data
    paper_content = state.get("paper_draft", "")
    messages = state.get("messages", [])
    
    # Create metadata
    metadata = {
        "research_id": research_id,
        "question": state.get("question", ""),
        "started_at": state.get("started_at"),
        "completed_at": datetime.utcnow().isoformat(),
        "total_iterations": state.get("iteration", 0) + 1,
        "final_quality_score": state.get("quality_score", 0.0),
        "quality_history": state.get("quality_history", []),
        "stop_reason": state.get("stop_reason", ""),
        "total_tokens_used": state.get("total_tokens_used", 0),
        "total_cost": state.get("total_cost", 0.0),
    }
    
    # Save files (async)
    async with aiofiles.open(paper_path, "w", encoding="utf-8") as f:
        await f.write(paper_content)
    
    async with aiofiles.open(metadata_path, "w", encoding="utf-8") as f:
        await f.write(json.dumps(metadata, indent=2, ensure_ascii=False))
    
    async with aiofiles.open(conversation_path, "w", encoding="utf-8") as f:
        await f.write(json.dumps(messages, indent=2, ensure_ascii=False))
    
    async with aiofiles.open(state_path, "w", encoding="utf-8") as f:
        await f.write(json.dumps(state, indent=2, ensure_ascii=False, default=str))
    
    logger.info(f"Saved research {research_id}")
    
    return {
        "paper": paper_path,
        "metadata": metadata_path,
        "conversation": conversation_path,
        "state": state_path,
    }
```

---

## Error Handling & Resilience

### Retry Logic with Exponential Backoff

```python
def invoke(self, prompt: str, max_retries: int = 5) -> str:
    """Invoke with automatic retry on throttling."""
    
    for attempt in range(max_retries):
        try:
            response = self.client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(request_body)
            )
            
            # Success
            return self._parse_response(response)
        
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            
            if error_code == "ThrottlingException" and attempt < max_retries - 1:
                delay = 2 ** (attempt + 1)  # 2, 4, 8, 16, 32 seconds
                logger.warning(f"Throttled. Retrying in {delay}s...")
                time.sleep(delay)
                continue
            
            # Not throttling or last attempt
            raise BedrockClientError(f"AWS Error: {e}") from e
    
    raise BedrockClientError("Max retries exceeded")
```

### Agent Invocation Delays

```python
async def stream_research(question: str, research_id: str, **config):
    """Stream research with rate limiting."""
    
    # Get delay from environment
    agent_delay = float(os.getenv("AGENT_INVOCATION_DELAY", "2"))
    
    async for state_update in graph.astream(state):
        for node_name, updated_state in state_update.items():
            # Yield agent event
            yield event
            
            # Rate limiting: delay between agents
            if node_name != "flow_master" and agent_delay > 0:
                await asyncio.sleep(agent_delay)
```

### Graceful Degradation

```python
async def _multi_source_search(self, question: str) -> list[dict]:
    """Search with graceful degradation."""
    
    tasks = [
        search_semantic_scholar(question),
        search_arxiv(question),
        search_tavily(question)
    ]
    
    # Use gather with return_exceptions
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Filter out exceptions, use successful results
    valid_results = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            logger.warning(f"Search {i} failed: {result}")
        else:
            valid_results.extend(result)
    
    # Return what we have, even if partial
    return valid_results
```

---

## Performance Optimization

### AWS Bedrock Token Usage Tracking

```python
class BedrockClient:
    def __init__(self):
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cost = 0.0
    
    def invoke(self, prompt: str) -> str:
        response = self.client.invoke_model(...)
        response_body = json.loads(response["body"].read())
        
        # Track usage
        usage = response_body.get("usage", {})
        input_tokens = usage.get("input_tokens", 0)
        output_tokens = usage.get("output_tokens", 0)
        
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens
        
        # Calculate cost (Claude 3.5 Sonnet pricing)
        input_cost = (input_tokens / 1000) * 0.003   # $3 per 1M tokens
        output_cost = (output_tokens / 1000) * 0.015  # $15 per 1M tokens
        self.total_cost += input_cost + output_cost
        
        logger.info(f"Tokens: {input_tokens} in, {output_tokens} out")
        logger.info(f"Cost: ${input_cost + output_cost:.4f}")
        
        return text
```

### Caching Strategy (Future)

```python
from functools import lru_cache
import hashlib

@lru_cache(maxsize=100)
async def cached_search(query_hash: str) -> list[dict]:
    """Cache search results by query hash."""
    # Implementation
    pass

def search_with_cache(query: str) -> list[dict]:
    query_hash = hashlib.sha256(query.encode()).hexdigest()
    return await cached_search(query_hash)
```

### Parallel Execution

```python
async def execute_agents_parallel(state: ResearchState) -> ResearchState:
    """Execute independent agents in parallel (future optimization)."""
    
    # These agents don't depend on each other
    current_task = current_agent.execute(state)
    source_task = source_agent.execute(state)
    
    # Run in parallel
    current_result, source_result = await asyncio.gather(
        current_task,
        source_task
    )
    
    # Merge results
    state.update(current_result)
    state.update(source_result)
    
    return state
```

---

## Configuration Management

### Environment Variables

```bash
# AWS Configuration
AWS_PROFILE=default
AWS_REGION=us-east-1
AWS_BEDROCK_MODEL_ID=us.anthropic.claude-3-5-sonnet-20241022-v2:0

# Research Configuration
MAX_ITERATIONS=1
QUALITY_THRESHOLD=8.0
IMPROVEMENT_THRESHOLD=0.5

# Rate Limiting
AGENT_INVOCATION_DELAY=2

# Logging
LOG_LEVEL=INFO
```

### Dynamic Configuration

```python
class Config:
    """Centralized configuration management."""
    
    def __init__(self):
        load_dotenv()
        
        self.aws_profile = os.getenv("AWS_PROFILE", "default")
        self.aws_region = os.getenv("AWS_REGION", "us-east-1")
        self.model_id = os.getenv("AWS_BEDROCK_MODEL_ID")
        
        self.max_iterations = int(os.getenv("MAX_ITERATIONS", "1"))
        self.quality_threshold = float(os.getenv("QUALITY_THRESHOLD", "8.0"))
        self.improvement_threshold = float(os.getenv("IMPROVEMENT_THRESHOLD", "0.5"))
        
        self.agent_delay = float(os.getenv("AGENT_INVOCATION_DELAY", "2"))
        
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
    
    def validate(self):
        """Validate configuration."""
        assert self.max_iterations > 0, "MAX_ITERATIONS must be positive"
        assert 0 <= self.quality_threshold <= 10, "QUALITY_THRESHOLD must be 0-10"
        assert self.agent_delay >= 0, "AGENT_INVOCATION_DELAY must be non-negative"

config = Config()
config.validate()
```

---

## Conclusion

This technical design document provides the low-level implementation details for the FLUX research system. Key technical highlights:

1. **Agent Pattern**: Clean separation of concerns with abstract base class
2. **State Management**: Type-safe state evolution through LangGraph
3. **API Design**: RESTful endpoints with SSE for real-time updates
4. **Error Handling**: Comprehensive retry logic and graceful degradation
5. **Performance**: Token tracking, caching strategy, and parallel execution
6. **Configuration**: Environment-based configuration management

The system is built with production-readiness in mind, emphasizing reliability, observability, and maintainability.

