# Encoding Challenges - Developer Documentation

This document provides technical implementation details for CTF organizers and developers working with the encoding challenges.

## Architecture Overview

The encoding challenges repository contains four distinct challenges, each demonstrating different encoding techniques:

1. **01-all-white-qr**: Visual encoding (QR code inversion)
2. **02-rgb-ascii**: Color-based encoding (RGB channels)
3. **03-dtmf**: Audio encoding (telephone tones)
4. **04-morse**: Video encoding (Matrix-style visual Morse code)

## Challenge Details

### Challenge 01: All White QR
**Implementation**: [01-all-white-qr/](./01-all-white-qr/)

**Concept**: QR codes with inverted black/white colors
- Standard QR codes: black on white background
- Challenge QR codes: white on black background

**Files**:
- `generate.py`: Creates inverted QR code SVG
- `solve.py`: Inverts colors and decodes QR

**Testing**: `tests/test_all_white_qr.py`

### Challenge 02: RGB ASCII (Matrix Rain Edition)
**Implementation**: [02-rgb-ascii/](./02-rgb-ascii/)

**Concept**: ASCII text encoded as RGB color values with Matrix rain aesthetic
- Each character's ASCII code becomes RGB components
- Flag split into 3 parts, injected into cover text with '+' markers
- Sequential channel encoding: R channel data → G channel data → B channel data
- Matrix visual effect using easily detectable filler values (5, 20, 80)

**Encoding Details**:
- **Filler values**:
  - FILLER_LOW = 5 (very dark)
  - FILLER_HIGH = 20 (dark)
  - FILLER_GREEN = 80 (darker green for Matrix effect)
- **Color patterns**:
  - R channel data: rgb(char, 80, 20) - subtle green tint
  - G channel data: rgb(20, char, 5) - very dark
  - B channel data: rgb(5, 80, char) - subtle green tint
- **Visual**: QR-code-like position markers (green), dark background, subtle green for Matrix rain

**Files**:
- `generate.py`: Creates Matrix-themed SVG with QR-like markers and sequential RGB encoding
- `solve.py`: Detects filler values and extracts printable ASCII from each channel

**Testing**: `tests/test_rgb_ascii.py`

### Challenge 03: DTMF
**Implementation**: [03-dtmf/](./03-dtmf/)

**Concept**: Text encoded via telephone keypad (T9) and DTMF tones
- Text → T9 sequences → DTMF audio
- Requires spectral analysis to decode

**Files**:
- `generate.py`: Creates DTMF audio WAV file
- `solve.py`: Analyzes frequencies and decodes

**Testing**: `tests/test_dtmf.py`

### Challenge 04: Morse (Video-Based)
**Implementation**: [04-morse/](./04-morse/)

**Concept**: Matrix-style cascading Chinese characters encoding Morse code

**Technical Implementation**:

#### Video Generation (`generate.py`)
- **Framework**: OpenCV (cv2) for video, PIL/ImageFont for Chinese characters
- **Resolution**: 420x600 pixels
- **Frame Rate**: 30 FPS
- **Scroll Speed**: 100 pixels/second

**Character Encoding**:
- **'点'** (diǎn - "dot") = Morse dot (.)
- **'线'** (xiàn - "line") = Morse dash (-)
- **Filler characters** (decorative, faded green):
  - '雨' (yǔ - "rain")
  - '绿' (lǜ - "green")
  - '码' (mǎ - "code")
  - '数' (shù - "number/digital")
  - '字' (zì - "character/word")

**Visual Design**:
- Bright green (#00FF00): Morse code symbols
- Faded green (#005000): Decorative filler
- 10 characters per line (3 filler + morse + filler padding)
- Video extends 5.5 seconds after last line enters screen

**Performance Optimization**:
1. Pre-render all unique Chinese characters once
2. Store as RGBA images with alpha channel
3. Use alpha blending to composite onto frames
4. Reduces generation time from >30s to ~10-15s

**Music Support** (Optional):
- Uses ffmpeg to combine video with audio track
- Command: `python generate.py "FLAG" music.mp3`
- Creates `output_with_music.mp4`
- Requires: `brew install ffmpeg` (macOS) or `apt-get install ffmpeg` (Linux)

**Legacy Files** (Audio-based, no longer primary):
- `generate.py`: Audio Morse with frequency sweeps
- `solve.py`: Audio Morse decoder
- `solve_video.py`: Computer vision solver (outdated)
- `solve_video_simple.py`: OCR solver (needs updating for Chinese)

**Testing**:
- `tests/test_morse.py` - Audio-based tests (legacy)
- `tests/test_morse_video.py` - Video generation tests (primary)

## Testing Infrastructure

### Test Organization

All tests are located in `tests/` directory:
```
tests/
├── test_all_white_qr.py
├── test_rgb_ascii.py
├── test_dtmf.py
├── test_morse.py          # Audio-based Morse tests
└── test_morse_video.py    # Video-based Morse tests
```

### Running Tests

```bash
# Run all tests
python -m unittest discover tests/ -v

# Run specific challenge
python -m unittest tests.test_morse_video -v

# Run single test
python -m unittest tests.test_morse_video.TestMorseVideoChallenge.test_video_creation_simple -v
```

### Test Coverage

**Challenge 04 Video Tests** (13 tests):
- Character to Morse conversion
- Video properties (dimensions, FPS, codec)
- Duration validation (including 5.5s extra)
- Black screen start
- Green content detection
- Punctuation handling
- Long text support
- Edge cases (empty text)

## Dependencies

### Python Packages

Core dependencies (from `requirements.txt`):
```
numpy>=1.21.0
pillow>=10.4.0
qrcode[pil]>=7.4.2
pyzbar>=0.1.9
scipy>=1.7.0
opencv-python>=4.5.0
pytest>=7.4.0
```

Optional dependencies:
- `pytesseract` - For OCR-based video solving
- `ffmpeg` - For music integration (system package)

### System Requirements

- Python 3.9+
- Chinese font support (STHeiti, PingFang on macOS)
- ffmpeg (optional, for music)

## Configuration

### Challenge 04 Video Parameters

Key settings in `generate.py`:

```python
fps = 30                    # Frames per second
scroll_speed = 100          # Pixels per second
line_height = 70            # Vertical spacing between lines
font_size = 50              # Character size
width = 420                 # Video width
height = 600                # Video height
duration += 5.5             # Extra seconds after last line enters

# Colors (BGR format)
green = (0, 255, 0)         # Bright green for Morse
faded_green = (0, 80, 0)    # Faded green for filler
```

## Deployment Guide

### For CTF Organizers

1. **Generate Challenge Files**:
```bash
cd 01-all-white-qr
python generate.py "HC{YOUR_FLAG}"

cd ../02-rgb-ascii
python generate.py "Cover text here" "HC{YOUR_FLAG}"

cd ../03-dtmf
python generate.py "HC{YOUR_FLAG}"

cd ../04-morse
python generate.py "HC{YOUR_FLAG}"
# Optional with music:
python generate.py "HC{YOUR_FLAG}" background_music.mp3
```

2. **Distribute Files**:
   - Provide only `output.svg`, `output.wav`, or `output.mp4` files
   - Keep `generate.py` and `solve.py` scripts private
   - Include challenge descriptions from README files

3. **Validation**:
   - Run solve scripts to verify flags are recoverable
   - Test with actual challenge files before deployment

### File Permissions

Recommended permissions for distribution:
```bash
chmod 644 output.svg output.wav output.mp4  # Read-only for participants
chmod 700 generate.py solve.py              # Private for organizers
```

## Known Issues and Limitations

### Challenge 04 (Morse Video)

1. **OCR Solver Compatibility**:
   - `solve_video.py` and `solve_video_simple.py` were written for old 'd'/'p' characters
   - Need updates to recognize Chinese characters ('点', '线')
   - Manual observation is the intended primary solution

2. **Font Availability**:
   - Requires Chinese-compatible fonts
   - Falls back to default font if unavailable (may not render correctly)
   - Tested on macOS (STHeiti, PingFang) - Linux/Windows may vary

3. **Video Codec**:
   - Uses mp4v codec (may have compatibility issues)
   - Consider h264 for better compatibility if needed

4. **FFmpeg Dependency**:
   - Music feature requires external ffmpeg installation
   - Gracefully handles missing ffmpeg with error message

## Future Improvements

### Potential Enhancements

1. **Challenge 04 Improvements**:
   - Update OCR solvers for Chinese character recognition
   - Add h264 codec option for better video compatibility
   - Configurable color schemes
   - Support for longer messages with automatic wrapping

2. **General Improvements**:
   - Automated difficulty calibration
   - Progressive hint system
   - Docker containerization for consistent environments
   - Web-based challenge interface

3. **Additional Challenges**:
   - Steganography challenges
   - Multi-layer encoding
   - Time-based encoding

## Troubleshooting

### Common Issues

**Issue**: Chinese characters appear as question marks in video
- **Solution**: Ensure Chinese fonts are installed; PIL/ImageFont will auto-detect

**Issue**: ffmpeg not found when adding music
- **Solution**: Install ffmpeg: `brew install ffmpeg` (macOS) or `apt-get install ffmpeg` (Linux)

**Issue**: Video generation is slow
- **Solution**: This is expected; pre-rendering optimization reduces time to ~10-15s for typical flags

**Issue**: Tests fail with module import errors
- **Solution**: Ensure virtual environment is activated and dependencies installed: `pip install -r tests/requirements.txt`

## Contributing

When adding new challenges or modifying existing ones:

1. Maintain the `generate.py` / `solve.py` structure
2. Add comprehensive tests in `tests/`
3. Update both challenge README and this CLAUDE.md
4. Ensure all tests pass before committing
5. Document any new dependencies

## License and Credits

See main repository LICENSE file for licensing information.

Matrix-style visual design inspired by "The Matrix" (1999).
