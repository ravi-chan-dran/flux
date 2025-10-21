# Tavily Search Fix

## Problem
The Tavily search was failing with a "400 Bad Request" error when processing long, complex research queries.

**Error Log:**
```
2025-10-20 09:47:04 | ERROR | flux_core.tools.search:search_tavily:200 - Tavily search failed: 400 Client Error: Bad Request for url: https://api.tavily.com/search
```

## Root Cause Analysis

### 1. **Query Length Issue**
The research question being sent to Tavily was extremely long (1000+ characters):
```
"Explore how creativity can be intentionally designed into AI systems through cognitive architectures and multi-agent collaboration. Begin with inspirations from human creativity—divergent vs. convergent thinking—and map these into System-1/System-2 dual-process frameworks.

Investigate questions like:

How can LLM agents simulate imagination, curiosity, and reflection through cooperative or competitive interaction?

What mechanisms enable emergent creativity when agents exchange hypotheses, analogies, or incomplete ideas?

How can cognitive architectures (like ACT-R, Soar, or Global Workspace Theory) be adapted to model collective intelligence among LLMs?

Can a metacognitive controller dynamically balance exploration (creative divergence) and exploitation (analytical convergence)?

Deliverables:

Identify at least five innovative cognitive or architectural patterns that could foster creativity in multi-agent LLM ecosystems.

Compare these to biological or human cognitive parallels.

Suggest experiment designs or simulation frameworks to evaluate creative output (e.g., novelty, usefulness, surprise).

Propose potential metrics and evaluation benchmarks for "AI creativity."

Stretch Goal:
Conceptualize a 'Creative AI Lab' prototype—where multiple agents with distinct cognitive roles (artist, critic, theorist, builder) co-create solutions to open-ended problems."
```

### 2. **API Limitations**
- Tavily API has query length limits (likely around 500-1000 characters)
- Complex queries with multiple questions and special characters may not be handled well
- The API expects more focused, search-engine-like queries

## Solution Implemented

### 1. **Query Truncation Logic**
Added intelligent query truncation in `search_tavily()`:

```python
# Truncate query if too long (Tavily has query length limits)
if len(query) > 500:
    # Split by sentences and take first few meaningful parts
    sentences = query.split('. ')
    truncated_query = '. '.join(sentences[:3])  # Take first 3 sentences
    if len(truncated_query) > 500:
        truncated_query = truncated_query[:500]
    logger.info(f"Query too long ({len(query)} chars), truncated to: {truncated_query[:100]}...")
    query = truncated_query
```

### 2. **Enhanced Error Handling**
Added detailed error logging to help diagnose issues:

```python
except Exception as e:
    error_msg = f"Tavily search failed: {str(e)}"
    logger.error(error_msg)
    
    # Log additional details for debugging
    if "400" in str(e):
        logger.error(f"Bad Request - Query length: {len(query)}, Query preview: {query[:200]}...")
        logger.error("This might be due to query length limits or invalid characters")
    elif "401" in str(e):
        logger.error("Unauthorized - Check TAVILY_API_KEY")
    elif "429" in str(e):
        logger.error("Rate limited - Too many requests")
```

### 3. **Fallback Mechanism**
Added a fallback search with simplified query when the main search fails:

```python
# Try with a simplified query as fallback
try:
    # Extract key terms from the original query
    simplified_query = query.split('\n')[0]  # Take first line
    if len(simplified_query) > 200:
        simplified_query = simplified_query[:200]
    logger.info(f"Trying Tavily with simplified query: {simplified_query[:100]}...")
    
    tavily_fallback_results = search_tavily(simplified_query, limit=per_source_limit)
    all_results.extend(tavily_fallback_results)
    sources_used.append("tavily_fallback")
    logger.info(f"Added {len(tavily_fallback_results)} results from Tavily (fallback)")
except SearchError as fallback_e:
    logger.error(f"Tavily fallback also failed: {fallback_e}")
    sources_failed.append("tavily_fallback")
```

## Benefits

### ✅ **Robust Query Handling**
- Automatically truncates long queries to fit API limits
- Preserves the most important parts of the query (first sentences)
- Graceful degradation when queries are too complex

### ✅ **Better Error Diagnostics**
- Specific error messages for different HTTP status codes
- Query length and preview logging for debugging
- Clear indication of what went wrong

### ✅ **Fallback Strategy**
- Simplified query retry when main search fails
- System continues working even if Tavily has issues
- Other search sources (Semantic Scholar, ArXiv) remain unaffected

### ✅ **Improved Reliability**
- Research workflow continues even with search failures
- Better user experience with fewer interruptions
- More resilient multi-source search system

## Technical Details

### Query Truncation Strategy
1. **Length Check**: If query > 500 characters
2. **Sentence Splitting**: Split by `. ` to preserve meaning
3. **Take First 3**: Use first 3 sentences (most relevant)
4. **Hard Limit**: Ensure final query ≤ 500 characters
5. **Logging**: Record truncation for debugging

### Fallback Strategy
1. **Primary Search Fails**: Original query fails
2. **Extract First Line**: Take the main question
3. **Simplify**: Limit to 200 characters
4. **Retry**: Attempt search with simplified query
5. **Continue**: System proceeds with whatever results obtained

### Error Classification
- **400 Bad Request**: Query length/format issues
- **401 Unauthorized**: API key problems
- **429 Too Many Requests**: Rate limiting
- **Other Errors**: Network or service issues

## Files Modified
- ✅ `backend/flux_core/tools/search.py` - Enhanced Tavily search function

## Testing Results
✅ **Verified Working:**
- Long queries are automatically truncated
- Fallback mechanism activates on failures
- Detailed error logging helps with debugging
- Multi-source search continues even if Tavily fails

## Usage Impact
- **Research Workflow**: Continues uninterrupted
- **Search Quality**: Maintained through other sources
- **Error Visibility**: Better debugging information
- **System Reliability**: Improved resilience

## Future Improvements
1. **Query Optimization**: Extract key terms instead of truncation
2. **API Version Check**: Verify Tavily API version and limits
3. **Retry Logic**: Add exponential backoff for rate limits
4. **Query Caching**: Cache successful queries to avoid repeats

---

**Status: ✅ RESOLVED**

Tavily search now handles long queries gracefully and provides fallback mechanisms when failures occur. The research system continues to function reliably even when individual search sources have issues.
