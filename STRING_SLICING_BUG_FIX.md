# String Slicing Bug Fix

## Error
```
2025-10-20 02:00:38 | ERROR | flux_core.graph.research_graph:filter_node:295 - 🛡️ The Filter error: slice(None, 150, None)
```

## Root Cause
Multiple agent formatting methods were attempting to slice the result of `.get()` operations without ensuring the value was a string first. When `.get()` returned `None` or a non-string object, the slice operation `[:N]` would fail with a confusing error message like "slice(None, 150, None)".

## Vulnerable Code Pattern
```python
# BAD - Will fail if method is None
method = exp.get("method", "N/A")[:150]

# BAD - Will fail if abstract is None  
abstract = s.get("abstract", "")[:200]
```

## Fixes Applied

### 1. FilterAgent (`backend/flux_core/agents/filter.py`)
**Line 388-391** - `_format_experiments` method:
```python
# Before
method = exp.get("method", "N/A")[:150]

# After
method = exp.get("method", "N/A")
method_str = str(method) if method is not None else "N/A"
formatted.append(f"- {hyp_id}: {method_str[:150]}...")
```

### 2. ChannelAgent (`backend/flux_core/agents/channel.py`)
**Line 256** - `_fallback_experiments` method:
```python
# Before
"method": f"Design experimental method to test: {hyp.get('text', 'hypothesis')[:100]}"

# After
"method": f"Design experimental method to test: {str(hyp.get('text', 'hypothesis'))[:100]}"
```

**Line 282-284** - `_format_experiments_for_prompt` method:
```python
# Before
formatted.append(
    f"- {exp.get('hypothesis_id', '?')}: {exp.get('method', 'N/A')[:200]}"
)

# After
method = str(exp.get('method', 'N/A'))
formatted.append(
    f"- {exp.get('hypothesis_id', '?')}: {method[:200]}"
)
```

### 3. ConfluenceAgent (`backend/flux_core/agents/confluence.py`)
**Line 296** - `_format_sources` method:
```python
# Before
abstract = s.get("abstract", "")[:200]

# After
abstract = str(s.get("abstract", ""))[:200] if s.get("abstract") else ""
```

### 4. SourceAgent (`backend/flux_core/agents/source.py`)
**Line 229-230** - `_format_sources_for_prompt` method:
```python
# Before
abstract = source.get("abstract", source.get("content", ""))[:300]

# After
abstract_raw = source.get("abstract", source.get("content", ""))
abstract = str(abstract_raw)[:300] if abstract_raw else ""
```

## Safe String Slicing Pattern
When slicing dictionary values, always ensure they're strings first:

```python
# Pattern 1: Simple case
value = str(data.get("field", "default"))[:N]

# Pattern 2: With None check
raw_value = data.get("field", "default")
value = str(raw_value)[:N] if raw_value else "default"

# Pattern 3: Inline with ternary
value = str(data.get("field", ""))[:N] if data.get("field") else ""
```

## Impact
- ✅ Prevents TypeError when formatting experiments with None values
- ✅ Prevents slice object errors in all agent formatting methods
- ✅ Ensures robust string handling across all agents
- ✅ No impact on existing functionality - backward compatible

## Testing
All fixed methods are called during normal research workflow:
- FilterAgent: Called in every iteration for quality evaluation
- ChannelAgent: Called when designing experiments
- ConfluenceAgent: Called when generating final paper
- SourceAgent: Called when searching and formatting sources

## Files Modified
- ✅ `backend/flux_core/agents/filter.py`
- ✅ `backend/flux_core/agents/channel.py`
- ✅ `backend/flux_core/agents/confluence.py`
- ✅ `backend/flux_core/agents/source.py`

## Prevention
To avoid similar issues in the future:
1. Always use `str()` before slicing dictionary values
2. Check for None before slicing
3. Use proper defaults in `.get()` calls
4. Test with empty/None data

