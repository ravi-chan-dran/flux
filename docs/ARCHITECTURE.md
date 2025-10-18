# FLUX Architecture Documentation

## Table of Contents
1. [System Overview](#system-overview)
2. [High-Level Architecture](#high-level-architecture)
3. [Component Architecture](#component-architecture)
4. [Data Flow](#data-flow)
5. [Technology Stack](#technology-stack)
6. [Deployment Architecture](#deployment-architecture)

---

## System Overview

**FLUX** (Flow-based Learning Understanding eXchange) is a multi-agent AI research system that uses orbital iteration through specialized agents to conduct comprehensive research on any given topic.

### Key Characteristics
- **Multi-Agent System**: 6 specialized AI agents working in coordination
- **Orbital Iteration**: Iterative refinement through repeated agent cycles
- **Real-Time Streaming**: Server-Sent Events (SSE) for live research updates
- **Quality-Driven**: Automated quality assessment and iteration control
- **Research Synthesis**: Comprehensive paper generation from distributed research

### Design Philosophy
1. **Separation of Concerns**: Each agent has a single, well-defined responsibility
2. **Stateful Workflow**: Research state flows through agents and accumulates knowledge
3. **Observable Process**: Real-time visibility into agent activities and decisions
4. **Resilient**: Automatic retry logic, error handling, and graceful degradation
5. **Scalable**: Stateless backend, horizontal scaling capability

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                           │
│                    (Next.js 14 Frontend)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Homepage   │  │ Live Theater │  │ Paper Viewer │         │
│  │   Research   │  │  Real-time   │  │ Archive &    │         │
│  │    Input     │  │  Streaming   │  │ Meta-analysis│         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└───────────────────────────┬─────────────────────────────────────┘
                            │ HTTP/REST + SSE
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API LAYER (FastAPI)                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   /start     │  │   /stream    │  │   /paper     │         │
│  │   Research   │  │   Research   │  │   Retrieval  │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                  RESEARCH ORCHESTRATION                          │
│                    (LangGraph Workflow)                          │
│                                                                   │
│    ┌─────────────────────────────────────────────────────┐     │
│    │              ORBITAL ITERATION LOOP                  │     │
│    │                                                       │     │
│    │  ┌──────────┐      ┌──────────┐      ┌──────────┐ │     │
│    │  │   Flow   │─────▶│  Current │─────▶│  Source  │ │     │
│    │  │  Master  │      │ (Hypothe-│      │ (Research│ │     │
│    │  │(Orchestr)│      │   sis)   │      │ Searcher)│ │     │
│    │  └──────────┘      └──────────┘      └──────────┘ │     │
│    │       ▲                                      │       │     │
│    │       │                                      ▼       │     │
│    │  ┌──────────┐      ┌──────────┐      ┌──────────┐ │     │
│    │  │  Filter  │◀─────│  Channel │◀─────│   ...    │ │     │
│    │  │ (Quality │      │(Experim- │                   │     │
│    │  │  Critic) │      │   ent)   │                   │     │
│    │  └──────────┘      └──────────┘                   │     │
│    │       │                                             │     │
│    │       │ Quality OK?                                 │     │
│    │       └─────────────────────┐                      │     │
│    │                              ▼                      │     │
│    │                       ┌──────────┐                 │     │
│    │                       │Confluence│                 │     │
│    │                       │  (Paper  │                 │     │
│    │                       │   Synth) │                 │     │
│    │                       └──────────┘                 │     │
│    └─────────────────────────────────────────────────────┘     │
│                                                                   │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    EXTERNAL SERVICES                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ AWS Bedrock  │  │   Semantic   │  │    ArXiv     │         │
│  │   Claude     │  │   Scholar    │  │     API      │         │
│  │  3.5 Sonnet  │  │     API      │  │              │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│  ┌──────────────┐                                               │
│  │    Tavily    │                                               │
│  │  Web Search  │                                               │
│  └──────────────┘                                               │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                      STORAGE LAYER                               │
│  ┌──────────────────────────────────────────────────────┐      │
│  │            File System Storage                        │      │
│  │  backend/storage/papers/{research_id}/               │      │
│  │    ├── paper.md           (Final paper)              │      │
│  │    ├── metadata.json      (Research metadata)        │      │
│  │    ├── conversation.json  (Agent messages)           │      │
│  │    └── state.json         (Complete state)           │      │
│  └──────────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────────┘
```

---

## Component Architecture

### Frontend Architecture (Next.js 14)

```
flux-frontend/
├── app/                          # App Router
│   ├── page.tsx                  # Homepage (Research Input)
│   ├── flow/[id]/page.tsx       # Live Research Theater
│   ├── papers/[id]/page.tsx     # Paper Viewer
│   ├── research/page.tsx         # Research Archive
│   └── layout.tsx                # Root Layout
├── components/                   # Reusable Components
│   ├── AgentAvatar.tsx          # Agent visualization
│   ├── ConversationFeed.tsx     # Message stream
│   ├── PhaseProgress.tsx        # Progress indicator
│   ├── LiveStats.tsx            # Real-time metrics
│   ├── ConnectionStatus.tsx     # SSE status
│   └── CelebrationAnimation.tsx # Completion animation
└── lib/                          # Utilities
    ├── api.ts                    # API client & SSE hook
    └── types.ts                  # TypeScript interfaces
```

**Key Frontend Patterns:**
- **Custom Hooks**: `useResearchStream` for SSE management
- **State Management**: React hooks + local state
- **Real-time Updates**: EventSource API with reconnection
- **Responsive Design**: Mobile-first with Tailwind CSS
- **Type Safety**: Full TypeScript coverage

### Backend Architecture (FastAPI + LangGraph)

```
flux/backend/
├── main.py                       # FastAPI application
├── flux_core/
│   ├── agents/                   # Agent Implementations
│   │   ├── base_agent.py        # Abstract base class
│   │   ├── flow_master.py       # Orchestrator
│   │   ├── current.py           # Hypothesis generator
│   │   ├── source.py            # Research searcher
│   │   ├── channel.py           # Experiment designer
│   │   ├── filter.py            # Quality critic
│   │   └── confluence.py        # Paper synthesizer
│   ├── graph/                    # LangGraph Workflow
│   │   ├── research_graph.py    # Orbital flow definition
│   │   └── state.py             # Research state management
│   └── tools/                    # External Integrations
│       ├── bedrock_client.py    # AWS Bedrock client
│       ├── search.py            # Multi-source search
│       └── storage.py           # File storage
└── storage/                      # Persistent storage
    └── papers/                   # Research papers
```

**Key Backend Patterns:**
- **Agent Pattern**: Specialized, single-responsibility agents
- **State Machine**: LangGraph for workflow orchestration
- **Async/Await**: Full async support for I/O operations
- **Retry Logic**: Exponential backoff for external APIs
- **Event Streaming**: SSE for real-time updates

---

## Data Flow

### 1. Research Initiation Flow

```
User Input → Frontend → POST /api/research/start
    ↓
Create initial state (research_id, question, config)
    ↓
Return research_id to frontend
    ↓
Frontend → SSE /api/research/{id}/stream?question=...
```

### 2. Research Execution Flow

```
1. Flow Master (Orchestrator)
   ├─ Analyzes current state
   ├─ Determines next action
   └─ Routes to appropriate agent

2. The Current (Hypothesis Generator)
   ├─ Analyzes research question
   ├─ Generates testable hypotheses
   ├─ Assigns confidence scores
   └─ Returns to Flow Master

3. The Source (Research Searcher)
   ├─ Searches Semantic Scholar
   ├─ Searches ArXiv
   ├─ Searches Tavily Web
   ├─ Synthesizes findings
   └─ Returns to Flow Master

4. The Channel (Experiment Designer)
   ├─ Designs experiments for each hypothesis
   ├─ Defines success criteria
   ├─ Estimates resources
   └─ Returns to Flow Master

5. The Filter (Quality Critic)
   ├─ Evaluates research quality (0-10)
   ├─ Identifies issues and strengths
   ├─ Decides: iterate or complete?
   └─ If iterate → back to Flow Master
       If complete → to Confluence

6. The Confluence (Paper Synthesizer)
   ├─ Synthesizes all research
   ├─ Generates comprehensive paper
   ├─ Saves to file system
   └─ Research complete!
```

### 3. State Evolution

```
Initial State
├── question: string
├── research_id: string
├── iteration: 0
├── quality_score: 0.0
├── phase: "initialize"
└── messages: []

After Current
├── hypotheses: [...]
├── phase: "ideation"
└── messages: [...]

After Source
├── hypotheses: [...]
├── sources: [...]
├── phase: "research"
└── messages: [...]

After Channel
├── hypotheses: [...]
├── sources: [...]
├── experiments: [...]
├── phase: "design"
└── messages: [...]

After Filter
├── quality_score: 7.5
├── critiques: [...]
├── should_iterate: false
├── stop_reason: "quality_threshold_met"
├── phase: "critique"
└── messages: [...]

After Confluence
├── paper_draft: "# Research Paper..."
├── phase: "complete"
└── messages: [...]
```

---

## Technology Stack

### Frontend Stack

| Technology | Purpose | Version |
|------------|---------|---------|
| **Next.js** | React framework with App Router | 14.x |
| **TypeScript** | Type safety and developer experience | 5.x |
| **Tailwind CSS** | Utility-first styling | 3.x |
| **Framer Motion** | Animations and transitions | 11.x |
| **Axios** | HTTP client with retry logic | 1.x |
| **React Markdown** | Markdown rendering | 9.x |
| **date-fns** | Date formatting | 3.x |
| **EventSource** | SSE client (native browser API) | - |

### Backend Stack

| Technology | Purpose | Version |
|------------|---------|---------|
| **Python** | Primary language | 3.11+ |
| **FastAPI** | Web framework | 0.104+ |
| **LangGraph** | Workflow orchestration | Latest |
| **AWS Bedrock** | LLM inference (Claude 3.5 Sonnet) | - |
| **Boto3** | AWS SDK | 1.34+ |
| **Loguru** | Structured logging | 0.7+ |
| **Pydantic** | Data validation | 2.x |
| **aiofiles** | Async file I/O | 23.x |
| **pytest** | Testing framework | 7.x |

### External Services

| Service | Purpose | Rate Limits |
|---------|---------|-------------|
| **AWS Bedrock** | Claude 3.5 Sonnet LLM | Configurable (default: ~10-50 req/min) |
| **Semantic Scholar** | Academic paper search | 100 req/5min |
| **ArXiv** | Preprint paper search | 1 req/3sec |
| **Tavily** | Web search | Plan-dependent |

---

## Deployment Architecture

### Development Setup

```
┌─────────────────────────────────────────┐
│          Developer Machine               │
│                                          │
│  ┌────────────────────────────────────┐ │
│  │   Frontend (localhost:3000)        │ │
│  │   npm run dev                       │ │
│  └────────────────────────────────────┘ │
│                ↓                         │
│  ┌────────────────────────────────────┐ │
│  │   Backend (localhost:8000)         │ │
│  │   python main.py                   │ │
│  └────────────────────────────────────┘ │
│                ↓                         │
│  ┌────────────────────────────────────┐ │
│  │   AWS Bedrock (us-east-1)          │ │
│  │   Via AWS Profile                  │ │
│  └────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

### Production Architecture (Future)

```
┌─────────────────────────────────────────────────────────┐
│                    CDN (Vercel/CloudFront)              │
└─────────────────────┬───────────────────────────────────┘
                      │ HTTPS
                      ▼
┌─────────────────────────────────────────────────────────┐
│              Frontend (Vercel/AWS Amplify)              │
│                    Static Site + SSR                    │
└─────────────────────┬───────────────────────────────────┘
                      │ HTTPS/WSS
                      ▼
┌─────────────────────────────────────────────────────────┐
│            Load Balancer (ALB/API Gateway)              │
└─────────────────────┬───────────────────────────────────┘
                      │
            ┌─────────┴─────────┐
            ▼                   ▼
┌─────────────────────┐  ┌─────────────────────┐
│   Backend Instance  │  │   Backend Instance  │
│   (ECS/Lambda)      │  │   (ECS/Lambda)      │
└──────────┬──────────┘  └──────────┬──────────┘
           │                        │
           └───────────┬────────────┘
                       ▼
┌─────────────────────────────────────────────────────────┐
│              Shared Storage (EFS/S3)                    │
│              Papers & Research Data                      │
└─────────────────────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│              External Services                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ AWS Bedrock  │  │   Semantic   │  │    ArXiv     │ │
│  │              │  │   Scholar    │  │              │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────┘
```

### Scaling Considerations

**Horizontal Scaling:**
- Backend is stateless (except file storage)
- Multiple backend instances behind load balancer
- Shared file storage (EFS or S3)

**Vertical Scaling:**
- Increase AWS Bedrock quotas
- Larger instance types for compute-heavy tasks

**Caching:**
- Cache search results (Redis)
- Cache LLM responses for repeated queries
- CDN for frontend assets

**Rate Limiting:**
- Per-user rate limits on API
- Distributed rate limiting (Redis)
- Queue system for research requests

---

## Security Architecture

### Authentication & Authorization
```
User → Frontend → API Key/JWT → Backend
                      ↓
              Validate Token
                      ↓
              Check Permissions
                      ↓
              Process Request
```

### Data Security
- **In Transit**: HTTPS/TLS for all communications
- **At Rest**: Encrypted file storage
- **API Keys**: Environment variables, never committed
- **AWS**: IAM roles and policies for least privilege

### CORS Configuration
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Performance Characteristics

### Research Execution Time

| Component | Time (avg) | Notes |
|-----------|-----------|-------|
| Flow Master | 1-2s | Fast, no external API |
| The Current | 5-8s | LLM generation |
| The Source | 10-15s | Multiple API calls |
| The Channel | 5-8s | LLM generation |
| The Filter | 3-5s | LLM analysis |
| The Confluence | 8-12s | Long-form generation |
| **Total (1 iteration)** | **32-50s** | With 2s delays between agents |
| **Total (3 iterations)** | **96-150s** | If quality requires iteration |

### Throughput
- **Single Instance**: 1-2 concurrent research sessions
- **With Scaling**: 10-50+ concurrent sessions (limited by AWS quotas)

### Resource Usage
- **Frontend**: ~50MB RAM, minimal CPU
- **Backend**: ~200-500MB RAM per instance
- **Storage**: ~50-200KB per research paper

---

## Reliability & Resilience

### Error Handling Strategy

1. **Retry with Exponential Backoff**
   - AWS throttling: 2s → 4s → 8s → 16s → 32s
   - Network errors: 3 retries with backoff

2. **Graceful Degradation**
   - If Source fails: Use partial results
   - If Filter fails: Use default quality score
   - If Confluence fails: Generate fallback paper

3. **State Recovery**
   - Research state persisted at each step
   - Can resume from last successful state

4. **Connection Management**
   - SSE auto-reconnection (10 attempts)
   - Heartbeat detection (60s timeout)
   - State preservation across reconnections

### Monitoring Points

```
1. API Endpoints
   ├─ Request rate
   ├─ Error rate
   ├─ Response time
   └─ Status codes

2. Agent Execution
   ├─ Invocation count
   ├─ Success/failure rate
   ├─ Execution time
   └─ Token usage

3. External Services
   ├─ AWS Bedrock throttling events
   ├─ API response times
   └─ Rate limit proximity

4. Storage
   ├─ Papers saved
   ├─ Storage usage
   └─ I/O errors
```

---

## Future Enhancements

### Short-term (Next 3 months)
1. **Database Integration**: PostgreSQL for metadata and search
2. **User Authentication**: OAuth2 with JWT tokens
3. **Research Templates**: Pre-configured research types
4. **Export Formats**: PDF, LaTeX, Word
5. **Collaboration**: Multiple users, shared research

### Medium-term (3-6 months)
1. **Advanced Search**: Full-text search across papers
2. **Research Graphs**: Visualization of knowledge connections
3. **Custom Agents**: User-defined agent types
4. **API Access**: Public API for programmatic access
5. **Analytics Dashboard**: Usage metrics and insights

### Long-term (6-12 months)
1. **Multi-LLM Support**: GPT-4, Gemini, etc.
2. **Distributed Execution**: Kubernetes-based scaling
3. **Research Marketplace**: Share and discover research
4. **Real-time Collaboration**: Multiple users on same research
5. **Mobile Apps**: iOS and Android native apps

---

## Conclusion

FLUX is a sophisticated multi-agent research system built on modern, scalable technologies. The architecture emphasizes:

- **Modularity**: Each component is independent and replaceable
- **Observability**: Full visibility into the research process
- **Resilience**: Robust error handling and recovery
- **Scalability**: Horizontal scaling capability
- **Extensibility**: Easy to add new agents or features

The system is production-ready for single-user deployments and can be scaled to support multiple concurrent users with appropriate infrastructure.

