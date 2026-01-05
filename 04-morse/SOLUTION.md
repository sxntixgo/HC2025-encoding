# Challenge 04: Neo Sees The Code - Solution Guide

**For CTF Organizers Only**

## Overview

This challenge encodes Morse code in a Matrix-style falling character video. Bright green Chinese characters represent dots and dashes, while faded characters are decorative background noise.

## How It Works

1. Text is converted to Morse code
2. Each Morse character becomes a line of falling Chinese glyphs:
   - `点` (diǎn - "dot") = Morse dot (.)
   - `线` (xiàn - "line") = Morse dash (-)
3. Filler characters create the Matrix rain effect (faded green):
   - `雨` (yǔ - "rain")
   - `绿` (lǜ - "green")
   - `码` (mǎ - "code")
   - `数` (shù - "number")
   - `字` (zì - "character")
4. Each line = 3 filler chars + Morse symbols + padding (10 chars total)
5. Punctuation (`{`, `}`, `_`) appears unchanged

## Solving the Challenge

### Method 1: Manual Observation (Intended)

1. Watch the video and identify bright vs faded characters
2. Note down bright characters for each falling line:
   - `点` → dot (.)
   - `线` → dash (-)
   - `{`, `}`, `_` → literal characters
3. Convert each line's Morse to a letter:
   ```
   ....  → H
   -.-.  → C
   {     → {
   -     → T
   .     → E
   ...   → S
   -     → T
   }     → }
   ```
4. Combine to get the flag

### Method 2: Frame-by-Frame Analysis

1. Open video in VLC or similar player
2. Step through frames (press E in VLC)
3. Record each line of bright characters
4. Decode Morse code

### Dependencies

For generation:
```bash
pip install numpy opencv-python pillow
brew install ffmpeg  # Optional, for music
```

## Video Parameters

- **Resolution:** 420x600 pixels
- **Frame Rate:** 30 FPS
- **Scroll Speed:** 100 pixels/second
- **Line Height:** 70 pixels
- **Font Size:** 50 pixels
- **Colors:** Bright green (#00FF00) for Morse, faded green (#005000) for filler

## Morse Code Reference

```
A .-    B -...  C -.-.  D -..   E .     F ..-.
G --.   H ....  I ..    J .---  K -.-   L .-..
M --    N -.    O ---   P .--.  Q --.-  R .-.
S ...   T -     U ..-   V ...-  W .--   X -..-
Y -.--  Z --..

0 ----- 1 .---- 2 ..--- 3 ...-- 4 ....-
5 ..... 6 -.... 7 --... 8 ---.. 9 ----.
```

## Expected Solution Path

Participants should:
1. Recognize the Matrix-style visual as more than decoration
2. Notice some characters are brighter than others
3. Research or recognize the Chinese characters:
   - `点` means "dot/point"
   - `线` means "line"
4. Connect this to Morse code (dots and dashes)
5. Record the sequence of bright characters per line
6. Decode using Morse code table
