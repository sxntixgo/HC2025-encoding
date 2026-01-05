#!/usr/bin/env python3
import sys
import math

def generate_rgb_ascii(flag, random_text, output_file):
    """
    Generate a QR-code-like image with RGB encoding.

    - Split flag into 3 parts and inject evenly into random text with '+' delimiters
    - Split resulting text into 3 sections (one per RGB channel)
    - Encode each section in its own channel (R, G, or B) as ASCII decimal values
    - Other channels use easily detectable filler values (non-printable, consistent for Matrix rain)
    """

    # Split flag into 3 parts
    flag_third = len(flag) // 3
    flag_part1 = flag[:flag_third]
    flag_part2 = flag[flag_third:2*flag_third]
    flag_part3 = flag[2*flag_third:]

    # Split random text into 3 parts
    text_third = len(random_text) // 3
    text_part1 = random_text[:text_third]
    text_part2 = random_text[text_third:2*text_third]
    text_part3 = random_text[2*text_third:]

    # Inject flag parts into random text with '+' delimiters
    # Pattern: text+FLAG+text
    mid1 = len(text_part1) // 2
    injected_part1 = text_part1[:mid1] + '+' + flag_part1 + '+' + text_part1[mid1:]

    mid2 = len(text_part2) // 2
    injected_part2 = text_part2[:mid2] + '+' + flag_part2 + '+' + text_part2[mid2:]

    mid3 = len(text_part3) // 2
    injected_part3 = text_part3[:mid3] + '+' + flag_part3 + '+' + text_part3[mid3:]

    # Combine all three parts to get total text
    full_text = injected_part1 + injected_part2 + injected_part3

    # Split full text into 3 sections for RGB channels
    section_len = len(full_text) // 3
    r_section = full_text[:section_len]
    g_section = full_text[section_len:2*section_len]
    b_section = full_text[2*section_len:]

    # Calculate grid size
    # We need cells for ALL three sections (sequentially), not just the max
    total_chars = len(r_section) + len(g_section) + len(b_section)
    marker_cells = 3 * 7 * 7  # 3 position markers
    grid_size = max(math.ceil(math.sqrt(total_chars + marker_cells)), 21)

    # Filler values for Matrix rain effect (easily detectable, non-printable)
    # Use consistent values that are clearly non-printable ASCII
    # Use low values to keep background dark for Matrix effect
    FILLER_LOW = 5    # Low value (non-printable)
    FILLER_HIGH = 20  # Low value for dark Matrix effect (non-printable)

    box_size = 20
    border = 2
    total_size = (grid_size + border * 2) * box_size

    # SVG header with black background
    svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{total_size}" height="{total_size}" viewBox="0 0 {total_size} {total_size}">
<rect width="{total_size}" height="{total_size}" fill="black"/>
'''

    def is_position_marker(i, j, grid_size):
        """Check if cell is part of a position marker (QR-code style)"""
        if i < 7 and j < 7:  # Top-left
            return True
        if i < 7 and j >= grid_size - 7:  # Top-right
            return True
        if i >= grid_size - 7 and j < 7:  # Bottom-left
            return True
        return False

    def get_marker_color(i, j, grid_size):
        """Get color for position marker (green for Matrix theme)"""
        local_i = i if i < 7 else (i - (grid_size - 7))
        local_j = j if j < 7 else (j - (grid_size - 7))

        # Matrix style: bright green borders, darker green interior
        if local_i == 0 or local_i == 6 or local_j == 0 or local_j == 6:
            return "rgb(0, 255, 0)"  # Bright green
        if local_i == 1 or local_i == 5 or local_j == 1 or local_j == 5:
            return "rgb(0, 50, 0)"   # Dark green
        return "rgb(0, 150, 0)"      # Medium green

    # Track indices for each channel
    r_idx = 0
    g_idx = 0
    b_idx = 0

    # Generate grid
    for i in range(grid_size):
        for j in range(grid_size):
            x = (j + border) * box_size
            y = (i + border) * box_size

            if is_position_marker(i, j, grid_size):
                marker_color = get_marker_color(i, j, grid_size)
                svg_content += f'<rect x="{x}" y="{y}" width="{box_size}" height="{box_size}" fill="{marker_color}"/>\n'
            else:
                # Encode one character from one channel only
                # Other channels use easily detectable filler values

                if r_idx < len(r_section):
                    # R channel contains data, G darker for Matrix effect, B is filler
                    r_val = ord(r_section[r_idx])
                    g_val = 80           # Darker green for Matrix rain (not too bright)
                    b_val = FILLER_HIGH  # Easily detectable filler
                    r_idx += 1
                elif g_idx < len(g_section):
                    # G channel contains data, R and B are filler
                    r_val = FILLER_HIGH  # Easily detectable filler
                    g_val = ord(g_section[g_idx])
                    b_val = FILLER_LOW   # Easily detectable filler
                    g_idx += 1
                elif b_idx < len(b_section):
                    # B channel contains data, G darker for Matrix effect, R is filler
                    r_val = FILLER_LOW   # Easily detectable filler
                    g_val = 80           # Darker green for Matrix rain (not too bright)
                    b_val = ord(b_section[b_idx])
                    b_idx += 1
                else:
                    # All filler (no more data)
                    r_val = FILLER_LOW
                    g_val = FILLER_LOW   # Keep dark
                    b_val = FILLER_LOW

                # No green boost - use values directly
                svg_content += f'<rect x="{x}" y="{y}" width="{box_size}" height="{box_size}" fill="rgb({r_val},{g_val},{b_val})"/>\n'

    svg_content += '</svg>'

    with open(output_file, 'w') as f:
        f.write(svg_content)

    print(f"RGB ASCII encoded image saved to {output_file}")
    print(f"Flag split into 3 parts and injected into random text")
    print(f"R channel section: {r_section}")
    print(f"G channel section: {g_section}")
    print(f"B channel section: {b_section}")
    print(f"\nFiller values used: Low={FILLER_LOW}, High={FILLER_HIGH}")
    print(f"Printable ASCII range: 32-126")
    print(f"Filler values are easily detectable (outside printable range)")

def main():
    if len(sys.argv) != 3:
        print("Usage: python generate.py <flag> <random_text>")
        sys.exit(1)

    flag = sys.argv[1]
    random_text = sys.argv[2]

    generate_rgb_ascii(flag, random_text, "output.svg")

if __name__ == "__main__":
    main()
