# FLUX Sequence Diagrams

## Table of Contents
1. [Complete Research Flow](#complete-research-flow)
2. [Research Initiation](#research-initiation)
3. [SSE Streaming Connection](#sse-streaming-connection)
4. [Orbital Iteration Cycle](#orbital-iteration-cycle)
5. [Agent Execution Flow](#agent-execution-flow)
6. [Error Handling & Retry](#error-handling--retry)
7. [Paper Retrieval](#paper-retrieval)

---

## Complete Research Flow

```mermaid
sequenceDiagram
    actor User
    participant Frontend as Next.js Frontend
    participant API as FastAPI Backend
    participant Graph as LangGraph Workflow
    participant Agents as Research Agents
    participant LLM as AWS Bedrock
    participant Storage as File System

    User->>Frontend: Enter research question
    Frontend->>API: POST /api/research/start
    API->>API: Generate research_id
    API-->>Frontend: {research_id, status}
    
    Frontend->>API: GET /stream?question=...
    API->>Graph: stream_research(question, research_id)
    
    loop Orbital Iteration
        Graph->>Agents: Execute Flow Master
        Agents-->>Graph: next_action
        Graph->>Agents: Execute Current
        Agents->>LLM: Generate hypotheses
        LLM-->>Agents: Hypotheses
        Agents-->>Graph: Updated state
        Graph-->>API: agent_message event
        API-->>Frontend: SSE: agent_message
        Frontend->>Frontend: Update UI
        
        Graph->>Agents: Execute Source
        Agents->>LLM: Search & synthesize
        LLM-->>Agents: Sources
        Agents-->>Graph: Updated state
        Graph-->>API: agent_message event
        API-->>Frontend: SSE: agent_message
        
        Graph->>Agents: Execute Channel
        Agents->>LLM: Design experiments
        LLM-->>Agents: Experiments
        Agents-->>Graph: Updated state
        Graph-->>API: agent_message event
        API-->>Frontend: SSE: agent_message
        
        Graph->>Agents: Execute Filter
        Agents->>LLM: Evaluate quality
        LLM-->>Agents: Quality score
        Agents-->>Graph: Updated state + should_iterate
        Graph-->>API: agent_message event
        API-->>Frontend: SSE: agent_message
        
        alt Quality acceptable
            Graph->>Agents: Execute Confluence
            Agents->>LLM: Write paper
            LLM-->>Agents: Paper content
            Agents-->>Graph: Updated state + paper
            Graph->>Storage: save_paper()
            Storage-->>Graph: Saved paths
            Graph-->>API: complete event
            API-->>Frontend: SSE: complete
            Frontend->>Frontend: Show celebration
        else Quality insufficient
            Note over Graph,Agents: Iterate again
        end
    end
    
    Frontend->>API: GET /api/research/{id}/paper
    API->>Storage: load_paper(research_id)
    Storage-->>API: Paper data
    API-->>Frontend: Paper JSON
    Frontend->>User: Display research paper
```

---

## Research Initiation

```mermaid
sequenceDiagram
    actor User
    participant UI as Homepage
    participant Router as Next.js Router
    participant API as FastAPI /start

    User->>UI: Fill research form
    User->>UI: Click "Start Research"
    UI->>UI: Validate input
    
    UI->>API: POST /api/research/start<br/>{question, max_iterations, ...}
    
    API->>API: Generate UUID<br/>research_id = "research-abc123"
    API->>API: Create background task<br/>run_research_background()
    
    API-->>UI: 200 OK<br/>{research_id, question, status}
    
    UI->>Router: Navigate to<br/>/flow/[id]?question=...
    Router->>Router: Load Live Theater page
    
    Note over Router: Live Theater page<br/>connects to SSE stream
```

---

## SSE Streaming Connection

```mermaid
sequenceDiagram
    participant Theater as Live Theater Page
    participant Hook as useResearchStream Hook
    participant ES as EventSource
    participant API as FastAPI /stream
    participant Graph as Research Graph

    Theater->>Hook: useResearchStream(id, question)
    Hook->>ES: new EventSource(url)
    ES->>API: GET /stream?question=...
    
    API->>Graph: stream_research()
    API-->>ES: event: connected<br/>data: {research_id, message}
    ES->>Hook: onopen()
    Hook->>Theater: connectionStatus = 'connected'
    
    loop Research Execution
        Graph-->>API: yield agent_message event
        API-->>ES: event: agent_message<br/>data: {agent, message, ...}
        ES->>Hook: addEventListener('agent_message')
        Hook->>Hook: Update state<br/>(messages, phase, quality)
        Hook->>Theater: Re-render with new data
        Theater->>Theater: Auto-scroll feed<br/>Animate agent avatar
    end
    
    Graph-->>API: yield complete event
    API-->>ES: event: complete<br/>data: {research_id, stop_reason, ...}
    ES->>Hook: addEventListener('complete')
    Hook->>Hook: connectionStatus = 'complete'
    Hook->>Theater: Trigger onComplete callback
    Theater->>Theater: Show celebration animation
    
    alt Connection Error
        API->>API: Exception occurs
        API-->>ES: event: error<br/>data: {error}
        ES->>Hook: onerror()
        Hook->>Hook: Implement reconnection<br/>with exponential backoff
        Hook->>ES: new EventSource(url)
    end
    
    Theater->>Hook: Component unmount
    Hook->>ES: eventSource.close()
```

---

## Orbital Iteration Cycle

```mermaid
sequenceDiagram
    participant Graph as LangGraph
    participant FM as Flow Master
    participant Current as The Current
    participant Source as The Source
    participant Channel as The Channel
    participant Filter as The Filter
    participant Confluence as The Confluence
    participant State as Research State

    Note over Graph,State: Iteration 0 starts
    
    Graph->>FM: flow_master_node(state)
    FM->>State: Analyze state
    FM->>FM: hypotheses_count = 0<br/>next_action = "current"
    FM->>State: Update next_action, phase
    State-->>Graph: Updated state
    
    Graph->>Graph: route_from_flow_master()
    Graph->>Current: current_node(state)
    Current->>Current: Generate hypotheses
    Current->>State: Add hypotheses, messages
    State-->>Graph: Updated state
    
    Graph->>FM: flow_master_node(state)
    FM->>State: hypotheses_count = 3<br/>sources_count = 0
    FM->>FM: next_action = "source"
    State-->>Graph: Updated state
    
    Graph->>Source: source_node(state)
    Source->>Source: Multi-source search
    Source->>State: Add sources
    State-->>Graph: Updated state
    
    Graph->>FM: flow_master_node(state)
    FM->>FM: next_action = "channel"
    State-->>Graph: Updated state
    
    Graph->>Channel: channel_node(state)
    Channel->>Channel: Design experiments
    Channel->>State: Add experiments
    State-->>Graph: Updated state
    
    Graph->>FM: flow_master_node(state)
    FM->>FM: next_action = "filter"
    State-->>Graph: Updated state
    
    Graph->>Filter: filter_node(state)
    Filter->>Filter: Evaluate quality<br/>quality_score = 7.5
    Filter->>Filter: should_continue_iteration()<br/>score < threshold?<br/>iterations < max?
    
    alt Quality acceptable OR max iterations
        Filter->>State: should_iterate = false<br/>stop_reason = "quality_threshold_met"
        State-->>Graph: Updated state
        Graph->>Graph: route_from_filter()<br/>→ "confluence"
        Graph->>Confluence: confluence_node(state)
        Confluence->>Confluence: Write comprehensive paper
        Confluence->>State: paper_draft, stop_reason
        State-->>Graph: Final state
        Graph->>Graph: END
    else Quality insufficient
        Filter->>State: should_iterate = true<br/>iteration += 1
        State-->>Graph: Updated state
        Graph->>Graph: route_from_filter()<br/>→ "flow_master"
        Note over Graph,FM: Start next orbit
        Graph->>FM: flow_master_node(state)
    end
```

---

## Agent Execution Flow

```mermaid
sequenceDiagram
    participant Node as Graph Node
    participant Agent as Base Agent
    participant Bedrock as Bedrock Client
    participant AWS as AWS Bedrock API
    participant State as Research State

    Note over Node,State: Example: The Current Agent
    
    Node->>Agent: execute(state)
    Agent->>Agent: Extract question<br/>from state
    Agent->>Agent: _build_prompt()<br/>Create LLM prompt
    
    Agent->>Bedrock: invoke(prompt, system_prompt)
    
    loop Retry with exponential backoff
        Bedrock->>AWS: invoke_model()<br/>{model_id, messages, ...}
        
        alt Success
            AWS-->>Bedrock: {content, usage}
            Bedrock->>Bedrock: Track tokens & cost<br/>input: 1234, output: 567
            Bedrock-->>Agent: Response text
        else ThrottlingException
            AWS-->>Bedrock: ThrottlingException
            Bedrock->>Bedrock: Wait 2^attempt seconds
            Note over Bedrock: Retry...
        else Other Error
            AWS-->>Bedrock: ClientError
            Bedrock-->>Agent: Raise BedrockClientError
        end
    end
    
    Agent->>Agent: _parse_response()<br/>Extract structured data
    Agent->>Agent: format_message()<br/>Create agent message
    
    Agent->>State: Update state<br/>- Add parsed data<br/>- Add message<br/>- Update phase
    State-->>Agent: Updated state
    Agent-->>Node: Return updated state
    
    Node->>Node: Add message to state.messages
    Node-->>Node: Continue to next node
```

---

## Error Handling & Retry

```mermaid
sequenceDiagram
    participant Agent as Research Agent
    participant Bedrock as Bedrock Client
    participant AWS as AWS Bedrock

    Agent->>Bedrock: invoke(prompt)
    
    Note over Bedrock,AWS: Attempt 1/5
    Bedrock->>AWS: invoke_model()
    AWS-->>Bedrock: ThrottlingException
    Bedrock->>Bedrock: Log warning<br/>Wait 2 seconds
    
    Note over Bedrock,AWS: Attempt 2/5
    Bedrock->>AWS: invoke_model()
    AWS-->>Bedrock: ThrottlingException
    Bedrock->>Bedrock: Log warning<br/>Wait 4 seconds
    
    Note over Bedrock,AWS: Attempt 3/5
    Bedrock->>AWS: invoke_model()
    AWS-->>Bedrock: 200 OK<br/>{content, usage}
    Bedrock->>Bedrock: Log success<br/>"✅ Successfully invoked after 3 attempts"
    Bedrock-->>Agent: Response text
    
    alt Max retries exceeded
        Note over Bedrock,AWS: Attempt 5/5
        Bedrock->>AWS: invoke_model()
        AWS-->>Bedrock: ThrottlingException
        Bedrock->>Bedrock: Log error<br/>"Max retries exceeded"
        Bedrock-->>Agent: Raise BedrockClientError
        Agent->>Agent: Handle error<br/>- Use fallback<br/>- Log failure<br/>- Continue research
    end
```

---

## Multi-Source Search Flow

```mermaid
sequenceDiagram
    participant Source as Source Agent
    participant Search as Search Tools
    participant Scholar as Semantic Scholar
    participant ArXiv as ArXiv API
    participant Tavily as Tavily API
    participant LLM as AWS Bedrock

    Source->>Search: multi_source_search(question)
    
    par Parallel Search
        Search->>Scholar: search_semantic_scholar()
        Scholar-->>Search: [paper1, paper2, ...]
    and
        Search->>ArXiv: search_arxiv()
        ArXiv-->>Search: [preprint1, preprint2, ...]
    and
        Search->>Tavily: search_tavily()
        Tavily-->>Search: [web1, web2, ...]
    end
    
    Search->>Search: Combine results<br/>Deduplicate by title
    Search->>Search: Rank by relevance<br/>Take top 20
    Search-->>Source: Combined sources
    
    Source->>LLM: Synthesize findings<br/>Prompt: "Analyze these sources..."
    LLM-->>Source: Synthesis summary
    
    Source->>Source: Update state<br/>- sources: [...]<br/>- synthesis: {...}
    
    alt Search Error
        Scholar-->>Search: Exception (timeout)
        Search->>Search: Log warning<br/>Continue with other sources
        Note over Search: Graceful degradation
    end
```

---

## Paper Retrieval Flow

```mermaid
sequenceDiagram
    actor User
    participant UI as Paper Viewer Page
    participant API as FastAPI
    participant Storage as File System

    User->>UI: Click "View Paper"<br/>or navigate to /papers/[id]
    UI->>UI: useEffect: loadPaper()
    
    UI->>API: GET /api/research/{id}/paper
    
    API->>Storage: load_paper(research_id)
    Storage->>Storage: Read paper.md
    Storage->>Storage: Read metadata.json
    Storage->>Storage: Read conversation.json
    Storage->>Storage: Read state.json
    
    alt Paper exists
        Storage-->>API: {paper, metadata, conversation, state}
        API-->>UI: 200 OK<br/>Complete paper data
        
        UI->>UI: setState(paper)
        UI->>UI: Render tabs<br/>- Paper (Markdown)<br/>- Meta-Analysis<br/>- Conversation
        UI->>User: Display formatted paper
    else Paper not found
        Storage-->>API: None (paper not found)
        API-->>UI: 404 Not Found<br/>{detail: "Research ... not found"}
        UI->>UI: Show error state<br/>with retry button
        UI->>User: Display error message
    else Storage error
        Storage-->>API: StorageError
        API-->>UI: 500 Internal Server Error
        UI->>UI: Show error state
        UI->>User: Display error message
    end
    
    User->>UI: Click "Download"
    UI->>UI: Create Blob from paper.paper
    UI->>UI: Trigger download<br/>research-{id}.md
    UI->>User: File downloaded
```

---

## Frontend State Management Flow

```mermaid
sequenceDiagram
    participant User
    participant Component as Live Theater Component
    participant Hook as useResearchStream Hook
    participant EventSource as EventSource API
    participant State as React State

    User->>Component: Load /flow/[id]?question=...
    Component->>Hook: useResearchStream(id, question)
    
    Hook->>State: Initialize state<br/>- messages: []<br/>- connectionStatus: 'connecting'<br/>- activeAgent: ''<br/>- qualityScore: 0
    
    Hook->>EventSource: new EventSource(url)
    EventSource-->>Hook: onopen()
    Hook->>State: connectionStatus = 'connected'
    State-->>Component: Re-render
    Component->>User: Show "Connected" status
    
    loop SSE Events
        EventSource->>Hook: agent_message event
        Hook->>State: Update messages<br/>setMessages(prev => [...prev, msg])
        Hook->>State: Update activeAgent<br/>setActiveAgent(msg.agent)
        Hook->>State: Update qualityScore<br/>setQualityScore(msg.quality_score)
        State-->>Component: Re-render
        Component->>Component: Animate agent avatar
        Component->>Component: Auto-scroll feed
        Component->>User: Show updated UI
    end
    
    EventSource->>Hook: complete event
    Hook->>State: connectionStatus = 'complete'
    Hook->>Hook: Call onComplete callback
    State-->>Component: Re-render
    Component->>Component: Show celebration animation
    Component->>User: Research complete!
    
    alt Connection Error
        EventSource->>Hook: onerror()
        Hook->>State: connectionStatus = 'reconnecting'
        Hook->>Hook: Implement exponential backoff
        Hook->>EventSource: new EventSource(url)
        Note over Hook,EventSource: Retry connection
    end
    
    Component->>Component: Component unmount
    Component->>Hook: Cleanup
    Hook->>EventSource: eventSource.close()
```

---

## Authentication Flow (Future)

```mermaid
sequenceDiagram
    actor User
    participant UI as Frontend
    participant Auth as Auth Service
    participant API as Backend API
    participant DB as Database

    User->>UI: Click "Login"
    UI->>Auth: Redirect to OAuth provider<br/>(Google/GitHub)
    User->>Auth: Authenticate
    Auth-->>UI: Redirect with auth code
    
    UI->>Auth: Exchange code for tokens
    Auth->>Auth: Validate auth code
    Auth->>DB: Get/Create user
    DB-->>Auth: User data
    Auth-->>UI: {access_token, refresh_token, user}
    
    UI->>UI: Store tokens<br/>localStorage.setItem('token', ...)
    UI->>UI: Update auth state
    
    loop API Requests
        UI->>API: Request with header<br/>Authorization: Bearer {token}
        API->>API: Verify JWT signature
        API->>API: Check expiration
        
        alt Token valid
            API->>API: Extract user_id from claims
            API->>API: Check permissions
            API-->>UI: 200 OK + response data
        else Token expired
            API-->>UI: 401 Unauthorized
            UI->>Auth: Refresh token
            Auth-->>UI: New access_token
            UI->>API: Retry with new token
        else Token invalid
            API-->>UI: 401 Unauthorized
            UI->>UI: Clear tokens<br/>Redirect to login
        end
    end
    
    User->>UI: Click "Logout"
    UI->>UI: Clear tokens
    UI->>Auth: Revoke tokens (optional)
    UI->>UI: Redirect to homepage
```

---

## Conclusion

These sequence diagrams provide a comprehensive view of the interactions within the FLUX system:

1. **Complete Research Flow**: End-to-end process from user input to paper delivery
2. **Research Initiation**: How research sessions are started
3. **SSE Streaming**: Real-time connection and event handling
4. **Orbital Iteration**: The core iterative research cycle
5. **Agent Execution**: How individual agents work with LLMs
6. **Error Handling**: Retry logic and resilience patterns
7. **Paper Retrieval**: How completed papers are accessed

Each diagram highlights:
- **Participants**: The components involved
- **Message Flow**: Sequential and parallel operations
- **Decision Points**: Conditional logic and error handling
- **State Changes**: How data evolves through the system
- **User Experience**: Visible feedback and interactions

These diagrams serve as both documentation and design validation tools for the FLUX architecture.

