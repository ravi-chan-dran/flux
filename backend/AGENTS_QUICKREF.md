# FLUX Agents - Quick Reference

## 🎭 The Research Team

| Agent | Role | When Used | Key Output |
|-------|------|-----------|------------|
| 🧑‍💼 **Flow Master** | Orchestrator | Every step | Routes to next agent |
| 💡 **The Current** | Theorist | Generate/refine hypotheses | List of hypotheses |
| 📚 **The Source** | Librarian | Search literature | Sources + synthesis |
| 🔬 **The Channel** | Experimenter | Design tests | Experiment protocols |
| 🛡️ **The Filter** | Critic | Evaluate quality | Quality score + critique |
| ✍️ **The Confluence** | Writer | Final synthesis | Research paper |

---

## 📊 Quick Usage

### Import All Agents
```python
from flux_core.agents import (
    FlowMasterAgent, CurrentAgent, SourceAgent,
    ChannelAgent, FilterAgent, ConfluenceAgent
)
```

### Initialize Agents
```python
flow_master = FlowMasterAgent()
current = CurrentAgent()
source = SourceAgent()
channel = ChannelAgent()
filter_agent = FilterAgent()
confluence = ConfluenceAgent()
```

---

## 🔄 Research Flow Pattern

```python
# 1. Flow Master decides where to start
next_action = await flow_master.decide_next_step(state)

# 2. Execute based on routing
if next_action == "current":
    hypotheses = await current.generate_hypotheses(question, context, iteration)
    
elif next_action == "source":
    research = await source.search_research(question, context, iteration)
    
elif next_action == "channel":
    experiments = await channel.design_experiments(hypotheses, sources, iteration)
    
elif next_action == "filter":
    critique = await filter_agent.review(state)
    
elif next_action == "confluence":
    paper = await confluence.write_paper(state)
```

---

## 📝 Agent Methods Cheat Sheet

### Flow Master 🧑‍💼
```python
# Analyze question and create plan
analysis = await flow_master.analyze_question(question)

# Decide next step in workflow
next_action = await flow_master.decide_next_step(state)
# Returns: "current" | "source" | "channel" | "filter" | "confluence"

# Check if should continue
should_continue, reason = await flow_master.should_continue_research(state)

# Generate routing message
message = await flow_master.generate_routing_message(state, next_action)
```

### The Current 💡
```python
# Generate or refine hypotheses
hypotheses = await current.generate_hypotheses(
    question="How does X work?",
    context={"existing_hypotheses": [...], "critiques": [...]},
    iteration=0  # 0 = new, 1+ = refine
)

# Returns list of dicts:
# [{
#     "id": "h1",
#     "text": "Hypothesis statement",
#     "confidence": 85,
#     "reasoning": "Why this makes sense",
#     "test_approach": "How to test it"
# }, ...]
```

### The Source 📚
```python
# Search and synthesize research
research = await source.search_research(
    question="Research question",
    context={"existing_hypotheses": [...]},
    iteration=0,
    limit=10
)

# Returns:
# {
#     "sources": [list of papers],
#     "synthesis": {
#         "summary": "Overview",
#         "key_themes": [...],
#         "research_gaps": [...],
#         "relevance": "How it relates",
#         "contradictions": [...]
#     },
#     "search_query": "actual query",
#     "source_count": 10
# }

# Helper methods
urls = source.get_source_urls(sources)
citations = source.format_sources_for_paper(sources)
```

### The Channel 🔬
```python
# Design experiments
experiments = await channel.design_experiments(
    hypotheses=[...],
    sources=[...],  # Optional context
    iteration=0,
    context={"existing_experiments": [...]}
)

# Returns list of dicts:
# [{
#     "hypothesis_id": "h1",
#     "method": "Step-by-step procedure",
#     "measurements": "What to measure",
#     "success_criteria": "How to validate",
#     "time_estimate": "Duration",
#     "potential_issues": "Risks"
# }, ...]
```

### The Filter 🛡️
```python
# Review research quality
critique = await filter_agent.review(state)

# Returns:
# {
#     "quality_score": 7.5,  # 0-10
#     "issues": ["Problem 1", "Problem 2"],
#     "strengths": ["Strength 1", "Strength 2"],
#     "recommendations": ["Fix 1", "Fix 2"],
#     "raw_critique": "Full text"
# }

# Helper methods
score = filter_agent.calculate_quality_score(text)
issues = filter_agent.extract_issues(text)
```

### The Confluence ✍️
```python
# Write final paper
paper = await confluence.write_paper(state)
# Returns markdown-formatted research paper

# Get metadata
metadata = confluence.get_paper_metadata(state, paper)
# Returns dict with word count, iterations, scores, etc.
```

---

## 🎯 State Requirements

### Minimal State
```python
state = {
    "question": "Research question",
    "research_id": "unique-id",
    "iteration": 0,
    "max_iterations": 3,
    "quality_score": 0.0,
    "quality_threshold": 8.0,
    "improvement_threshold": 0.5,
    "phase": "initialize",
    "hypotheses": [],
    "sources": [],
    "experiments": [],
    "critiques": [],
    "quality_history": [],
}
```

---

## 🚦 Stopping Conditions

Research stops when ANY of these are true:

1. **Max Iterations Reached**
   ```python
   state["iteration"] >= state["max_iterations"]
   ```

2. **Quality Threshold Met**
   ```python
   state["quality_score"] >= state["quality_threshold"]
   ```

3. **Insufficient Improvement**
   ```python
   improvement < state["improvement_threshold"]
   ```

---

## 💬 Agent Metaphors

### Flow Master 🧑‍💼 - Flow/Stream
- "The current flows strong..."
- "Channeling the stream..."
- "Waters are clear..."
- "Ready to confluence..."

### The Current 💡 - Energy/Spark
- "A spark of insight..."
- "Energy builds around..."
- "Charged with potential..."
- "Current of thought flows..."

### The Source 📚 - Upstream/Tributaries
- "From upstream sources..."
- "Tributaries of knowledge..."
- "Drawing from deep wells..."
- "Tracing back to foundations..."

### The Channel 🔬 - Pipeline/Conduit
- "Channeling hypothesis through..."
- "Experimental pipeline..."
- "Data flows through conduits..."
- "Conducting investigation..."

### The Filter 🛡️ - Signal/Noise
- "Filtering through noise..."
- "Signal is clear in..."
- "Passes quality filter..."
- "Blocking turbidity..."

### The Confluence ✍️ - Merge/Integration
- "Where streams converge..."
- "Confluence of ideas..."
- "Merging insights..."
- "Integrated flow shows..."

---

## 🧪 Testing

```python
# Run all agent tests
pytest tests/unit/test_agents.py -v

# Run specific agent tests
pytest tests/unit/test_agents.py::TestFlowMasterAgent -v
pytest tests/unit/test_agents.py::TestFilterAgent::test_calculate_quality_score -v

# With coverage
pytest tests/unit/test_agents.py --cov=flux_core.agents
```

---

## 📦 Files

```
flux_core/agents/
├── __init__.py         # Exports all agents
├── base_agent.py       # Abstract base class
├── flow_master.py      # Orchestrator
├── current.py          # Hypothesis generator
├── source.py           # Research searcher
├── channel.py          # Experiment designer
├── filter.py           # Quality critic
└── confluence.py       # Paper synthesizer
```

---

## ⚡ Pro Tips

1. **Always check quality score** after Filter reviews
2. **Use iteration number** to change agent behavior
3. **Pass context** between agents via state
4. **Track conversation history** for debugging
5. **Handle LLM failures** gracefully with fallbacks
6. **Stream responses** for real-time UI updates
7. **Format messages** with agent metadata for attribution

---

## 🎨 Color Scheme

Use these colors in UI:
- 🧑‍💼 Purple (`#9333EA`)
- 💡 Cyan (`#06B6D4`)
- 📚 Amber (`#F59E0B`)
- 🔬 Teal (`#14B8A6`)
- 🛡️ Red (`#EF4444`)
- ✍️ Indigo (`#6366F1`)

---

**Ready to research!** 🚀

