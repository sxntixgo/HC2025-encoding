#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate Matrix-style video with cascading lines of characters.
Each line has Chinese glyphs representing morse code with Matrix rain effect.
"""
import sys
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont
import os

def load_chinese_font(font_size):
    """Load a font that supports Chinese characters"""
    try:
        # Try common system fonts that support Chinese
        font_paths = [
            '/System/Library/Fonts/STHeiti Light.ttc',  # macOS
            '/System/Library/Fonts/PingFang.ttc',  # macOS
            '/usr/share/fonts/truetype/arphic/uming.ttc',  # Linux
            '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc',  # Linux
            'C:\\Windows\\Fonts\\msyh.ttc',  # Windows
        ]
        for fp in font_paths:
            if os.path.exists(fp):
                return ImageFont.truetype(fp, font_size)
        return ImageFont.load_default()
    except:
        return ImageFont.load_default()

def render_char_image(char, font, font_size, color):
    """Pre-render a character as an image with transparency"""
    # Create image with alpha channel
    img_size = int(font_size * 1.5)
    img = Image.new('RGBA', (img_size, img_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # PIL uses RGB
    rgb_color = (color[2], color[1], color[0], 255)
    draw.text((0, 0), char, font=font, fill=rgb_color)

    return np.array(img)

def overlay_char_image(frame, char_img, position):
    """Overlay a pre-rendered character image with transparency"""
    x, y = position
    h, w = char_img.shape[:2]

    # Bounds check
    if y < 0 or y + h > frame.shape[0] or x < 0 or x + w > frame.shape[1]:
        return frame

    # Extract alpha channel
    alpha = char_img[:, :, 3] / 255.0

    # Blend
    for c in range(3):
        frame[y:y+h, x:x+w, c] = (
            alpha * char_img[:, :, c] +
            (1 - alpha) * frame[y:y+h, x:x+w, c]
        )

    return frame

def char_to_morse(char):
    """Convert character to Morse code"""
    morse_table = {
        'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.',
        'G': '--.', 'H': '....', 'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..',
        'M': '--', 'N': '-.', 'O': '---', 'P': '.--.', 'Q': '--.-', 'R': '.-.',
        'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
        'Y': '-.--', 'Z': '--..',
        '0': '-----', '1': '.----', '2': '..---', '3': '...--', '4': '....-',
        '5': '.....', '6': '-....', '7': '--...', '8': '---..', '9': '----.',
        ' ': ' '
    }
    return morse_table.get(char.upper(), '')

def text_to_morse_letters(text):
    """Convert text to list of morse code letters"""
    morse_letters = []
    for char in text:
        if char == ' ':
            morse_letters.append('   ')
        elif char in '{}_':  # Include underscore
            morse_letters.append(char)
        else:
            morse_pattern = char_to_morse(char)
            if morse_pattern:
                morse_letters.append(morse_pattern)
    return morse_letters

def create_morse_video(text, output_file='output.mp4', width=420, height=600):
    """
    Create Matrix-style cascading video.

    Each line = x + morse_code + x_padding (total 6 chars)
    Lines scroll upward continuously with no gaps.
    """
    morse_letters = text_to_morse_letters(text)
    print(f"Text: {text}")
    print(f"Morse letters: {morse_letters}")

    # Chinese glyphs (safe, common characters)
    DOT_CHAR = '点'      # diǎn - means "dot/point" - represents dot in morse
    DASH_CHAR = '线'     # xiàn - means "line" - represents dash in morse

    # Multiple filler characters for variety
    FILLER_CHARS = [
        '雨',  # yǔ - "rain"
        '绿',  # lǜ - "green"
        '码',  # mǎ - "code"
        '数',  # shù - "number/digital"
        '字',  # zì - "character/word"
    ]

    # Build lines
    import random
    random.seed(42)  # For consistent filler character selection

    lines = []
    for morse_letter in morse_letters:
        if not morse_letter.strip():
            continue

        # Convert morse to display chars
        morse_chars = []
        for symbol in morse_letter:
            if symbol == '.':
                morse_chars.append(DOT_CHAR)
            elif symbol == '-':
                morse_chars.append(DASH_CHAR)
            elif symbol in '{}_':  # Handle special characters
                morse_chars.append(symbol)

        # Build line: xxx + morse + xxx (total 10 chars) with random filler chars
        line = [random.choice(FILLER_CHARS), random.choice(FILLER_CHARS), random.choice(FILLER_CHARS)] + morse_chars
        while len(line) < 10:
            line.append(random.choice(FILLER_CHARS))

        lines.append(line)

    # Reverse lines so HC{ appears first in video (top to bottom)
    # Currently lines are [H, C, {, T, E, S, T, }]
    # We want [}, T, S, E, T, {, C, H] so H appears first when scrolling down
    lines.reverse()

    # Add padding lines before message (3 lines of random filler chars)
    for _ in range(3):
        padding_line = [random.choice(FILLER_CHARS) for _ in range(10)]
        lines.insert(0, padding_line)

    # Add padding lines after message
    # Add 1 line of random fillers first
    lines.append([random.choice(FILLER_CHARS) for _ in range(10)])

    # Add 4 lines with random filler and space pattern (fading effect)
    for i in range(4):
        fade_line = []
        density = 0.7 - (i * 0.15)  # Decreasing density
        for _ in range(10):
            if random.random() < density:
                fade_line.append(random.choice(FILLER_CHARS))
            else:
                fade_line.append(' ')
        lines.append(fade_line)

    print(f"\nLines (top to bottom as displayed):")
    for line in lines:  # Print in order to show actual display
        print(''.join(line))

    # Video settings
    fps = 30
    scroll_speed = 100  # pixels per second (doubled from 50)
    line_height = 70  # vertical spacing between lines

    # Calculate how long it takes for all lines to scroll through
    # Start with all lines above screen, end when last line enters screen (y=0)
    # Last line starts at position: (len(lines)-1) * line_height
    # We want it to reach y=0, so scroll_offset needs to be: len(lines) * line_height
    total_scroll_distance = (len(lines) * line_height)
    duration = total_scroll_distance / scroll_speed
    duration += 6.27  # Add 6 extra seconds
    total_frames = int(duration * fps)

    # Initialize video
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_file, fourcc, fps, (width, height))

    # Font settings
    font_size = 50
    green = (0, 255, 0)  # Bright green for morse (BGR)
    faded_green = (0, 80, 0)  # Faded for filler chars (BGR)
    char_spacing = 45  # Reduced spacing - tighter layout

    x_start = -20  # Start off-screen to left (some chars will be cut)

    # Pre-render all unique characters
    print("Pre-rendering characters...")
    font = load_chinese_font(font_size)
    char_images = {}

    # Collect all unique characters
    unique_chars = set()
    for line in lines:
        for char in line:
            if char != ' ':
                unique_chars.add(char)

    # Render each unique character in both colors
    for char in unique_chars:
        if char in FILLER_CHARS:
            char_images[(char, 'faded')] = render_char_image(char, font, font_size, faded_green)
        else:
            char_images[(char, 'bright')] = render_char_image(char, font, font_size, green)

    # Generate frames
    print(f"Generating {total_frames} frames...")
    for frame_num in range(total_frames):
        frame = np.zeros((height, width, 3), dtype=np.uint8)

        # Calculate scroll offset (lines move downward)
        # Start with negative offset to ensure black screen at beginning
        scroll_offset = frame_num / fps * scroll_speed - (len(lines) * line_height)

        # Draw each line
        for line_idx, line in enumerate(lines):
            # Start well above screen
            y_position = (line_idx * line_height) + scroll_offset

            # Only draw if visible
            if -50 < y_position < height + 50:
                x_position = x_start
                for char in line:
                    # Skip spaces (transparent)
                    if char == ' ':
                        x_position += char_spacing
                        continue

                    # Determine color key: faded for filler chars, bright for morse
                    color_key = 'faded' if char in FILLER_CHARS else 'bright'

                    # Get pre-rendered character
                    char_img = char_images.get((char, color_key))
                    if char_img is not None:
                        overlay_char_image(frame, char_img, (x_position, int(y_position)))

                    x_position += char_spacing

        out.write(frame)

        # Progress indicator
        if frame_num % 30 == 0:
            print(f"Progress: {frame_num}/{total_frames} frames ({100*frame_num//total_frames}%)")

    out.release()
    print(f"\nVideo saved to {output_file}")
    print(f"Total frames: {total_frames}")
    print(f"Duration: {total_frames / fps:.2f} seconds")
    print(f"\nChinese Glyphs Used:")
    print(f"  '点' (diǎn - 'dot/point') = dot (.) in morse code")
    print(f"  '线' (xiàn - 'line') = dash (-) in morse code")
    print(f"  Filler characters (Matrix rain):")
    print(f"    '雨' (yǔ - 'rain')")
    print(f"    '绿' (lǜ - 'green')")
    print(f"    '码' (mǎ - 'code')")
    print(f"    '数' (shù - 'number/digital')")
    print(f"    '字' (zì - 'character/word')")
    print(f"  '{', '}', '_' = unchanged (flag delimiters/separator)")

    return output_file

def add_music_to_video(video_file, music_file, output_file='output_with_music.mp4'):
    """
    Add music to video file using ffmpeg.

    Args:
        video_file: Path to input video file
        music_file: Path to music file (mp3, wav, etc.)
        output_file: Path to output video file with music
    """
    import subprocess

    print(f"\nAdding music to video...")
    print(f"Video: {video_file}")
    print(f"Music: {music_file}")

    # Use ffmpeg to combine video and audio
    # -shortest makes output duration match the shorter of video/audio
    command = [
        'ffmpeg', '-y',  # -y to overwrite output file
        '-i', video_file,  # Input video
        '-i', music_file,  # Input music
        '-c:v', 'copy',  # Copy video codec (no re-encoding)
        '-c:a', 'aac',  # Encode audio as AAC
        '-shortest',  # End when shortest stream ends
        output_file
    ]

    try:
        subprocess.run(command, check=True, capture_output=True)
        print(f"Video with music saved to: {output_file}")
        return output_file
    except subprocess.CalledProcessError as e:
        print(f"Error adding music: {e}")
        print(f"Make sure ffmpeg is installed: brew install ffmpeg (macOS) or apt-get install ffmpeg (Linux)")
        return None
    except FileNotFoundError:
        print("ffmpeg not found. Please install it:")
        print("  macOS: brew install ffmpeg")
        print("  Linux: sudo apt-get install ffmpeg")
        print("  Windows: Download from https://ffmpeg.org/download.html")
        return None

def main():
    if len(sys.argv) < 2:
        print("Usage: python generate.py <text> [music_file]")
        print("  <text>: Text to encode in morse code")
        print("  [music_file]: Optional path to music file to add to video")
        sys.exit(1)

    text = sys.argv[1]
    music_file = sys.argv[2] if len(sys.argv) > 2 else None

    # Generate video
    video_file = create_morse_video(text, 'output.mp4')

    # Add music if provided
    if music_file:
        if os.path.exists(music_file):
            add_music_to_video(video_file, music_file, 'output_with_music.mp4')
        else:
            print(f"\nWarning: Music file not found: {music_file}")
            print("Video created without music.")

if __name__ == "__main__":
    main()
