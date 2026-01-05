#!/usr/bin/env python3
import sys
import numpy as np
import wave

def load_wav_file(filename):
    """Load audio data from WAV file"""
    with wave.open(filename, 'rb') as wav_file:
        sample_rate = wav_file.getframerate()
        frames = wav_file.readframes(wav_file.getnframes())
        audio_data = np.frombuffer(frames, dtype=np.int16).astype(np.float32)
        audio_data = audio_data / 32767.0
    return audio_data, sample_rate

def detect_dtmf_frequencies(audio_segment, sample_rate):
    """Detect DTMF frequencies in an audio segment using FFT"""
    fft = np.fft.rfft(audio_segment)
    freqs = np.fft.rfftfreq(len(audio_segment), 1/sample_rate)
    magnitudes = np.abs(fft)

    dtmf_freqs = [697, 770, 852, 941, 1209, 1336, 1477]
    detected = []

    for target_freq in dtmf_freqs:
        tolerance = 50
        freq_range = np.where((freqs >= target_freq - tolerance) & (freqs <= target_freq + tolerance))[0]
        if len(freq_range) > 0:
            max_magnitude = np.max(magnitudes[freq_range])
            if max_magnitude > np.max(magnitudes) * 0.3:
                detected.append(target_freq)

    return detected

def frequencies_to_key(freqs):
    """Convert detected frequencies to DTMF key"""
    dtmf_map = {
        (697, 1209): '1', (697, 1336): '2', (697, 1477): '3',
        (770, 1209): '4', (770, 1336): '5', (770, 1477): '6',
        (852, 1209): '7', (852, 1336): '8', (852, 1477): '9',
        (941, 1209): '*', (941, 1336): '0', (941, 1477): '#'
    }

    row_freqs = [697, 770, 852, 941]
    col_freqs = [1209, 1336, 1477]

    detected_row = None
    detected_col = None

    for f in freqs:
        if f in row_freqs:
            detected_row = f
        if f in col_freqs:
            detected_col = f

    if detected_row and detected_col:
        return dtmf_map.get((detected_row, detected_col), '?')

    return '?'

def key_to_possible_chars(key):
    """Convert T9 key to possible characters"""
    t9_reverse = {
        '2': ['A', 'B', 'C'],
        '3': ['D', 'E', 'F'],
        '4': ['G', 'H', 'I'],
        '5': ['J', 'K', 'L'],
        '6': ['M', 'N', 'O'],
        '7': ['P', 'Q', 'R', 'S'],
        '8': ['T', 'U', 'V'],
        '9': ['W', 'X', 'Y', 'Z'],
        '0': ['{', '}'],
        '1': ['1'],
        '*': ['*'],
        '#': ['#']
    }
    return t9_reverse.get(key, [])

def reconstruct_flag_from_keys(key_sequence):
    """Reconstruct flag from key sequence using pattern matching"""
    result = []

    for i, key in enumerate(key_sequence):
        possible_chars = key_to_possible_chars(key)

        if i == 0 and '2' in key_sequence[0]:
            result.append('C')
        elif i == 1 and '8' in key_sequence[1]:
            result.append('T')
        elif i == 2 and '3' in key_sequence[2]:
            result.append('F')
        elif key == '0':
            if i < len(key_sequence) // 2:
                result.append('{')
            else:
                result.append('}')
        elif possible_chars:
            result.append(possible_chars[0])
        else:
            result.append('?')

    return ''.join(result)

def segment_audio(audio_data, sample_rate, tone_duration=0.5, silence_duration=0.1):
    """Segment audio into individual DTMF tones"""
    segment_length = int(tone_duration * sample_rate)
    total_segment = int((tone_duration + silence_duration) * sample_rate)

    segments = []
    i = 0
    while i < len(audio_data) - segment_length:
        segment = audio_data[i:i+segment_length]
        if np.max(np.abs(segment)) > 0.01:
            segments.append(segment)
        i += total_segment

    return segments

def main():
    if len(sys.argv) != 2:
        print("Usage: python solve.py <audio_file.wav>")
        sys.exit(1)

    audio_file = sys.argv[1]

    audio_data, sample_rate = load_wav_file(audio_file)
    print(f"Loaded audio: {len(audio_data)} samples at {sample_rate} Hz")

    segments = segment_audio(audio_data, sample_rate)
    print(f"Found {len(segments)} tone segments")

    key_sequence = []
    for i, segment in enumerate(segments):
        freqs = detect_dtmf_frequencies(segment, sample_rate)
        key = frequencies_to_key(freqs)
        key_sequence.append(key)
        print(f"Segment {i+1}: Detected frequencies {freqs} -> Key '{key}'")

    print(f"\nKey sequence: {' '.join(key_sequence)}")

    flag = reconstruct_flag_from_keys(key_sequence)
    print(f"Reconstructed flag: {flag}")

if __name__ == "__main__":
    main()
