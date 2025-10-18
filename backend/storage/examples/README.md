# Example Research Papers

This directory contains curated example papers that are checked into git for demonstration purposes.

## Purpose

- Showcase the capabilities of FLUX
- Provide reference examples for users
- Demonstrate research quality and structure
- Available immediately after cloning

## Structure

```
examples/
├── README.md                                    # This file
├── quantum-computing/                           # Example research
│   ├── paper.md                                 # The research paper
│   ├── metadata.json                            # Research metadata
│   ├── conversation.json                        # Agent conversation
│   └── state.json                               # Research state
└── neural-networks/                             # Another example
    ├── paper.md
    ├── metadata.json
    ├── conversation.json
    └── state.json
```

## Adding Example Papers

To add a high-quality research paper as an example:

1. Generate paper normally (it goes to `storage/papers/`)
2. Review the quality and output
3. Copy the research folder to `storage/examples/`:
   ```bash
   cp -r storage/papers/research-abc123 storage/examples/quantum-computing
   ```
4. Clean up sensitive information if needed
5. Commit to git:
   ```bash
   git add storage/examples/quantum-computing
   git commit -m "Add quantum computing example paper"
   ```

## Notes

- Only add **high-quality** papers as examples
- Keep examples **relevant** and **educational**
- Update this README when adding new examples
- Examples should demonstrate different research topics
- Limit to **3-5 examples** to keep repo size manageable

## Current Examples

(None yet - add your first example paper!)

### Example 1: [Topic Name]
- **Question**: Research question
- **Quality Score**: X.X/10
- **Iterations**: N
- **Directory**: `examples/topic-name/`

### Example 2: [Topic Name]
- **Question**: Research question
- **Quality Score**: X.X/10
- **Iterations**: N
- **Directory**: `examples/topic-name/`

