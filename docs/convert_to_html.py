#!/usr/bin/env python3
"""
Convert markdown documentation files to HTML with Mermaid support.
"""

import os
import json
from pathlib import Path

# HTML template with Mermaid support
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - FLUX Documentation</title>
    <link rel="stylesheet" href="styles.css">
    <script src="https://cdn.jsdelivr.net/npm/marked@11.0.0/lib/marked.umd.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10.6.1/dist/mermaid.min.js"></script>
    <style>
        .markdown-body {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        
        .back-link {{
            display: inline-block;
            margin-bottom: 1rem;
            color: var(--primary);
            text-decoration: none;
            padding: 0.5rem 1rem;
            background: var(--background-light);
            border-radius: 0.5rem;
            transition: all 0.3s ease;
        }}
        
        .back-link:hover {{
            background: var(--background-lighter);
            transform: translateX(-4px);
        }}
        
        .doc-actions {{
            display: flex;
            gap: 1rem;
            margin-bottom: 2rem;
            flex-wrap: wrap;
        }}
        
        .btn {{
            padding: 0.5rem 1rem;
            border-radius: 0.5rem;
            border: 1px solid var(--border);
            background: var(--background-light);
            color: var(--text);
            text-decoration: none;
            cursor: pointer;
            transition: all 0.3s ease;
        }}
        
        .btn:hover {{
            background: var(--background-lighter);
            border-color: var(--primary);
            color: var(--primary);
        }}
    </style>
</head>
<body>
    <header>
        <div class="container">
            <h1>🌊 FLUX</h1>
            <p>Flow-based Learning Understanding eXchange - Documentation</p>
        </div>
    </header>

    <nav>
        <div class="container">
            <a href="index.html">Home</a>
            <a href="ARCHITECTURE.html" class="{arch_active}">Architecture</a>
            <a href="TECHNICAL_DESIGN.html" class="{tech_active}">Technical Design</a>
            <a href="SEQUENCE_DIAGRAMS.html" class="{seq_active}">Sequence Diagrams</a>
            <a href="FEATURES.html" class="{feat_active}">Features</a>
        </div>
    </nav>

    <main>
        <a href="index.html" class="back-link">← Back to Documentation Home</a>
        
        <div class="doc-actions">
            <a href="{md_file}" class="btn" download>📥 Download Markdown</a>
            <a href="{md_file}" class="btn" target="_blank">📄 View Markdown</a>
            <button class="btn" onclick="window.print()">🖨️ Print</button>
        </div>
        
        <div id="content" class="markdown-body"></div>
    </main>

    <footer>
        <div class="container">
            <p>&copy; 2025 FLUX - Flow-based Learning Understanding eXchange</p>
            <p class="text-muted">Multi-agent AI research system powered by orbital iteration</p>
        </div>
    </footer>

    <script>
        // Initialize Mermaid
        mermaid.initialize({{
            startOnLoad: false,
            theme: 'dark',
            themeVariables: {{
                primaryColor: '#06B6D4',
                primaryTextColor: '#F1F5F9',
                primaryBorderColor: '#0891B2',
                lineColor: '#06B6D4',
                secondaryColor: '#1E293B',
                tertiaryColor: '#334155',
                background: '#0F172A',
                mainBkg: '#1E293B',
                textColor: '#F1F5F9',
                fontSize: '16px',
            }}
        }});

        // Render embedded markdown
        const markdown = {markdown_json};
        
        // Parse markdown to HTML
        const html = marked.parse(markdown);
        
        // Replace mermaid code blocks with divs
        const processed = html.replace(
            /<pre><code class="language-mermaid">(.*?)<\\/code><\\/pre>/gs,
            '<div class="mermaid">$1</div>'
        );
        
        document.getElementById('content').innerHTML = processed;
        
        // Render mermaid diagrams
        mermaid.run({{
            querySelector: '.mermaid'
        }});
        
        // Smooth scroll for anchor links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {{
            anchor.addEventListener('click', function (e) {{
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {{
                    target.scrollIntoView({{
                        behavior: 'smooth',
                        block: 'start'
                    }});
                }}
            }});
        }});
    </script>
</body>
</html>
"""

def convert_markdown_to_html(md_file: Path, docs_dir: Path):
    """Convert a markdown file to HTML."""
    
    # Read markdown content
    md_content = md_file.read_text(encoding='utf-8')
    
    # Extract title from first # heading
    title = "Documentation"
    for line in md_content.split('\n'):
        if line.startswith('# '):
            title = line[2:].strip()
            break
    
    # Determine active nav link
    filename = md_file.stem
    nav_active = {
        'arch_active': 'active' if filename == 'ARCHITECTURE' else '',
        'tech_active': 'active' if filename == 'TECHNICAL_DESIGN' else '',
        'seq_active': 'active' if filename == 'SEQUENCE_DIAGRAMS' else '',
        'feat_active': 'active' if filename == 'FEATURES' else '',
    }
    
    # Escape markdown content for JavaScript JSON
    markdown_json = json.dumps(md_content)
    
    # Generate HTML with embedded markdown
    html_content = HTML_TEMPLATE.format(
        title=title,
        md_file=md_file.name,
        markdown_json=markdown_json,
        **nav_active
    )
    
    # Write HTML file
    html_file = docs_dir / f"{filename}.html"
    html_file.write_text(html_content, encoding='utf-8')
    
    print(f"✅ Generated: {html_file.name}")

def main():
    """Convert all markdown docs to HTML."""
    docs_dir = Path(__file__).parent
    
    markdown_files = [
        'ARCHITECTURE.md',
        'TECHNICAL_DESIGN.md',
        'SEQUENCE_DIAGRAMS.md',
        'FEATURES.md'
    ]
    
    print("🔄 Converting markdown files to HTML...")
    print()
    
    for md_filename in markdown_files:
        md_file = docs_dir / md_filename
        if md_file.exists():
            convert_markdown_to_html(md_file, docs_dir)
        else:
            print(f"❌ Not found: {md_filename}")
    
    print()
    print("✨ Conversion complete!")
    print()
    print("📖 Open docs/index.html in your browser to view the documentation portal.")
    print("   Or open individual HTML files:")
    for md_filename in markdown_files:
        html_filename = md_filename.replace('.md', '.html')
        print(f"   - docs/{html_filename}")

if __name__ == '__main__':
    main()

