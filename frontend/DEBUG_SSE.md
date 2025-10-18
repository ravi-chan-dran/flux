# Debugging SSE Streaming Issue

## Problem
Frontend shows "loading" indefinitely - never connects to SSE stream.

## Investigation Results

### Backend Status ✅
- Backend IS working and streaming correctly
- Tested with `curl -N` - events are being sent properly
- Sample events:
  - `connected`
  - `research_started`
  - `agent_message`
  - `iteration_complete`

### Frontend Issues Found

1. **Type Mismatch** - ConnectionStatus component expects lowercase strings, but enum values should match
2. **Component Import** - Using `ConnectionStatusOverlay` as alias for `ConnectionStatus`
3. **Enum Values** - Need to verify enum values match component expectations

## Testing Steps

1. Open browser console at http://localhost:3000
2. Start a research
3. Check console for:
   - EventSource connection logs
   - Event data being received
   - State updates
   - Any errors

## Fixes Needed

### Fix 1: Verify ConnectionStatus Enum Values
The enum in `lib/api.ts` should have lowercase string values:

```typescript
export enum ConnectionStatus {
  IDLE = "idle",
  CONNECTING = "connecting",
  CONNECTED = "connected",
  RECONNECTING = "reconnecting",
  ERROR = "error",
  COMPLETE = "complete",
}
```

### Fix 2: Fix Component Import Name
In `app/flow/[id]/page.tsx`:

```typescript
import ConnectionStatus from "@/components/ConnectionStatus";

// Later use:
<ConnectionStatus
  status={connectionStatus}  // Should auto-convert enum to string
  error={error ? new Error(error) : null}
  onRetry={reconnect}
  connectionQuality="good"
/>
```

### Fix 3: Check EventSource URL
Make sure `.env.local` has:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Browser Console Checks

Open DevTools and check:
1. **Network Tab**: Look for EventSource connection to `/api/research/.../stream`
2. **Console**: Check for connection logs from useResearchStream hook
3. **Application Tab**: Check if NEXT_PUBLIC_API_URL is set correctly

## Quick Test

Run this in browser console on the flow page:

```javascript
const es = new EventSource('http://localhost:8000/api/research/test-123/stream?question=test');
es.addEventListener('connected', (e) => console.log('CONNECTED:', e.data));
es.addEventListener('agent_message', (e) => console.log('MESSAGE:', JSON.parse(e.data)));
es.onerror = (e) => console.error('ERROR:', e);
```

If this works, the problem is in the React hook logic.
If this doesn't work, it's a CORS or network issue.

