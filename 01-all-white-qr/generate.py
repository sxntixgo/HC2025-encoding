#!/usr/bin/env python3
import sys
import qrcode
import xml.etree.ElementTree as ET

def generate_inverted_qr(text, output_file):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(text)
    qr.make(fit=True)

    modules = qr.modules
    size = len(modules)
    box_size = 10
    border = 4

    total_size = (size + border * 2) * box_size

    svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{total_size}" height="{total_size}" viewBox="0 0 {total_size} {total_size}">
<rect width="{total_size}" height="{total_size}" fill="white"/>
'''

    for i in range(size):
        for j in range(size):
            x = (j + border) * box_size
            y = (i + border) * box_size

            if modules[i][j]:
                svg_content += f'<rect x="{x}" y="{y}" width="{box_size}" height="{box_size}" fill="white"/>\n'

    svg_content += '</svg>'

    with open(output_file, 'w') as f:
        f.write(svg_content)

    print(f"Inverted QR code saved to {output_file}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python generate.py <flag>")
        sys.exit(1)

    flag = sys.argv[1]

    generate_inverted_qr(flag, "output.svg")

if __name__ == "__main__":
    main()