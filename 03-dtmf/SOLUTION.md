# Challenge 03: Morpheus Message - Solution Guide

**For CTF Organizers Only**

## Overview

This challenge encodes text using DTMF (Dual-Tone Multi-Frequency) tones combined with T9 keypad mapping. The flag is converted to phone keypad presses, then each keypress is encoded as a DTMF audio tone.

## How It Works

1. Text is converted to T9 keypad sequences:
   - A, B, C → 2
   - D, E, F → 3
   - G, H, I → 4
   - J, K, L → 5
   - M, N, O → 6
   - P, Q, R, S → 7
   - T, U, V → 8
   - W, X, Y, Z → 9
   - `{` and `}` → 0

2. Each keypress generates a DTMF tone (two simultaneous frequencies):
   ```
           1209 Hz   1336 Hz   1477 Hz
   697 Hz:    1         2         3
   770 Hz:    4         5         6
   852 Hz:    7         8         9
   941 Hz:    *         0         #
   ```

## Solving the Challenge

### Method 1: Automated Solver

```bash
python solve.py morpheusmessage.wav
```

The solver:
- Loads and segments the WAV file
- Performs FFT analysis on each tone segment
- Detects DTMF frequency pairs
- Maps frequencies to keypad keys
- Reconstructs text using T9 reverse mapping

### Method 2: Manual Approach

1. Open the WAV in audio analysis software (Audacity, Sonic Visualizer)
2. View the spectrogram to identify frequency components
3. Match frequencies to the DTMF table above
4. Record the key sequence
5. Apply T9 reverse mapping (with context for ambiguous letters)

### Dependencies

```bash
pip install numpy scipy
```

## Audio Parameters

- **Sample Rate:** 8000 Hz
- **Tone Duration:** 0.5 seconds per character
- **Silence Duration:** 0.1 seconds between tones
- **Format:** 16-bit mono WAV
- **Fade in/out:** 50ms (prevents clicking artifacts)

## Challenge Difficulty

The T9 mapping is **lossy** - multiple letters map to the same key:
- Key `2` could be A, B, or C
- Key `7` could be P, Q, R, or S

Solvers must use context and pattern recognition:
- Flags start with `HC{` (keys: 4-2-0)
- Flags end with `}` (key: 0)
- Common words help disambiguate letters

## Expected Solution Path

Participants should:
1. Recognize the audio as telephone touch-tones (DTMF)
2. Use spectral analysis to identify frequency pairs
3. Map frequencies to keypad digits
4. Recognize T9 encoding pattern
5. Apply context to resolve ambiguous letters
6. Reconstruct the flag
