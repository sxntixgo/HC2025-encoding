# Challenge 01: White Rabbit - Solution Guide

**For CTF Organizers Only**

## Overview

This challenge uses an inverted QR code where both the background and QR modules are white, making it invisible to phone cameras but still parseable from the SVG structure.

## How It Works

1. A standard QR code has black modules on a white background
2. This challenge inverts it: white modules on a white background
3. The SVG still contains rectangle elements for each QR module
4. Solvers must parse the SVG to identify module positions and reconstruct a scannable QR

## Solving the Challenge

### Method 1: Automated Solver

```bash
python solve.py whiterabbit.svg
```

The solver:
- Parses the SVG file structure
- Identifies QR modules based on rectangle positions (not colors)
- Reconstructs a standard black-on-white QR code
- Decodes the resulting QR code using pyzbar

### Method 2: Manual Approach

1. Open the SVG in a text editor
2. Observe that all `<rect>` elements have `fill="white"`
3. The first large rectangle is the background
4. Subsequent small rectangles (10x10) are QR modules
5. Create a new image with black rectangles at those positions
6. Scan the resulting QR code

### Dependencies

```bash
pip install qrcode pillow pyzbar
brew install zbar  # macOS - required for pyzbar
```

## Expected Solution Path

Participants should:
1. Notice the QR code appears blank/invisible
2. Examine the SVG source code
3. Realize the structure is intact, only colors are inverted
4. Either invert colors or parse rectangle positions
5. Decode the reconstructed QR code
