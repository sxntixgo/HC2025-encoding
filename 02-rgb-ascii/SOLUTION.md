# Challenge 02: Kung Fu - Solution Guide

**For CTF Organizers Only**

## Overview

This challenge encodes ASCII text using RGB color values with a Matrix rain visual effect. The flag is hidden within random text and distributed across RGB channels with easily detectable filler values.

## How It Works

1. The flag is split into 3 parts
2. Each part is injected into random cover text with `+` markers
3. The combined text is split into 3 sections (one per RGB channel)
4. Each cell encodes one character in one channel:
   - R channel data: `rgb(char, 80, 20)`
   - G channel data: `rgb(20, char, 5)`
   - B channel data: `rgb(5, 80, char)`
5. Filler values (5, 20, 80) are outside printable ASCII range (32-126)

## Solving the Challenge

### Method 1: Automated Solver

```bash
python solve.py kungfu.svg
```

The solver:
- Parses the SVG to extract RGB values
- Identifies filler values (5, 20, 80) vs data values
- Extracts printable ASCII characters from each channel
- Reconstructs the text and extracts the flag

### Method 2: Manual Approach

1. Open the SVG in a text editor
2. Find `<rect fill="rgb(...)"/>` elements
3. For each RGB value, check which channel has printable ASCII (32-126)
4. Channels with values 5, 20, or 80 are filler
5. Convert printable values to characters
6. Combine to reveal the flag

### Dependencies

```bash
pip install pillow
```

## Encoding Details

**Filler Values:**
- `FILLER_LOW = 5` - Very dark, non-printable
- `FILLER_HIGH = 20` - Dark, non-printable
- `FILLER_GREEN = 80` - Darker green for Matrix effect, non-printable

**Sequential Encoding:**
- First N cells: R channel has data
- Next M cells: G channel has data
- Final K cells: B channel has data

**Visual Features:**
- QR-like position markers (bright green in corners)
- Dark background with subtle green tint
- Colors are visually dark but data is embedded

## Expected Solution Path

Participants should:
1. Recognize the Matrix-themed SVG with colored rectangles
2. Inspect the SVG source to find RGB values
3. Notice certain values (5, 20, 80) repeat frequently
4. Realize these are filler values outside printable ASCII
5. Extract characters from channels with printable values
6. Piece together the flag from `+` delimited sections
