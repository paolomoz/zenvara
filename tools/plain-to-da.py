#!/usr/bin/env python3
"""Convert .plain.html (EDS rendered format) to DA authoring format (table-based HTML document).

The .plain.html format uses:
  - <div class="blockname"> wrappers for blocks
  - <div> rows with <div> cells inside blocks
  - <hr> for section breaks
  - <div class="section-metadata"> for section metadata

The DA authoring format uses:
  - <table> for blocks, with block name in first <th> row
  - <tr>/<td> for block rows/cells
  - <hr> for section breaks
  - Wrapped in <html><body><main> with <div> per section

Usage: python3 plain-to-da.py input.plain.html > output.html
"""

import sys
import re
from html.parser import HTMLParser


def convert_plain_to_da(html_content, title=""):
    """Convert .plain.html content to DA document format."""
    # Split into sections by <hr> tags
    sections = re.split(r'<hr\s*/?>', html_content)

    da_sections = []
    for section in sections:
        section = section.strip()
        if not section:
            continue
        converted = convert_section(section)
        if converted.strip():
            da_sections.append(f"<div>\n{converted}\n</div>")

    main_content = "\n".join(da_sections)

    return f"""<html>
<head><title>{title}</title></head>
<body>
<header></header>
<main>
{main_content}
</main>
<footer></footer>
</body>
</html>"""


def convert_section(section_html):
    """Convert a single section's content from plain to DA format."""
    # A section is wrapped in <div>...</div> at the top level
    # Inside it may have blocks (<div class="blockname">) and default content

    # Remove outer <div> wrapper if present
    section_html = section_html.strip()
    if section_html.startswith('<div>') and section_html.endswith('</div>'):
        # Remove just the outermost div wrapper
        inner = remove_outer_div(section_html)
        if inner is not None:
            section_html = inner

    # Find all block divs and convert them to tables
    result = convert_blocks_to_tables(section_html)
    return result


def remove_outer_div(html):
    """Remove the outermost <div>...</div> wrapper, respecting nesting."""
    html = html.strip()
    if not html.startswith('<div>'):
        return None

    depth = 0
    i = 0
    while i < len(html):
        if html[i:i+4] == '<div':
            depth += 1
            i = html.index('>', i) + 1
        elif html[i:i+6] == '</div>':
            depth -= 1
            if depth == 0:
                # This is the closing tag of the outer div
                if i + 6 >= len(html) or html[i+6:].strip() == '':
                    return html[html.index('>', 0) + 1:i].strip()
                else:
                    return None  # Not just a single outer div
            i += 6
        else:
            i += 1
    return None


def convert_blocks_to_tables(html):
    """Convert <div class="blockname"> structures to <table> structures."""
    # Pattern to find block divs: <div class="blockname">
    result = []
    pos = 0

    while pos < len(html):
        # Look for block div
        match = re.search(r'<div\s+class="([^"]+)">', html[pos:])
        if not match:
            result.append(html[pos:])
            break

        # Add content before the block
        result.append(html[pos:pos + match.start()])

        block_name = match.group(1)
        block_start = pos + match.start()

        # Find the closing </div> for this block
        block_inner_start = block_start + len(match.group(0))
        block_end = find_closing_div(html, block_start)

        if block_end is None:
            result.append(html[pos + match.start():])
            break

        block_inner = html[block_inner_start:block_end]

        # Convert to table
        table = convert_block_to_table(block_name, block_inner)
        result.append(table)

        pos = block_end + 6  # skip </div>

    return ''.join(result)


def find_closing_div(html, start):
    """Find the position of the closing </div> for the div starting at `start`."""
    depth = 0
    i = start
    while i < len(html):
        if html[i:i+4] == '<div':
            depth += 1
            i = html.index('>', i) + 1
        elif html[i:i+6] == '</div>':
            depth -= 1
            if depth == 0:
                return i
            i += 6
        else:
            i += 1
    return None


def convert_block_to_table(block_name, inner_html):
    """Convert a block's inner HTML from div rows/cells to table rows/cells."""
    # Handle variant classes: "columns reverse" -> block="columns", variant="reverse"
    parts = block_name.split()
    base_name = parts[0]
    variants = parts[1:] if len(parts) > 1 else []

    # Format block name: kebab-case to Title Case
    display_name = base_name.replace('-', ' ').title()
    # Handle special names
    name_map = {
        'Section Metadata': 'Section Metadata',
        'Cta Banner': 'CTA Banner',
        'Faq': 'FAQ',
        'Logo Wall': 'Logo Wall',
    }
    display_name = name_map.get(display_name, display_name)

    # Add variants in parentheses: "Columns (reverse)"
    if variants:
        variant_str = ', '.join(v.replace('-', ' ') for v in variants)
        display_name = f'{display_name} ({variant_str})'

    # Extract rows: each direct child <div> of the block is a row
    rows = extract_direct_child_divs(inner_html)

    table_rows = []
    for row_html in rows:
        # Each row's direct child <div>s are cells
        cells = extract_direct_child_divs(row_html)
        if cells:
            tds = ''.join(f'<td>{cell.strip()}</td>' for cell in cells)
        else:
            tds = f'<td>{row_html.strip()}</td>'
        table_rows.append(f'<tr>{tds}</tr>')

    # Determine colspan from first row's cell count
    first_row_cells = extract_direct_child_divs(rows[0]) if rows else []
    colspan = max(len(first_row_cells), 1)

    header = f'<tr><th colspan="{colspan}">{display_name}</th></tr>'

    return f'<table>\n{header}\n{"".join(table_rows)}\n</table>'


def extract_direct_child_divs(html):
    """Extract content of direct child <div> elements."""
    html = html.strip()
    children = []
    pos = 0

    while pos < len(html):
        # Find next <div> or <div ...>
        match = re.search(r'<div[^>]*>', html[pos:])
        if not match:
            break

        div_start = pos + match.start()

        # Skip any text before this div (shouldn't be much)
        div_inner_start = div_start + len(match.group(0))
        div_end = find_closing_div(html, div_start)

        if div_end is None:
            break

        children.append(html[div_inner_start:div_end])
        pos = div_end + 6

    return children


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 plain-to-da.py input.plain.html [title]", file=sys.stderr)
        sys.exit(1)

    input_file = sys.argv[1]
    title = sys.argv[2] if len(sys.argv) > 2 else ""

    with open(input_file, 'r') as f:
        content = f.read()

    print(convert_plain_to_da(content, title))
