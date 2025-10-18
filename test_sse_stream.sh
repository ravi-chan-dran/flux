#!/bin/bash

# Test SSE Streaming Endpoint
# This script tests the Server-Sent Events streaming functionality

echo "======================================"
echo "  FLUX SSE Streaming Test"
echo "======================================"
echo ""

# Configuration
BACKEND_URL="http://localhost:8000"
RESEARCH_ID="test-$(date +%s)"
QUESTION="How does quantum entanglement work?"

echo "Backend URL: $BACKEND_URL"
echo "Research ID: $RESEARCH_ID"
echo "Question: $QUESTION"
echo ""
echo "Press Ctrl+C to stop"
echo "--------------------------------------"
echo ""

# URL encode the question
ENCODED_QUESTION=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$QUESTION'))")

# Stream the research progress
curl -N "${BACKEND_URL}/api/research/${RESEARCH_ID}/stream?question=${ENCODED_QUESTION}" 2>/dev/null | while IFS= read -r line; do
    # Check if line starts with "data: "
    if [[ $line == data:* ]]; then
        # Extract JSON data (remove "data: " prefix)
        json_data="${line#data: }"
        
        # Pretty print with Python
        echo "$json_data" | python3 -m json.tool --no-ensure-ascii 2>/dev/null || echo "$json_data"
        echo "---"
    fi
done

echo ""
echo "Stream ended"

