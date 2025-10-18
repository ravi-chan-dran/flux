# FLUX Documentation

## 📚 Overview

This directory contains comprehensive design documentation for the FLUX (Flow-based Learning Understanding eXchange) multi-agent research system.

## 📖 Documentation Structure

```
docs/
├── index.html                  # Documentation portal (START HERE)
├── styles.css                  # Styling for HTML documentation
├── convert_to_html.py          # Markdown to HTML converter
│
├── ARCHITECTURE.md/.html       # High-level system architecture
├── TECHNICAL_DESIGN.md/.html   # Low-level implementation details
├── SEQUENCE_DIAGRAMS.md/.html  # Interaction flow diagrams
├── FEATURES.md/.html           # Feature documentation
│
└── README.md                   # This file
```

## 🚀 Quick Start

### Viewing HTML Documentation

1. **Open the documentation portal:**
   ```bash
   open docs/index.html
   # Or on Windows: start docs/index.html
   # Or on Linux: xdg-open docs/index.html
   ```

2. **Or view directly in browser:**
   ```
   file:///path/to/flux/docs/index.html
   ```

3. **Or use a local server:**
   ```bash
   cd docs
   python3 -m http.server 8001
   # Then open http://localhost:8001
   ```

### Viewing Markdown Documentation

All documentation is available in both **Markdown** (.md) and **HTML** (.html) formats.

**Markdown files can be viewed:**
- In VS Code with markdown preview
- In GitHub/GitLab web interface
- With any markdown viewer
- Raw text editor

**HTML files provide:**
- Beautiful styling with dark theme
- Interactive diagrams (Mermaid)
- Print-friendly format
- Navigation between documents
- Download and view source options

## 📋 Documentation Contents

### 1. [ARCHITECTURE](ARCHITECTURE.md) | [HTML](ARCHITECTURE.html)
**System architecture and design**

Topics covered:
- System overview and philosophy
- High-level architecture diagram
- Component architecture (Frontend & Backend)
- Data flow patterns
- Technology stack
- Deployment architecture
- Security architecture
- Performance characteristics
- Reliability & resilience
- Future enhancements

**Audience:** Architects, Technical Leads, Stakeholders

---

### 2. [TECHNICAL_DESIGN](TECHNICAL_DESIGN.md) | [HTML](TECHNICAL_DESIGN.html)
**Implementation details and low-level design**

Topics covered:
- Agent system design (Base Agent + 6 specialized agents)
- State management (ResearchState TypedDict)
- LangGraph workflow implementation
- API design and endpoints
- Real-time streaming (SSE)
- Storage system
- Error handling & resilience
- Performance optimization
- Configuration management

**Audience:** Developers, Engineers, Implementation Teams

---

### 3. [SEQUENCE_DIAGRAMS](SEQUENCE_DIAGRAMS.md) | [HTML](SEQUENCE_DIAGRAMS.html)
**Visual interaction flows**

Diagrams included:
1. Complete research flow
2. Research initiation
3. SSE streaming connection
4. Orbital iteration cycle
5. Agent execution flow
6. Error handling & retry
7. Multi-source search flow
8. Paper retrieval flow
9. Frontend state management
10. Authentication flow (future)

**Format:** Mermaid diagrams (interactive in HTML)

**Audience:** All technical staff, Visual learners

---

### 4. [FEATURES](FEATURES.md) | [HTML](FEATURES.html)
**Feature documentation and roadmap**

Topics covered:
- Core features (Multi-agent, Orbital Iteration, Real-time Theater)
- User interface features
- Research capabilities
- System features
- Developer features
- Future features (Short/Medium/Long-term roadmap)
- Feature comparison table

**Audience:** Product Managers, Users, Business Stakeholders

## 🎨 Styling and Customization

### HTML Styling

The HTML documentation uses a dark theme with cyan accents (`styles.css`).

**Color scheme:**
- Primary: #06B6D4 (cyan)
- Secondary: #9333EA (purple)
- Background: #0F172A (dark slate)
- Text: #F1F5F9 (light)

**To customize styling:**
Edit `styles.css` and update the `:root` CSS variables.

### Mermaid Diagrams

Sequence diagrams are rendered using [Mermaid.js](https://mermaid.js.org/).

**In HTML:**
- Automatically rendered with dark theme
- Interactive (hover, zoom)

**In Markdown:**
- Rendered by compatible viewers (GitHub, VS Code with Mermaid extension)
- Shows raw code in basic markdown viewers

## 🔧 Regenerating HTML

If you update the markdown files and need to regenerate HTML:

```bash
cd docs
python3 convert_to_html.py
```

**What it does:**
- Reads all `.md` files
- Generates corresponding `.html` files
- Preserves markdown source
- Adds navigation and styling
- Enables Mermaid diagram rendering

## 📱 Responsive Design

All HTML documentation is fully responsive:
- **Desktop:** Full navigation, sidebar, multi-column layouts
- **Tablet:** Optimized spacing, collapsible sections
- **Mobile:** Single column, touch-friendly, hamburger menus

## 🖨️ Printing

HTML documentation includes print-optimized styles:
1. Open any HTML file in browser
2. Use browser's print function (Ctrl/Cmd + P)
3. Select "Save as PDF" or print directly

**Print features:**
- Removes navigation and interactive elements
- Optimizes for paper
- Preserves diagrams and code blocks
- Black and white friendly

## 🔗 External References

### Related Documentation
- [Main README](../README.md) - Project overview and setup
- [CHANGELOG](../CHANGELOG.md) - Version history
- [AWS Throttling Guide](../AWS_THROTTLING_GUIDE.md) - Throttling solutions
- [Throttling Fix Summary](../THROTTLING_FIX_SUMMARY.md) - Quick reference

### Online Documentation
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [LangGraph Docs](https://python.langchain.com/docs/langgraph)
- [Next.js Docs](https://nextjs.org/docs)
- [AWS Bedrock Docs](https://docs.aws.amazon.com/bedrock/)
- [Mermaid Docs](https://mermaid.js.org/)

## 🤝 Contributing to Documentation

### Adding New Documentation

1. **Create markdown file:**
   ```bash
   touch docs/NEW_DOCUMENT.md
   ```

2. **Write content in markdown**

3. **Update conversion script:**
   Edit `convert_to_html.py` and add to `markdown_files` list

4. **Generate HTML:**
   ```bash
   python3 docs/convert_to_html.py
   ```

5. **Update index.html:**
   Add link to new document in the documentation portal

### Documentation Standards

**Markdown Guidelines:**
- Use ATX-style headers (`#`, `##`, etc.)
- Include table of contents for long documents
- Use code blocks with language specification
- Include examples and use cases
- Add visual diagrams where helpful
- Keep paragraphs concise
- Use lists for scanability

**Diagram Guidelines:**
- Use Mermaid for sequence diagrams
- Use ASCII art for simple diagrams
- Use code blocks for file structures
- Keep diagrams focused and readable
- Add descriptions for complex diagrams

## 📊 Documentation Metrics

| Document | Lines | Sections | Topics | Diagrams |
|----------|-------|----------|---------|----------|
| ARCHITECTURE | ~600 | 10 | 30+ | 5 |
| TECHNICAL_DESIGN | ~800 | 8 | 40+ | 3 |
| SEQUENCE_DIAGRAMS | ~700 | 9 | 10+ | 10 |
| FEATURES | ~900 | 6 | 50+ | 2 |
| **TOTAL** | **~3000** | **33** | **130+** | **20** |

## 🎯 Documentation Goals

✅ **Comprehensive** - Covers all aspects of the system

✅ **Accessible** - Multiple formats (MD + HTML)

✅ **Visual** - Diagrams and flowcharts

✅ **Practical** - Code examples and configurations

✅ **Current** - Updated with each release

✅ **Navigable** - Clear structure and cross-references

✅ **Professional** - Publication-ready quality

## 📝 Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-10-19 | Initial comprehensive documentation release |

## 📧 Feedback

Found an issue or have suggestions for improving the documentation?

- Create an issue in the project repository
- Submit a pull request with corrections
- Contact the development team

---

## 📖 Quick Navigation

**Start Here:**
- [Documentation Portal (HTML)](index.html) 👈 **RECOMMENDED**

**Core Documents:**
- [Architecture](ARCHITECTURE.html) - System design
- [Technical Design](TECHNICAL_DESIGN.html) - Implementation
- [Sequence Diagrams](SEQUENCE_DIAGRAMS.html) - Interaction flows
- [Features](FEATURES.html) - Capabilities

**Markdown Versions:**
- [Architecture (MD)](ARCHITECTURE.md)
- [Technical Design (MD)](TECHNICAL_DESIGN.md)
- [Sequence Diagrams (MD)](SEQUENCE_DIAGRAMS.md)
- [Features (MD)](FEATURES.md)

---

<div align="center">

**FLUX Documentation**

*Comprehensive, Visual, Professional*

Made with ❤️ for the FLUX project

</div>

