#!/usr/bin/env python3
import sys
import xml.etree.ElementTree as ET
import re

def solve_rgb_ascii(svg_file):
    """
    Decode RGB ASCII encoded SVG.

    - Extract RGB values from SVG
    - Identify which channel contains data (printable ASCII 32-126)
    - Other channels will have filler values (5 or 250)
    - Reverse green tint boost
    - Reconstruct text from each channel
    - Extract flag from '+' delimited sections
    """

    # Parse SVG
    tree = ET.parse(svg_file)
    root = tree.getroot()

    # Find all rectangles
    ns = {'svg': 'http://www.w3.org/2000/svg'}
    rects = root.findall('.//svg:rect', ns)

    # Extract colors (skip position markers)
    marker_colors = {'rgb(0, 255, 0)', 'rgb(0, 50, 0)', 'rgb(0, 150, 0)', 'black'}
    colors = []

    for rect in rects:
        if 'fill' in rect.attrib:
            color = rect.attrib['fill']
            if color not in marker_colors and 'rgb' in color:
                # Parse RGB values
                vals = color.replace('rgb(', '').replace(')', '').split(',')
                r, g, b = int(vals[0]), int(vals[1]), int(vals[2])
                colors.append((r, g, b))

    # Decode each cell
    r_chars = []
    g_chars = []
    b_chars = []

    FILLER_LOW = 5
    FILLER_HIGH = 20  # Changed to match dark Matrix effect
    FILLER_GREEN = 80  # G is set to 80 when not used for data (darker Matrix green)

    for r, g, b in colors:
        # No green boost - use values directly
        # Determine which channel has data (printable ASCII)
        # Other channels should have filler values (5, 20, or 80 for G)

        r_is_filler = (r == FILLER_LOW or r == FILLER_HIGH)
        g_is_filler = (g == FILLER_LOW or g == FILLER_HIGH or g == FILLER_GREEN)
        b_is_filler = (b == FILLER_LOW or b == FILLER_HIGH)

        # Extract printable characters only (data channels)
        if not r_is_filler and 32 <= r <= 126:
            r_chars.append(chr(r))

        if not g_is_filler and 32 <= g <= 126:
            g_chars.append(chr(g))

        if not b_is_filler and 32 <= b <= 126:
            b_chars.append(chr(b))

    # Reconstruct sections from each channel
    r_section = ''.join(r_chars)
    g_section = ''.join(g_chars)
    b_section = ''.join(b_chars)

    # Combine all sections to get full text
    full_text = r_section + g_section + b_section

    print(f"R channel section: {r_section}")
    print(f"G channel section: {g_section}")
    print(f"B channel section: {b_section}")
    print(f"\nFull decoded text:\n{full_text}")

    # Extract flag from '+' delimited sections
    # Pattern: text+FLAG_PART+text+FLAG_PART+text+FLAG_PART+text
    parts = full_text.split('+')

    # Find the part with HC{ and extract every other part from there
    flag_parts = []
    flag_start_idx = None
    for i, part in enumerate(parts):
        if 'HC{' in part:
            flag_start_idx = i
            break

    if flag_start_idx is not None:
        # Extract every other part starting from flag_start_idx
        i = flag_start_idx
        while i < len(parts):
            flag_parts.append(parts[i])
            if '}' in parts[i]:
                break
            i += 2  # Skip random text, get next flag part

        extracted_flag = ''.join(flag_parts)
        if '}' in extracted_flag:
            extracted_flag = extracted_flag[:extracted_flag.index('}')+1]
        print(f"\nDecoded flag: {extracted_flag}")
    else:
        # Try simple regex
        flag_match = re.search(r'HC\{[^}]+\}', full_text)
        if flag_match:
            print(f"\nDecoded flag: {flag_match.group()}")
        else:
            print("\n(No flag pattern found in text)")

    return full_text

def main():
    if len(sys.argv) != 2:
        print("Usage: python solve.py <svg_file>")
        sys.exit(1)

    svg_file = sys.argv[1]
    solve_rgb_ascii(svg_file)

if __name__ == "__main__":
    main()
