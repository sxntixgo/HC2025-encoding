#!/usr/bin/env python3
import sys
import numpy as np
import wave

def char_to_key(char):
    """Convert character to T9 key number using standard T9 mapping"""
    t9_mapping = {
        'A': '2', 'B': '2', 'C': '2',
        'D': '3', 'E': '3', 'F': '3',
        'G': '4', 'H': '4', 'I': '4',
        'J': '5', 'K': '5', 'L': '5',
        'M': '6', 'N': '6', 'O': '6',
        'P': '7', 'Q': '7', 'R': '7', 'S': '7',
        'T': '8', 'U': '8', 'V': '8',
        'W': '9', 'X': '9', 'Y': '9', 'Z': '9',
        '0': '0', '1': '1', '2': '2', '3': '3', '4': '4',
        '5': '5', '6': '6', '7': '7', '8': '8', '9': '9',
        '{': '0', '}': '0',
        '*': '*', '#': '#'
    }
    return t9_mapping.get(char.upper(), '1')

def key_to_dtmf_freq(key):
    """Convert key to DTMF frequency pair (row_freq, col_freq)"""
    dtmf_freqs = {
        '1': (697, 1209), '2': (697, 1336), '3': (697, 1477),
        '4': (770, 1209), '5': (770, 1336), '6': (770, 1477),
        '7': (852, 1209), '8': (852, 1336), '9': (852, 1477),
        '*': (941, 1209), '0': (941, 1336), '#': (941, 1477)
    }
    return dtmf_freqs.get(key, (697, 1209))

def generate_dtmf_tone(key, duration=0.5, sample_rate=8000, amplitude=0.3):
    """Generate DTMF tone for a specific key"""
    row_freq, col_freq = key_to_dtmf_freq(key)

    t = np.linspace(0, duration, int(sample_rate * duration), False)

    tone = amplitude * (np.sin(2 * np.pi * row_freq * t) + np.sin(2 * np.pi * col_freq * t))

    fade_samples = int(0.05 * sample_rate)
    fade_in = np.linspace(0, 1, fade_samples)
    fade_out = np.linspace(1, 0, fade_samples)

    tone[:fade_samples] *= fade_in
    tone[-fade_samples:] *= fade_out

    return tone

def generate_silence(duration=0.1, sample_rate=8000):
    """Generate silence between tones"""
    return np.zeros(int(sample_rate * duration))

def text_to_dtmf_audio(text, output_file, tone_duration=0.5, silence_duration=0.1):
    """Convert text to DTMF audio using T9 mapping"""
    sample_rate = 8000
    audio_data = np.array([])

    key_sequence = []

    for char in text:
        key = char_to_key(char)
        key_sequence.append(key)

        tone = generate_dtmf_tone(key, tone_duration, sample_rate)
        silence = generate_silence(silence_duration, sample_rate)

        audio_data = np.concatenate([audio_data, tone, silence])

    audio_data = audio_data / np.max(np.abs(audio_data)) * 0.8

    audio_int16 = (audio_data * 32767).astype(np.int16)

    with wave.open(output_file, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_int16.tobytes())

    print(f"DTMF audio saved to {output_file}")
    print(f"Key sequence: {' '.join(key_sequence)}")

    return key_sequence

def main():
    if len(sys.argv) != 2:
        print("Usage: python generate.py <flag>")
        sys.exit(1)

    flag = sys.argv[1]

    text_to_dtmf_audio(flag, "output.wav")

if __name__ == "__main__":
    main()
