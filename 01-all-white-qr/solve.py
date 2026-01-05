#!/usr/bin/env python3
import sys
import xml.etree.ElementTree as ET
from PIL import Image, ImageDraw
import qrcode
try:
    from pyzbar import pyzbar
    HAS_PYZBAR = True
except ImportError:
    HAS_PYZBAR = False
    print("Warning: pyzbar not available. Install with: brew install zbar")
import io

def solve_inverted_qr(svg_file):
    tree = ET.parse(svg_file)
    root = tree.getroot()

    svg_width = int(root.attrib['width'])
    svg_height = int(root.attrib['height'])

    # Create image - start with white background
    inverted_img = Image.new('RGB', (svg_width, svg_height), 'white')
    draw = ImageDraw.Draw(inverted_img)

    # Parse SVG rectangles
    rects = list(root.findall('.//{http://www.w3.org/2000/svg}rect'))

    # The first large rectangle is the background, subsequent smaller ones are QR modules
    # QR modules are typically 10x10 boxes
    box_size = 10

    for rect in rects[1:]:  # Skip first rect (background)
        x = int(rect.attrib.get('x', 0))
        y = int(rect.attrib.get('y', 0))
        width = int(rect.attrib.get('width', svg_width))
        height = int(rect.attrib.get('height', svg_height))

        # Only process small rectangles that are likely QR modules
        if width == box_size and height == box_size:
            # Draw as black module in the output
            draw.rectangle([x, y, x + width, y + height], fill='black')
    
    if HAS_PYZBAR:
        decoded_objects = pyzbar.decode(inverted_img)
        
        if decoded_objects:
            flag = decoded_objects[0].data.decode('utf-8')
            print(f"Flag found: {flag}")
            return flag
        else:
            print("No QR code found or unable to decode")
            return None
    else:
        print("Cannot decode QR code: pyzbar library not available")
        print("Please install with: brew install zbar && pip install pyzbar")
        return None

def main():
    if len(sys.argv) != 2:
        print("Usage: python solve.py <svg_file>")
        sys.exit(1)
    
    svg_file = sys.argv[1]
    solve_inverted_qr(svg_file)

if __name__ == "__main__":
    main()