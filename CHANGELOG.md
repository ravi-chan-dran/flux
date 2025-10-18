# FLUX Changelog

All notable changes to the FLUX project are documented in this file.

## [Unreleased] - 2025-10-18

### Added
- **Research Archive Page**: Browse all completed research papers at `/research`
  - View all past research in a card grid layout
  - Sort by date or quality score
  - See metadata: quality score, date completed, iterations, sources count
  - Quick actions: View paper, open in new tab
  - Empty state with helpful guidance for first-time users
  - Accessible from homepage via "📚 Research Archive" button
- **Persistent Live Theater View**: Research theater stays visible after completion
  - Celebration auto-dismisses after 3 seconds
  - "View Paper" button opens in new tab (doesn't lose research view)
  - Floating action buttons for easy access to paper and home
  - Can review entire research process even after completion
- **Cleanup Scripts**: Created `cleanup.py` (cross-platform) and `cleanup.sh` (Mac/Linux) to stop all FLUX processes
- **Frontend Testing**: Comprehensive test suite for Live Theater page with 20+ test cases
- **Environment Configuration**: Added `.env.example` with detailed configuration comments
- **Mobile Responsiveness**: Full mobile/tablet support for all frontend pages

### Changed
- **DEFAULT MAX_ITERATIONS**: Changed from 3 to 1 for faster, cheaper research by default
  - Single orbit through all agents instead of 3
  - Reduces looping behavior
  - Users can still override via `.env` or API
- **AWS Bedrock Model ID**: Updated to use inference profile `us.anthropic.claude-3-5-sonnet-20241022-v2:0`
  - Required for Claude 3.5 Sonnet v2 access
  - Better availability with cross-region routing
- **AWS Authentication**: Switched from access keys to AWS profiles for better security
  - Use `AWS_PROFILE` instead of `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY`
  - Run `aws configure` to set up profiles

### Fixed
- **SSE Connection Loop**: Fixed React hook dependency causing infinite reconnection
  - Used `useRef` for callbacks to prevent unnecessary re-renders
  - Connection now stable and stays open
- **Frontend 404 Error**: Created missing `app/layout.tsx` for Next.js routing
- **Missing .env.local**: Added with `NEXT_PUBLIC_API_URL` for proper SSE connection
- **Dependency Conflicts**: Resolved boto3/botocore version conflicts with langchain-aws
- **Port Conflicts**: Cleanup scripts prevent "address already in use" errors

### Technical Details

#### Environment Variables
```bash
# AWS (Required)
AWS_PROFILE=default
AWS_REGION=us-east-1
AWS_BEDROCK_MODEL_ID=us.anthropic.claude-3-5-sonnet-20241022-v2:0

# Research Configuration
MAX_ITERATIONS=1               # Changed from 3
QUALITY_THRESHOLD=8.0
IMPROVEMENT_THRESHOLD=0.5

# Optional
TAVILY_API_KEY=your_key        # For web search
LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:3000
```

#### Cleanup Commands
```bash
# Stop all FLUX processes
python3 cleanup.py             # Cross-platform (recommended)
./cleanup.sh                   # Mac/Linux only

# Restart
python start.py                # All platforms
```

#### Testing
```bash
# Backend tests
cd backend
pytest                         # Run all tests
pytest --cov=flux_core         # With coverage

# Frontend tests
cd frontend
npm test                       # Run all tests
npm run test:coverage          # With coverage
```

### Known Issues
None at this time.

---

## Version History

### Initial Release
- Multi-agent research system with 6 specialized agents
- Orbital iteration workflow using LangGraph
- FastAPI backend with SSE streaming
- Next.js 14 frontend with live research theater
- Integration with AWS Bedrock (Claude 3.5 Sonnet)
- Multi-source research (Semantic Scholar, ArXiv, Tavily)
- Quality-driven stopping conditions
- Full cross-platform support (Mac, Linux, Windows)

---

## Contributing

When making changes:
1. Update this CHANGELOG.md with your changes
2. Follow the format: Added/Changed/Fixed/Removed
3. Include technical details if needed
4. Keep it concise and user-focused

---

## Documentation

- **README.md** - Main project documentation and setup guide
- **CLEANUP_GUIDE.md** - How to stop/restart FLUX processes
- **backend/README.md** - Backend-specific documentation
- **backend/AGENTS_IMPLEMENTATION.md** - Agent system details
- **frontend/tests/README.md** - Testing guide

