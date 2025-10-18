# FLUX Feature Documentation

## Table of Contents
1. [Core Features](#core-features)
2. [User Interface Features](#user-interface-features)
3. [Research Capabilities](#research-capabilities)
4. [System Features](#system-features)
5. [Developer Features](#developer-features)
6. [Future Features](#future-features)

---

## Core Features

### 1. Multi-Agent Research System

**Description**: Six specialized AI agents work in coordination to conduct comprehensive research.

**Agents:**
- **🧑‍💼 Flow Master**: Orchestrates the workflow and routes to appropriate agents
- **💡 The Current**: Generates creative, testable hypotheses
- **📚 The Source**: Searches multiple academic and web sources
- **🔬 The Channel**: Designs rigorous experimental methodologies
- **🛡️ The Filter**: Critically evaluates research quality
- **✍️ The Confluence**: Synthesizes findings into comprehensive papers

**Benefits:**
- Separation of concerns - each agent has a single responsibility
- Parallelizable workload (future optimization)
- Easy to add new agent types
- Observable agent contributions

**Use Cases:**
- Academic research
- Literature reviews
- Hypothesis validation
- Experimental design
- Knowledge synthesis

---

### 2. Orbital Iteration

**Description**: Iterative refinement through repeated cycles of hypothesis generation, research, and critique.

**How It Works:**
```
Iteration 0: Generate → Research → Design → Critique (Score: 6.5)
    ↓
Iteration 1: Refine → Deep Research → Better Design → Critique (Score: 7.8)
    ↓
Iteration 2: Polish → Comprehensive → Rigorous → Critique (Score: 8.2)
    ↓
Quality threshold met → Final synthesis
```

**Configuration:**
- `MAX_ITERATIONS`: Maximum number of orbits (default: 1)
- `QUALITY_THRESHOLD`: Minimum acceptable quality score (default: 8.0/10)
- `IMPROVEMENT_THRESHOLD`: Minimum improvement between iterations (default: 0.5)

**Stop Conditions:**
1. Quality threshold met
2. Maximum iterations reached
3. Insufficient improvement detected
4. Error occurs

**Benefits:**
- Progressively better research quality
- Automatic quality control
- Configurable trade-off between speed and quality

---

### 3. Real-Time Research Theater

**Description**: Live visualization of the research process as it happens.

**Features:**
- **Live Agent Display**: See which agent is currently working
- **Animated Avatars**: Agents pulse and glow when active
- **Phase Progress**: Visual timeline of research phases
- **Conversation Feed**: Real-time message stream from agents
- **Live Stats Sidebar**: Current metrics and progress
- **Quality Score Evolution**: Watch quality improve across iterations
- **Celebration Animation**: Confetti and celebration on completion

**Technical Implementation:**
- Server-Sent Events (SSE) for real-time updates
- Automatic reconnection with exponential backoff
- State preservation across reconnections
- Heartbeat detection for stale connections

**User Experience:**
- No manual refresh needed
- Instant feedback on research progress
- Full transparency into agent activities
- Engaging and educational

---

### 4. Multi-Source Research

**Description**: Comprehensive search across multiple academic and web sources.

**Data Sources:**

| Source | Type | Coverage | Rate Limits |
|--------|------|----------|-------------|
| **Semantic Scholar** | Academic papers | 200M+ papers | 100 req/5min |
| **ArXiv** | Preprints | 2M+ papers (STEM) | 1 req/3sec |
| **Tavily** | Web search | General web | Plan-dependent |

**Features:**
- Parallel search execution
- Smart deduplication by title/DOI
- Relevance ranking
- Citation count tracking
- Source synthesis via LLM

**Search Strategy:**
1. Query all sources in parallel
2. Combine and deduplicate results
3. Rank by relevance to question
4. Select top 15-20 sources
5. Synthesize key themes and gaps

**Graceful Degradation:**
- If one source fails, others continue
- Partial results are still useful
- Clear logging of failures

---

### 5. Comprehensive Paper Generation

**Description**: Automatically synthesizes research into well-structured academic papers.

**Paper Structure:**
```markdown
# [Research Question as Title]

## Abstract
150-200 word summary

## Introduction
Context and motivation

## Background
Literature review and foundations

## Hypotheses
Testable hypotheses with confidence levels

## Methodology
Experimental designs and approaches

## Results
Expected outcomes (research design paper)

## Discussion
Interpretation, limitations, implications

## Conclusion
Key takeaways and future directions

## References
Full citations with URLs
```

**Content Quality:**
- Scholarly tone
- Evidence-based claims
- Proper attribution of agent contributions
- Accessible to educated general readers
- Structured markdown formatting

**Fallback Mechanisms:**
- If LLM fails, generates basic template
- Ensures all required sections present
- Adds missing sections if needed

---

## User Interface Features

### 1. Homepage - Research Input

**Features:**
- Clean, focused design
- Large text area for research question
- Example questions for inspiration
- System stats cards (agents, phases, sources)
- Agent showcase with roles
- Responsive mobile layout

**User Flow:**
1. Enter research question
2. Click "Start Research"
3. Navigate to live theater
4. Watch research unfold

---

### 2. Live Research Theater

**Layout:**
```
┌─────────────────────────────────────────────────────┐
│ Header: FLUX | Research ID | Copy | Download        │
├─────────────────────────────────────────────────────┤
│ Agent Avatars (Horizontal, Active Agent Highlighted)│
├─────┬───────────────────────────────────────┬───────┤
│     │  Phase Progress Timeline              │       │
│     │  (5 phases, current highlighted)      │       │
│     ├───────────────────────────────────────┤       │
│     │                                       │ Live  │
│     │  Conversation Feed                    │ Stats │
│     │  (Agent messages, auto-scroll)        │       │
│     │                                       │ Side  │
│     │  - Hypotheses                         │ -bar  │
│     │  - Sources found                      │       │
│     │  - Experiments designed               │       │
│     │  - Quality critique                   │       │
│     │  - Paper synthesized                  │       │
│     │                                       │       │
└─────┴───────────────────────────────────────┴───────┘
```

**Interactions:**
- Auto-scroll conversation (with pause on manual scroll)
- Click message to expand metadata
- Hover agent avatar for info
- Real-time quality score updates
- Iteration counter

**Mobile Responsive:**
- Single column layout
- Horizontal agent scroll
- Collapsible stats section
- Touch-friendly interactions

---

### 3. Research Archive

**Features:**
- Grid of completed research papers
- Sort by date or quality score
- Search/filter (future)
- Paper cards with:
  - Research question
  - Quality score badge
  - Completion date
  - Iteration count
  - Source count
  - Quick actions (View, Open in new tab)

**Stats Dashboard:**
- Total papers
- Average quality score
- Storage usage

---

### 4. Paper Viewer

**Three-Tab Interface:**

#### Tab 1: Paper
- Full markdown-rendered content
- Beautiful typography (@tailwindcss/typography)
- Copy to clipboard button
- Download as .md button
- Proper code block formatting
- Math equations (if present)

#### Tab 2: Meta-Analysis
- **Summary Stats Cards**:
  - Quality score (color-coded)
  - Total iterations
  - Duration
  - Token usage & cost
  
- **Research Details**:
  - Original question
  - Start/completion timestamps
  - Stop reason
  
- **Quality Evolution Chart**:
  - Bar chart showing score progression
  - Color-coded by quality level
  
- **Hypotheses Section**:
  - Top 5 hypotheses with confidence
  - Reasoning and test approaches
  - Expandable for more
  
- **Sources Section**:
  - Top 10 sources with metadata
  - Authors, year, citations
  - Clickable links

#### Tab 3: Conversation
- Full agent message history
- Agent avatars and colors
- Formatted timestamps
- Expandable metadata
- Chronological order

---

## Research Capabilities

### 1. Hypothesis Generation

**Capabilities:**
- Generate 3-5 testable hypotheses
- Assign confidence scores (0-100%)
- Explain reasoning for each
- Propose test approaches
- Relate to existing literature

**Example Output:**
```json
{
  "id": "H1",
  "text": "Quantum entanglement enables faster-than-light information transfer",
  "confidence": 20,
  "reasoning": "Common misconception; violates special relativity",
  "test_approach": "Design Bell test experiment to demonstrate no-communication theorem"
}
```

---

### 2. Experimental Design

**Capabilities:**
- Design experiments for each hypothesis
- Define success criteria
- Estimate resources and time
- Identify potential issues
- Consider ethical implications

**Experiment Components:**
- Method description
- Measurements to collect
- Success/failure criteria
- Time estimate
- Resource requirements
- Potential issues

---

### 3. Quality Evaluation

**Evaluation Criteria:**
1. **Hypothesis Quality** (0-10)
   - Testability
   - Clarity
   - Originality
   
2. **Source Relevance** (0-10)
   - Authority
   - Recency
   - Coverage
   
3. **Experimental Design** (0-10)
   - Rigor
   - Feasibility
   - Completeness
   
4. **Overall Coherence** (0-10)
   - Logical flow
   - Consistency
   - Integration

5. **Completeness** (0-10)
   - Depth
   - Breadth
   - Documentation

**Output:**
- Overall quality score (average of criteria)
- Specific issues identified
- Strengths highlighted
- Recommendations for improvement

---

## System Features

### 1. AWS Bedrock Integration

**Model**: Claude 3.5 Sonnet v2 (via inference profile)

**Features:**
- Automatic retry with exponential backoff (5 attempts)
- Rate limiting with configurable delays
- Token usage tracking
- Cost calculation
- Model invocation logging

**Configuration:**
```bash
AWS_PROFILE=default
AWS_REGION=us-east-1
AWS_BEDROCK_MODEL_ID=us.anthropic.claude-3-5-sonnet-20241022-v2:0
AGENT_INVOCATION_DELAY=2
```

**Rate Limiting:**
- 2-second delay between agent invocations (configurable)
- Exponential backoff on throttling: 2s, 4s, 8s, 16s, 32s
- Graceful degradation on persistent failures

---

### 2. Persistent Storage

**Storage Structure:**
```
backend/storage/papers/
└── {research_id}/
    ├── paper.md           # Final paper (Markdown)
    ├── metadata.json      # Research metadata
    ├── conversation.json  # Full message history
    └── state.json         # Complete research state
```

**Features:**
- Atomic file operations
- Async I/O (aiofiles)
- Cross-platform path handling (pathlib)
- Automatic directory creation
- Idempotent operations

**Metadata Tracking:**
- Question
- Timestamps (start, completion)
- Iteration count
- Quality score history
- Stop reason
- Token usage
- Estimated cost

---

### 3. Error Handling & Resilience

**Strategies:**

1. **Retry Logic**
   - Automatic retry on transient failures
   - Exponential backoff
   - Maximum retry limits

2. **Graceful Degradation**
   - Partial results on search failures
   - Fallback paper generation
   - Continue research on agent errors

3. **Connection Management**
   - SSE automatic reconnection
   - State preservation across reconnections
   - Heartbeat detection (60s timeout)

4. **Logging**
   - Structured logging with Loguru
   - Log levels (DEBUG, INFO, WARNING, ERROR)
   - Contextual information
   - Error stack traces

---

### 4. Performance Features

**Optimizations:**
- Async/await throughout
- Parallel source searches
- Configurable agent delays
- Token usage optimization
- Connection pooling

**Metrics:**
- Request/response times
- Token usage per agent
- Cost per research
- Quality score trends
- Error rates

**Scaling:**
- Stateless backend (except file storage)
- Horizontal scaling capability
- Shared storage (EFS/S3 ready)
- Load balancer compatible

---

## Developer Features

### 1. Comprehensive Logging

**Log Levels:**
```python
logger.debug("Detailed debug information")
logger.info("General information")
logger.warning("Warning messages")
logger.error("Error messages")
```

**Context:**
- Agent names
- Research IDs
- Iteration numbers
- Quality scores
- Token usage
- Timing information

**Output:**
```
2025-10-19 01:33:45 | INFO | The Current generating hypotheses
2025-10-19 01:33:47 | INFO | Tokens used: 1234 input, 567 output
2025-10-19 01:33:47 | WARNING | ⚠️ Throttled by AWS Bedrock. Retrying in 2s...
2025-10-19 01:33:49 | INFO | ✅ Successfully invoked after 2 attempts
```

---

### 2. Testing Framework

**Backend Tests:**
```bash
# Unit tests
pytest backend/tests/unit/ -v

# Integration tests
pytest backend/tests/integration/ -v

# Specific test
pytest backend/tests/unit/test_bedrock_client.py -v

# With coverage
pytest --cov=flux_core --cov-report=html
```

**Frontend Tests:**
```bash
# All tests
npm test

# Watch mode
npm run test:watch

# Coverage
npm run test:coverage

# CI mode
npm run test:ci
```

**Test Coverage:**
- Agent execution
- State management
- API endpoints
- Storage operations
- Error handling
- UI components

---

### 3. Configuration Management

**Environment Variables:**
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

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Validation:**
- Type checking
- Range validation
- Required variables
- Default values

---

### 4. API Documentation

**FastAPI Auto-Generated Docs:**
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

**Features:**
- Interactive API testing
- Request/response schemas
- Authentication (future)
- Example requests

---

### 5. Developer Scripts

**Startup Scripts:**
```bash
# Cross-platform launcher
python start.py

# Mac/Linux
./start.sh

# Windows
start.bat
```

**Cleanup Scripts:**
```bash
# Cross-platform cleanup
python cleanup.py

# Mac/Linux
./cleanup.sh
```

**Testing Scripts:**
```bash
# Backend
cd backend && pytest

# Frontend
cd frontend && npm test

# All
python start.py --test-mode
```

---

## Future Features

### Short-term (Next 3 Months)

#### 1. Database Integration
- PostgreSQL for metadata
- Full-text search across papers
- User research history
- Advanced filtering

#### 2. User Authentication
- OAuth2 (Google, GitHub)
- JWT tokens
- User profiles
- Access control

#### 3. Research Templates
- Quick-start templates
- Domain-specific configurations
- Custom agent prompts
- Saved configurations

#### 4. Export Formats
- PDF generation
- LaTeX export
- Word/DOCX format
- BibTeX citations

#### 5. Collaboration
- Shared research
- Comments and annotations
- Multiple users per research
- Real-time collaboration

---

### Medium-term (3-6 Months)

#### 1. Advanced Search
- Full-text search
- Filter by quality, date, topic
- Tag system
- Saved searches

#### 2. Research Graphs
- Knowledge graph visualization
- Hypothesis relationships
- Source connections
- Research timeline

#### 3. Custom Agents
- User-defined agent types
- Custom system prompts
- Specialized workflows
- Agent marketplace

#### 4. Public API
- RESTful API access
- Webhooks
- Rate limiting
- API keys

#### 5. Analytics Dashboard
- Usage metrics
- Cost tracking
- Quality trends
- Performance insights

---

### Long-term (6-12 Months)

#### 1. Multi-LLM Support
- GPT-4, GPT-4 Turbo
- Google Gemini
- Anthropic Claude (direct)
- Open-source models (Llama, Mixtral)
- Model comparison

#### 2. Distributed Execution
- Kubernetes deployment
- Auto-scaling
- Load balancing
- Multi-region support

#### 3. Research Marketplace
- Public research sharing
- Collaboration tools
- Citation tracking
- Research discovery

#### 4. Real-time Collaboration
- Multiple users on same research
- Live cursors
- Commenting
- Version history

#### 5. Mobile Applications
- iOS native app
- Android native app
- React Native
- Offline support

#### 6. Advanced Features
- Voice input
- Multi-modal research (images, videos)
- Automated literature monitoring
- Research alerts
- Integration with reference managers (Zotero, Mendeley)

---

## Feature Comparison

### Current vs. Future

| Feature | Current | Future |
|---------|---------|--------|
| **Agents** | 6 built-in | + Custom agents |
| **LLM** | Claude 3.5 Sonnet | Multiple LLMs |
| **Storage** | File system | Database + files |
| **Auth** | None | OAuth2 + JWT |
| **Collaboration** | Single user | Multi-user |
| **Export** | Markdown only | PDF, LaTeX, Word |
| **Search** | List view | Full-text search |
| **API** | Internal only | Public API |
| **Deployment** | Local | Cloud + K8s |
| **Mobile** | Responsive web | Native apps |

---

## Conclusion

FLUX provides a comprehensive set of features for AI-powered research:

**Core Strengths:**
1. Multi-agent specialization
2. Iterative quality improvement
3. Real-time transparency
4. Multi-source research
5. Automatic synthesis

**User Benefits:**
1. Fast, comprehensive research
2. High-quality outputs
3. Full process visibility
4. Easy to use
5. Reliable and resilient

**Developer Benefits:**
1. Well-documented codebase
2. Comprehensive testing
3. Easy configuration
4. Extensible architecture
5. Production-ready

The feature set positions FLUX as a powerful tool for automated research while maintaining transparency and user control. The roadmap ensures continuous improvement and expansion of capabilities.

