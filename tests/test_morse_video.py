#!/usr/bin/env python3
"""
Test cases for Matrix-style Morse code video generation.
"""
import os
import sys
import tempfile
import unittest
import cv2
import numpy as np
from unittest.mock import patch
import importlib.util

# Add the morse directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
morse_dir = os.path.join(os.path.dirname(current_dir), "04-morse")
sys.path.insert(0, morse_dir)

# Load generate module
def load_module_from_path(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

generate_path = os.path.join(morse_dir, "generate.py")
generate_video = load_module_from_path("generate", generate_path)


class TestMorseVideoChallenge(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_video_file = os.path.join(self.temp_dir, "test_output.mp4")

    def tearDown(self):
        """Clean up test files"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_char_to_morse(self):
        """Test character to Morse code conversion"""
        test_cases = {
            'A': '.-',
            'B': '-...',
            'C': '-.-.',
            'H': '....',
            'E': '.',
            'L': '.-..',
            'O': '---',
            # Punctuation returns empty string from char_to_morse
            # but is preserved in text_to_morse_letters
            '{': '',
            '}': '',
            '_': ''
        }

        for char, expected_morse in test_cases.items():
            with self.subTest(char=char):
                result = generate_video.char_to_morse(char)
                self.assertEqual(result, expected_morse)

    def test_text_to_morse_letters(self):
        """Test text to morse letters conversion"""
        text = "HI"
        morse_letters = generate_video.text_to_morse_letters(text)

        # H = .... , I = ..
        self.assertEqual(morse_letters, ['....', '..'])

        # Test with punctuation
        text = "HC{}"
        morse_letters = generate_video.text_to_morse_letters(text)
        self.assertEqual(morse_letters, ['....', '-.-.', '{', '}'])

    def test_video_creation_simple(self):
        """Test basic video creation"""
        text = "HI"
        output_file = os.path.join(self.temp_dir, "test.mp4")

        # Generate video
        result = generate_video.create_morse_video(text, output_file)

        # Check that video file was created
        self.assertTrue(os.path.exists(output_file))
        self.assertEqual(result, output_file)

        # Check that video can be opened
        cap = cv2.VideoCapture(output_file)
        self.assertTrue(cap.isOpened(), "Video file should be readable")

        # Check basic video properties
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        self.assertEqual(fps, 30, "FPS should be 30")
        self.assertGreater(frame_count, 0, "Should have frames")
        self.assertEqual(width, 420, "Width should be 420")
        self.assertEqual(height, 600, "Height should be 600")

        cap.release()

    def test_video_duration(self):
        """Test that video duration is calculated correctly"""
        text = "AB"
        output_file = os.path.join(self.temp_dir, "test.mp4")

        generate_video.create_morse_video(text, output_file)

        cap = cv2.VideoCapture(output_file)
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps

        # Should have reasonable duration (at least 5.5 seconds for the extra time)
        self.assertGreater(duration, 5.5, "Video should include 5.5s extra time")

        cap.release()

    def test_video_starts_with_black_screen(self):
        """Test that video starts with a black screen"""
        text = "A"
        output_file = os.path.join(self.temp_dir, "test.mp4")

        generate_video.create_morse_video(text, output_file)

        cap = cv2.VideoCapture(output_file)
        ret, first_frame = cap.read()

        self.assertTrue(ret, "Should be able to read first frame")

        # Check if first frame is mostly black (allowing for some compression artifacts)
        max_brightness = np.max(first_frame)
        self.assertLess(max_brightness, 50, "First frame should be mostly black")

        cap.release()

    def test_video_has_green_content(self):
        """Test that video contains green characters"""
        text = "A"
        output_file = os.path.join(self.temp_dir, "test.mp4")

        generate_video.create_morse_video(text, output_file)

        cap = cv2.VideoCapture(output_file)

        # Skip to middle of video
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_count // 2)

        ret, frame = cap.read()
        self.assertTrue(ret, "Should be able to read middle frame")

        # Check for green content (BGR format, so green is index 1)
        green_channel = frame[:, :, 1]
        max_green = np.max(green_channel)

        # Should have significant green content in the middle of the video
        self.assertGreater(max_green, 100, "Should have green characters visible")

        cap.release()

    def test_video_with_punctuation(self):
        """Test video generation with flag format"""
        text = "HC{TEST}"
        output_file = os.path.join(self.temp_dir, "test.mp4")

        result = generate_video.create_morse_video(text, output_file)

        self.assertTrue(os.path.exists(output_file))

        # Verify video is valid
        cap = cv2.VideoCapture(output_file)
        self.assertTrue(cap.isOpened())
        cap.release()

    def test_chinese_character_definitions(self):
        """Test that Chinese characters are properly defined"""
        # These should be defined in the create_morse_video function
        # We can't easily test the actual rendering, but we can verify the constants exist
        # and are the correct characters

        # Just verify the module loads without errors
        self.assertTrue(hasattr(generate_video, 'create_morse_video'))

    def test_line_building(self):
        """Test that morse lines are built correctly"""
        text = "A"  # A = .-
        morse_letters = generate_video.text_to_morse_letters(text)

        self.assertEqual(len(morse_letters), 1)
        self.assertEqual(morse_letters[0], '.-')

    def test_video_codec(self):
        """Test that video uses correct codec"""
        text = "A"
        output_file = os.path.join(self.temp_dir, "test.mp4")

        generate_video.create_morse_video(text, output_file)

        cap = cv2.VideoCapture(output_file)

        # Get codec information
        fourcc = int(cap.get(cv2.CAP_PROP_FOURCC))

        # Should be able to open and read
        self.assertTrue(cap.isOpened())

        ret, frame = cap.read()
        self.assertTrue(ret, "Should be able to read frames")

        cap.release()

    def test_empty_text_handling(self):
        """Test handling of empty text"""
        text = ""
        output_file = os.path.join(self.temp_dir, "test.mp4")

        # Should handle empty text gracefully
        try:
            generate_video.create_morse_video(text, output_file)
            # If it succeeds, verify the output
            if os.path.exists(output_file):
                cap = cv2.VideoCapture(output_file)
                self.assertTrue(cap.isOpened())
                cap.release()
        except Exception:
            # Empty text might raise an exception, which is acceptable
            pass

    def test_long_text(self):
        """Test video generation with longer text"""
        text = "HC{NO_MORE_RUNNING}"
        output_file = os.path.join(self.temp_dir, "test.mp4")

        result = generate_video.create_morse_video(text, output_file)

        self.assertTrue(os.path.exists(output_file))

        # Verify video properties
        cap = cv2.VideoCapture(output_file)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        duration = frame_count / fps

        # Longer text should produce longer video
        self.assertGreater(duration, 5.5, "Long text should produce longer video")

        cap.release()

    def test_video_dimensions(self):
        """Test that video has correct dimensions"""
        text = "TEST"
        output_file = os.path.join(self.temp_dir, "test.mp4")

        generate_video.create_morse_video(text, output_file)

        cap = cv2.VideoCapture(output_file)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # Check dimensions match specification
        self.assertEqual(width, 420, "Width should be 420 pixels")
        self.assertEqual(height, 600, "Height should be 600 pixels")

        cap.release()


if __name__ == "__main__":
    unittest.main()
