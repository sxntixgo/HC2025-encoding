# Encoding Challenges CTF

A collection of encoding-based challenges for Capture The Flag (CTF) competitions. Each challenge demonstrates a different encoding technique that participants must reverse-engineer to recover hidden flags.

## Overview

This repository contains four distinct encoding challenges, each progressively building on different concepts from visual encoding to audio signal processing.

## Challenges

### [01-all-white-qr](./01-all-white-qr/)
**Difficulty: Easy**
A QR code challenge with inverted colors (black/white reversed). Participants must recognize that the QR code colors have been swapped and invert them to decode the flag.

**Key Skills**: QR code structure, color inversion, SVG processing

### [02-rgb-ascii](./02-rgb-ascii/)
**Difficulty: Easy-Medium**
Matrix rain themed challenge where text is encoded using RGB color values in an SVG image. ASCII character codes are placed in RGB components with a dark Matrix aesthetic using easily detectable filler values (5, 20, 80). The flag is split into three parts and injected into random text with '+' markers, then distributed sequentially across R, G, and B channels.

**Key Skills**: ASCII encoding, RGB color model, SVG parsing, filler detection, Matrix visual analysis, pattern recognition

**Visual Features**: QR-code-like position markers (green), dark background, subtle green tint (G=80) for authentic Matrix rain effect

### [03-dtmf](./03-dtmf/)
**Difficulty: Medium**
Audio challenge using DTMF (telephone tone) encoding combined with T9 keypad mapping. Text is converted to T9 sequences then encoded as telephone touch-tone audio.

**Key Skills**: DTMF frequency analysis, T9 mapping, audio signal processing, spectral analysis

### [04-morse](./04-morse/)
**Difficulty: Medium-Hard**
Matrix-style video with falling green Chinese characters encoding Morse code. Bright green characters ('点' for dots, '线' for dashes) represent the Morse code, while faded green characters provide decorative background rain effect.

**Key Skills**: Morse code, visual pattern recognition, Chinese character identification, video analysis

## Getting Started

### Prerequisites

Install the required dependencies:

```bash
pip install -r requirements.txt
```

**System dependencies:**
- `zbar` library (for QR code decoding): `brew install zbar` (macOS) or `apt-get install libzbar0` (Linux)
- `ffmpeg` (optional, for video music): `brew install ffmpeg` (macOS) or `apt-get install ffmpeg` (Linux)

### Quick Start

Each challenge directory contains:
- `generate.py` - Creates the challenge file
- `solve.py` - Solves the challenge
- `README.md` - Detailed solving instructions

### Running Tests

```bash
# Run all tests
./run_tests.sh

# Run specific challenge tests
./run_tests.sh all-white-qr
./run_tests.sh rgb-ascii
./run_tests.sh dtmf
./run_tests.sh morse

# Manual testing with unittest
python -m unittest tests.test_all_white_qr -v
python -m unittest tests.test_rgb_ascii -v
python -m unittest tests.test_dtmf -v
python -m unittest tests.test_morse -v
python -m unittest tests.test_morse_video -v
```