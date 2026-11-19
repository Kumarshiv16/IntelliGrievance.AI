"""
IntelliGrievance AI - Report HTML to PDF Converter
Uses Headless Microsoft Edge or Google Chrome to render PROJECT_REPORT.html into PROJECT_REPORT.pdf.
"""

import os
import subprocess
import markdown

HERE = os.path.dirname(os.path.abspath(__file__))
MD_PATH = os.path.join(HERE, "..", "PROJECT_REPORT.md")
HTML_PATH = os.path.join(HERE, "..", "PROJECT_REPORT.html")
PDF_PATH = os.path.join(HERE, "..", "PROJECT_REPORT.pdf")

def convert_to_pdf():
    print(f"Reading markdown from: {MD_PATH}")
    with open(MD_PATH, "r", encoding="utf-8") as f:
        md_text = f.read()

    html_content = markdown.markdown(md_text, extensions=['tables', 'fenced_code'])
    
    styled_html = f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>IntelliGrievance AI - Project Report</title>
<style>
  @page {{
    size: A4;
    margin: 20mm 15mm 20mm 15mm;
  }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    line-height: 1.6;
    color: #1e293b;
    font-size: 11pt;
  }}
  h1 {{ font-size: 20pt; text-align: center; color: #1e1b4b; margin-bottom: 5px; }}
  h2 {{ font-size: 15pt; border-bottom: 2px solid #6366f1; padding-bottom: 4px; color: #312e81; margin-top: 24px; }}
  h3 {{ font-size: 13pt; color: #4338ca; margin-top: 18px; }}
  h4 {{ font-size: 11pt; color: #475569; }}
  p, li {{ text-align: justify; margin: 6px 0; }}
  table {{
    width: 100%;
    border-collapse: collapse;
    margin: 16px 0;
    font-size: 9.5pt;
  }}
  th, td {{
    border: 1px solid #cbd5e1;
    padding: 7px 10px;
    text-align: left;
  }}
  th {{
    background-color: #f1f5f9;
    color: #0f172a;
    font-weight: 600;
  }}
  pre, code {{
    background-color: #f8fafc;
    border: 1px solid #e2e8f0;
    font-family: "Courier New", Courier, monospace;
    font-size: 9pt;
    padding: 2px 4px;
    border-radius: 4px;
  }}
  pre {{
    padding: 10px;
    overflow-x: auto;
  }}
  blockquote {{
    border-left: 4px solid #6366f1;
    margin: 0;
    padding-left: 14px;
    color: #475569;
    font-style: italic;
  }}
</style>
</head>
<body>
{html_content}
</body>
</html>
"""

    with open(HTML_PATH, "w", encoding="utf-8") as f:
        f.write(styled_html)
    print(f"Generated intermediate HTML at: {HTML_PATH}")

    # Search for headless browser
    browsers = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    ]
    
    target_browser = None
    for b in browsers:
        if os.path.exists(b):
            target_browser = b
            break

    if not target_browser:
        print("Notice: Headless browser not found for PDF export.")
        return

    cmd = [
        target_browser,
        "--headless",
        "--disable-gpu",
        f"--print-to-pdf={PDF_PATH}",
        HTML_PATH
    ]
    print(f"Executing: {' '.join(cmd)}")
    res = subprocess.run(cmd, capture_output=True, text=True)
    if os.path.exists(PDF_PATH) and os.path.getsize(PDF_PATH) > 0:
        print(f"Successfully generated PDF report ({os.path.getsize(PDF_PATH)} bytes) at: {PDF_PATH}")
    else:
        print(f"PDF creation returned error: {res.stderr}")

if __name__ == "__main__":
    convert_to_pdf()
