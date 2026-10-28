#!/usr/bin/env python3
"""
Simple script to recursively list all PDFs in a folder and generate an HTML page
with a client-side search/filter at the top.
"""

import os
import sys
from html import escape


def find_pdfs(folder):
    """Recursively find all PDF files relative to the given folder."""
    pdfs = []
    folder = os.path.abspath(folder)
    for root, dirs, files in os.walk(folder):
        for file in files:
            if file.lower().endswith(".pdf"):
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, folder)
                # Use forward slashes for web compatibility
                rel_path = rel_path.replace(os.sep, "/")
                pdfs.append(rel_path)
    return sorted(pdfs)


def generate_html(pdfs, output_file):
    """Generate a simple HTML page listing the PDFs with a search box."""
    html_parts = [
        """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PDF Index</title>
    <style>
        body {
            font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
            max-width: 900px;
            margin: 40px auto;
            padding: 0 20px;
            background: #f8f9fa;
            color: #212529;
        }
        h1 { margin-bottom: 0.2em; }
        .count { color: #6c757d; margin-bottom: 1.2em; }
        #search {
            width: 100%;
            padding: 12px 16px;
            font-size: 16px;
            border: 1px solid #ced4da;
            border-radius: 6px;
            margin-bottom: 20px;
            box-sizing: border-box;
        }
        #search:focus {
            outline: none;
            border-color: #0d6efd;
            box-shadow: 0 0 0 3px rgba(13, 110, 253, 0.15);
        }
        ul {
            list-style: none;
            padding: 0;
            margin: 0;
            background: white;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        }
        li {
            border-bottom: 1px solid #e9ecef;
        }
        li:last-child { border-bottom: none; }
        li a {
            display: block;
            padding: 12px 16px;
            text-decoration: none;
            color: #0d6efd;
            word-break: break-all;
        }
        li a:hover {
            background: #f1f3f5;
        }
        .hidden { display: none !important; }
        .no-results {
            padding: 20px;
            text-align: center;
            color: #6c757d;
            display: none;
        }
    </style>
</head>
<body>
    <h1>PDF Files</h1>
    <div class="count" id="count"></div>
    <input type="text" id="search" placeholder="Search PDFs by name or path..." autofocus>
    <ul id="pdfList">
"""
    ]

    for pdf in pdfs:
        safe = escape(pdf)
        html_parts.append(f'        <li><a href="{safe}" target="_blank">{safe}</a></li>\n')

    html_parts.append(
        """    </ul>
    <div class="no-results" id="noResults">No matching PDFs found.</div>

    <script>
        const search = document.getElementById('search');
        const list = document.getElementById('pdfList');
        const items = list.querySelectorAll('li');
        const countEl = document.getElementById('count');
        const noResults = document.getElementById('noResults');
        const total = items.length;

        function updateCount(visible) {
            countEl.textContent = visible === total
                ? total + ' PDF' + (total !== 1 ? 's' : '')
                : visible + ' of ' + total + ' PDFs';
            noResults.style.display = visible === 0 ? 'block' : 'none';
        }

        function filter() {
            const q = search.value.trim().toLowerCase();
            let visible = 0;
            items.forEach(item => {
                const text = item.textContent.toLowerCase();
                const match = !q || text.includes(q);
                item.classList.toggle('hidden', !match);
                if (match) visible++;
            });
            updateCount(visible);
        }

        search.addEventListener('input', filter);
        updateCount(total);
    </script>
</body>
</html>
"""
    )

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("".join(html_parts))

    print(f"Generated {output_file} with {len(pdfs)} PDF(s).")


def main():
    if len(sys.argv) < 2:
        print("Usage: python pdf_index.py <folder> [output.html]")
        print("Example: python pdf_index.py ./docs")
        print("         python pdf_index.py ./docs index.html")
        sys.exit(1)

    folder = sys.argv[1]
    if not os.path.isdir(folder):
        print(f"Error: '{folder}' is not a valid directory.")
        sys.exit(1)

    # Default output: index.html inside the scanned folder
    if len(sys.argv) >= 3:
        output = sys.argv[2]
    else:
        output = os.path.join(folder, "index.html")

    pdfs = find_pdfs(folder)
    if not pdfs:
        print("No PDF files found.")
        # Still generate empty page
    generate_html(pdfs, output)


if __name__ == "__main__":
    main()
