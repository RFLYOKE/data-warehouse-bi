import os
import json

base_dir = r"g:\My Drive\File Kuliah\Semester 7\data-warehouse\assignment\tugas kelompok\Data-20261013T041524Z-1-001\NRG_DW"
md_path = os.path.join(base_dir, "Laporan_Desain_Data_Warehouse_Kelompok_4.md")
html_path = os.path.join(base_dir, "Laporan_Desain_Data_Warehouse_Kelompok_4.html")

with open(md_path, "r", encoding="utf-8") as f:
    md_content = f.read()

# Escape backticks and dollar signs for template literal or use JSON.dumps
md_json = json.dumps(md_content)

html_template = f"""<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Laporan Desain Data Warehouse - Kelompok 4</title>
  <!-- Google Fonts -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <!-- Marked.js for Markdown parsing -->
  <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
  <!-- Mermaid.js for diagrams -->
  <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
  <!-- Highlight.js for code highlighting -->
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@11.9.0/build/styles/github-dark.min.css">
  <script src="https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@11.9.0/build/highlight.min.js"></script>
  <script src="https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@11.9.0/build/languages/sql.min.js"></script>
  <script src="https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@11.9.0/build/languages/powershell.min.js"></script>

  <style>
    :root {{
      --bg: #f8fafc;
      --card-bg: #ffffff;
      --text: #1e293b;
      --text-muted: #64748b;
      --primary: #2563eb;
      --primary-dark: #1d4ed8;
      --border: #e2e8f0;
      --border-accent: #cbd5e1;
      --code-bg: #0f172a;
    }}

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}

    body {{
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background-color: var(--bg);
      color: var(--text);
      line-height: 1.7;
      font-size: 15px;
      padding: 40px 20px;
    }}

    .container {{
      max-width: 1040px;
      margin: 0 auto;
      background: var(--card-bg);
      padding: 60px 80px;
      border-radius: 16px;
      box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 10px 15px -3px rgba(0, 0, 0, 0.07);
      border: 1px solid var(--border);
    }}

    h1, h2, h3, h4, h5, h6 {{
      color: #0f172a;
      font-weight: 700;
      margin-top: 1.8em;
      margin-bottom: 0.6em;
      line-height: 1.3;
    }}

    h1 {{
      font-size: 2.2rem;
      border-bottom: 3px solid #e2e8f0;
      padding-bottom: 16px;
      margin-top: 0;
      color: #1e3a8a;
    }}

    h2 {{
      font-size: 1.6rem;
      border-bottom: 2px solid #f1f5f9;
      padding-bottom: 10px;
      margin-top: 2.2em;
      color: #1e40af;
    }}

    h3 {{
      font-size: 1.25rem;
      color: #334155;
    }}

    p {{
      margin-bottom: 1.2em;
    }}

    ul, ol {{
      margin-bottom: 1.4em;
      padding-left: 28px;
    }}

    li {{
      margin-bottom: 6px;
    }}

    hr {{
      border: 0;
      height: 1px;
      background: var(--border);
      margin: 36px 0;
    }}

    table {{
      width: 100%;
      border-collapse: collapse;
      margin: 24px 0;
      font-size: 13.5px;
      background: #ffffff;
      border-radius: 8px;
      overflow: hidden;
      border: 1px solid var(--border);
    }}

    th, td {{
      padding: 10px 14px;
      text-align: left;
      border-bottom: 1px solid var(--border);
    }}

    th {{
      background: #f1f5f9;
      font-weight: 600;
      color: #334155;
      white-space: nowrap;
    }}

    tr:hover td {{
      background-color: #f8fafc;
    }}

    code {{
      font-family: 'JetBrains Mono', Consolas, monospace;
      font-size: 0.88em;
      background: #f1f5f9;
      color: #0f172a;
      padding: 2px 6px;
      border-radius: 4px;
      border: 1px solid #e2e8f0;
    }}

    pre {{
      background: var(--code-bg);
      border-radius: 10px;
      padding: 18px 20px;
      margin: 20px 0;
      overflow-x: auto;
      border: 1px solid #334155;
    }}

    pre code {{
      background: transparent;
      color: #f8fafc;
      padding: 0;
      border: none;
      font-size: 0.9em;
      line-height: 1.5;
    }}

    blockquote {{
      border-left: 4px solid var(--primary);
      padding: 12px 20px;
      background: #eff6ff;
      border-radius: 0 8px 8px 0;
      margin: 20px 0;
      color: #1e40af;
    }}

    .mermaid {{
      margin: 30px 0;
      background: #f8fafc;
      padding: 24px;
      border-radius: 12px;
      border: 1px solid var(--border);
      text-align: center;
    }}

    a {{
      color: var(--primary);
      text-decoration: none;
    }}

    a:hover {{
      text-decoration: underline;
    }}

    /* Print styles */
    @media print {{
      body {{
        background: #fff;
        padding: 0;
      }}
      .container {{
        box-shadow: none;
        border: none;
        padding: 0;
        max-width: 100%;
      }}
      pre, table {{
        page-break-inside: avoid;
      }}
      h2, h3 {{
        page-break-after: avoid;
      }}
    }}
  </style>
</head>
<body>
  <div class="container" id="content">Memuat dokumen laporan...</div>

  <script>
    mermaid.initialize({{ startOnLoad: false, theme: 'neutral' }});

    const rawMd = {md_json};

    marked.setOptions({{
      highlight: function(code, lang) {{
        if (lang && hljs.getLanguage(lang)) {{
          try {{
            return hljs.highlight(code, {{ language: lang }}).value;
          }} catch (e) {{}}
        }}
        return hljs.highlightAuto(code).value;
      }},
      breaks: false,
      gfm: true
    }});

    // Custom renderer to preserve mermaid code
    const renderer = new marked.Renderer();
    const defaultCodeRenderer = renderer.code.bind(renderer);
    renderer.code = function(code, language) {{
      if (language === 'mermaid') {{
        return `<div class="mermaid">${{code}}</div>`;
      }}
      return defaultCodeRenderer(code, language);
    }};

    marked.use({{ renderer }});

    document.getElementById('content').innerHTML = marked.parse(rawMd);

    // Render Mermaid diagrams
    mermaid.run();
  </script>
</body>
</html>
"""

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html_template)

print(f"HTML report successfully generated at: {{html_path}}")
