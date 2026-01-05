# The HACKERS CHALLENGE - Encoding CTF Challenges

A collection of 4 encoding-based challenges for Capture The Flag (CTF) competitions. Each challenge demonstrates a different encoding technique that participants must reverse-engineer to recover hidden flags.

## 🎯 Challenges Overview

| Challenge | Encoding Type | Difficulty | Output File |
|-----------|---------------|------------|-------------|
| [01-all-white-qr](./01-all-white-qr/) | QR Code Color Inversion | Easy | output.svg |
| [02-rgb-ascii](./02-rgb-ascii/) | RGB Channel ASCII Encoding (Matrix Theme) | Easy-Medium | output.svg |
| [03-dtmf](./03-dtmf/) | DTMF Telephone Tones + T9 Keypad | Medium | output.wav |
| [04-morse](./04-morse/) | Visual Morse Code (Chinese Characters) | Medium-Hard | output.mp4 |

## 🚀 Quick Start

### Run Individual Challenge
```bash
# Generate a challenge
cd 01-all-white-qr
python generate.py "HC{YOUR_FLAG}"
# Creates output.svg

# Solve the challenge
python solve.py
# Recovers the flag
```

### For Challenge 02 (RGB ASCII)
```bash
cd 02-rgb-ascii
python generate.py "Cover text here" "HC{YOUR_FLAG}"
python solve.py
```

### For Challenge 04 (Morse - Optional Music)
```bash
cd 04-morse
python generate.py "HC{YOUR_FLAG}"
# Or with background music:
python generate.py "HC{YOUR_FLAG}" music.mp3
```

## 🔍 Encoding Types Covered

### 1. **Visual Encoding**
- QR code color inversion (black/white reversal)
- RGB color channel data encoding
- Matrix-style visual effects with position markers

### 2. **Audio Encoding**
- DTMF (Dual-Tone Multi-Frequency) telephone tones
- T9 keypad text-to-number mapping
- Spectral frequency analysis

### 3. **Video Encoding**
- Morse code visual representation
- Chinese character differentiation ('点' for dots, '线' for dashes)
- Matrix-style cascading effects with filler characters

### 4. **Multi-Layer Encoding**
- ASCII-to-RGB color mapping
- Sequential channel distribution (R→G→B)
- Filler value detection and filtering

## 📁 Project Structure

```
HC2025-encoding/
├── 01-all-white-qr/                # QR Code Inversion Challenge
│   ├── generate.py
│   ├── solve.py
│   └── README.md
├── 02-rgb-ascii/                   # RGB ASCII Challenge
│   ├── generate.py
│   ├── solve.py
│   └── README.md
├── 03-dtmf/                        # DTMF Audio Challenge
│   ├── generate.py
│   ├── solve.py
│   └── README.md
├── 04-morse/                       # Morse Video Challenge
│   ├── generate.py
│   ├── solve.py
│   ├── solve_video.py              # Legacy computer vision solver
│   ├── solve_video_simple.py       # Legacy OCR solver
│   └── README.md
├── tests/                          # Test suite
│   ├── test_all_white_qr.py
│   ├── test_rgb_ascii.py
│   ├── test_dtmf.py
│   ├── test_morse.py
│   └── test_morse_video.py
├── CLAUDE.md                       # Development guidelines
├── requirements.txt                # Python dependencies
├── run_tests.sh                    # Test runner script
└── README.md                       # This file
```

## 🚦 Development & Testing

### Prerequisites

Install the required dependencies:

```bash
pip install -r requirements.txt
```

**System dependencies:**
- `zbar` library (for QR code decoding): `brew install zbar` (macOS) or `apt-get install libzbar0` (Linux)
- `ffmpeg` (optional, for video music): `brew install ffmpeg` (macOS) or `apt-get install ffmpeg` (Linux)

### Challenge Structure

Each challenge directory contains:
- `generate.py` - Creates the challenge file
- `solve.py` - Solves the challenge and recovers the flag
- `README.md` - Detailed solving instructions and hints

## 🧪 Testing Framework

The project includes a comprehensive test suite that validates:
- Challenge generation
- Flag encoding correctness
- Solution scripts
- Edge cases and error handling

### Run All Tests
```bash
./run_tests.sh
```

### Run Specific Challenge Tests
```bash
./run_tests.sh all-white-qr
./run_tests.sh rgb-ascii
./run_tests.sh dtmf
./run_tests.sh morse
```

### Manual Testing with unittest
```bash
python -m unittest tests.test_all_white_qr -v
python -m unittest tests.test_rgb_ascii -v
python -m unittest tests.test_dtmf -v
python -m unittest tests.test_morse -v
python -m unittest tests.test_morse_video -v
```
