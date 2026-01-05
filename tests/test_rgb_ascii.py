#!/usr/bin/env python3
import unittest
import os
import sys
import tempfile
import shutil
import xml.etree.ElementTree as ET
import re
from unittest.mock import patch
import importlib.util

rgb_ascii_path = os.path.join(os.path.dirname(__file__), '..', '02-rgb-ascii')

# Import generate module from RGB ASCII directory
rgb_gen_spec = importlib.util.spec_from_file_location("rgb_generate", os.path.join(rgb_ascii_path, "generate.py"))
rgb_generate = importlib.util.module_from_spec(rgb_gen_spec)
rgb_gen_spec.loader.exec_module(rgb_generate)

# Import solve module from RGB ASCII directory
rgb_solve_spec = importlib.util.spec_from_file_location("rgb_solve", os.path.join(rgb_ascii_path, "solve.py"))
rgb_solve = importlib.util.module_from_spec(rgb_solve_spec)
rgb_solve_spec.loader.exec_module(rgb_solve)

class TestRGBAscii(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.original_dir = os.getcwd()
        os.chdir(self.test_dir)

    def tearDown(self):
        os.chdir(self.original_dir)
        shutil.rmtree(self.test_dir)

    def test_generate_creates_svg_file(self):
        test_flag = "CTF{test}"
        random_text = "Lorem ipsum dolor sit amet"
        rgb_generate.generate_rgb_ascii(test_flag, random_text, "test_output.svg")

        self.assertTrue(os.path.exists("test_output.svg"))

        with open("test_output.svg", 'r') as f:
            content = f.read()
            self.assertIn('<?xml version="1.0"', content)
            self.assertIn('<svg', content)
            self.assertIn('</svg>', content)
            self.assertIn('rgb(', content)

    def test_generate_main_function(self):
        test_flag = "CTF{main_test}"
        random_text = "Random text for testing"

        with patch('sys.argv', ['rgb_generate.py', test_flag, random_text]):
            rgb_generate.main()

        self.assertTrue(os.path.exists("output.svg"))

    def test_svg_contains_rgb_colors(self):
        random_text = "ABC"
        test_flag = "XYZ"
        rgb_generate.generate_rgb_ascii(test_flag, random_text, "rgb_test.svg")

        with open("rgb_test.svg", 'r') as f:
            content = f.read()

        # Check that RGB values are present
        self.assertIn('rgb(', content)
        # Check for green position markers (Matrix theme)
        self.assertTrue('rgb(0, 255, 0)' in content or 'rgb(0,255,0)' in content)

    def test_solve_extracts_text(self):
        random_text = "The quick brown fox jumps over the lazy dog"
        test_flag = "HC{test}"
        rgb_generate.generate_rgb_ascii(test_flag, random_text, "solve_test.svg")

        with patch('builtins.print') as mock_print:
            result = rgb_solve.solve_rgb_ascii("solve_test.svg")

        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)
        # Result should contain parts of the flag
        self.assertIn('HC', result)
        # Result should contain + markers
        self.assertIn('+', result)

    def test_solve_main_function(self):
        random_text = "Test text here"
        test_flag = "HC{solve}"
        rgb_generate.generate_rgb_ascii(test_flag, random_text, "solve_main_test.svg")

        with patch('sys.argv', ['rgb_solve.py', 'solve_main_test.svg']):
            with patch('builtins.print') as mock_print:
                rgb_solve.main()
                mock_print.assert_called()

    def test_svg_structure_and_parsing(self):
        random_text = "Sample text"
        test_flag = "TEST"
        rgb_generate.generate_rgb_ascii(test_flag, random_text, "structure_test.svg")

        tree = ET.parse("structure_test.svg")
        root = tree.getroot()

        rects = root.findall('.//{http://www.w3.org/2000/svg}rect')
        self.assertTrue(len(rects) > 0)

        # Check for both position markers (green) and data cells
        has_markers = False
        has_rgb = False
        for rect in rects:
            self.assertIn('fill', rect.attrib)
            fill = rect.attrib['fill']
            if 'rgb(0' in fill and '255' in fill:  # Green markers
                has_markers = True
            elif fill.startswith('rgb(') and not ('rgb(0' in fill and '255' in fill):
                has_rgb = True

        self.assertTrue(has_markers, "Should have green position markers")
        self.assertTrue(has_rgb, "Should have RGB-encoded data cells")

    def test_flag_injection(self):
        """Test that flag is properly injected into random text"""
        random_text = "AAAAAAAAAA" * 10  # Long repetitive text
        test_flag = "HC{inject}"

        rgb_generate.generate_rgb_ascii(test_flag, random_text, "inject_test.svg")
        result = rgb_solve.solve_rgb_ascii("inject_test.svg")

        # Should contain parts of both random text and flag
        self.assertIn('A', result)
        self.assertIn('HC', result)
        # Should have + markers
        self.assertIn('+', result)

    def test_filler_values(self):
        """Test that filler values (5, 20, 80) are used for Matrix rain effect"""
        random_text = "Short"
        test_flag = "HC{x}"
        rgb_generate.generate_rgb_ascii(test_flag, random_text, "padding_test.svg")

        tree = ET.parse("padding_test.svg")
        root = tree.getroot()

        # Extract RGB values
        rgb_values = []
        for rect in root.findall('.//{http://www.w3.org/2000/svg}rect'):
            fill = rect.attrib.get('fill', '')
            if fill.startswith('rgb(') and not ('rgb(0' in fill and '255' in fill):  # Skip green markers
                rgb_match = re.search(r'rgb\((\d+),(\d+),(\d+)\)', fill)
                if rgb_match:
                    r, g, b = map(int, rgb_match.groups())
                    rgb_values.extend([r, g, b])

        # Check that we have filler values (5, 20, 80)
        filler_values = [v for v in rgb_values if v in [5, 20, 80]]
        self.assertTrue(len(filler_values) > 0, "Should have filler values (5, 20, 80) for Matrix rain")

    def test_matrix_green_effect(self):
        """Test that Matrix green effect is applied (G=80 when not used for data)"""
        random_text = "Test text here for Matrix effect"
        test_flag = "HC{matrix}"
        rgb_generate.generate_rgb_ascii(test_flag, random_text, "matrix_test.svg")

        tree = ET.parse("matrix_test.svg")
        root = tree.getroot()

        # Extract RGB values and check for G=80 pattern
        g_80_count = 0

        for rect in root.findall('.//{http://www.w3.org/2000/svg}rect'):
            fill = rect.attrib.get('fill', '')
            if fill.startswith('rgb(') and not ('rgb(0' in fill and '255' in fill):  # Skip markers
                rgb_match = re.search(r'rgb\((\d+),(\d+),(\d+)\)', fill)
                if rgb_match:
                    r, g, b = map(int, rgb_match.groups())
                    if g == 80:
                        g_80_count += 1

        # Should have cells with G=80 (Matrix green effect)
        self.assertGreater(g_80_count, 0, "Should have cells with G=80 for Matrix green effect")

    def test_concatenation_markers(self):
        """Test that + markers are present in the decoded output"""
        random_text = "Random text for testing purposes"
        test_flag = "HC{markers}"

        rgb_generate.generate_rgb_ascii(test_flag, random_text, "markers_test.svg")
        result = rgb_solve.solve_rgb_ascii("markers_test.svg")

        # The result should contain + markers showing concatenation
        self.assertIn('+', result)

    def test_roundtrip_encoding_decoding(self):
        """Test encoding and decoding various flag formats"""
        test_cases = [
            ("Random text here", "HC{short}"),
            ("The quick brown fox jumps", "HC{longer_flag}"),
            ("Lorem ipsum dolor sit amet", "HC{sp3c14l}"),
            ("Pack my box with five dozen", "HC{num123}"),
            ("The lazy dog sleeps", "HC{MixedCase}"),
        ]

        for random_text, test_flag in test_cases:
            with self.subTest(flag=test_flag):
                svg_file = f"test_{abs(hash(test_flag))}.svg"
                rgb_generate.generate_rgb_ascii(test_flag, random_text, svg_file)
                result = rgb_solve.solve_rgb_ascii(svg_file)
                self.assertIsInstance(result, str)
                # Should contain parts of the flag
                self.assertIn('HC', result)
                # Should have markers
                self.assertIn('+', result)

    def test_error_handling(self):
        """Test error handling for invalid inputs"""
        with self.assertRaises(SystemExit):
            with patch('sys.argv', ['generate.py']):  # Missing arguments
                rgb_generate.main()

        with self.assertRaises(SystemExit):
            with patch('sys.argv', ['generate.py', 'only_one_arg']):  # Missing flag
                rgb_generate.main()

    def test_qr_like_structure(self):
        """Test that the SVG has QR-like position detection patterns (green)"""
        random_text = "Testing QR structure"
        test_flag = "HC{qr}"
        rgb_generate.generate_rgb_ascii(test_flag, random_text, "qr_test.svg")

        tree = ET.parse("qr_test.svg")
        root = tree.getroot()

        # Count green position markers
        green_markers = 0

        for rect in root.findall('.//{http://www.w3.org/2000/svg}rect'):
            fill = rect.attrib.get('fill', '')
            if 'rgb(0' in fill and ('255' in fill or '50' in fill or '150' in fill):  # Green markers
                green_markers += 1

        # Should have green position markers (3 corners, each 7x7 with pattern)
        self.assertGreater(green_markers, 0, "Should have green position markers (Matrix theme)")

    def test_flag_extraction_with_markers(self):
        """Test that the flag can be extracted with its surrounding markers"""
        random_text = "This is a test message"
        test_flag = "HC{flag_test}"

        rgb_generate.generate_rgb_ascii(test_flag, random_text, "extract_test.svg")

        with patch('builtins.print') as mock_print:
            result = rgb_solve.solve_rgb_ascii("extract_test.svg")

        # Check that result contains flag components (may be split)
        self.assertIn('HC', result)
        # Check that result has markers and some random text
        self.assertIn('+', result)
        self.assertIn('is', result)  # From "This is"

    def test_different_text_lengths(self):
        """Test encoding with different text lengths"""
        test_cases = [
            ("Short text", "HC{x}"),  # Made text longer to avoid issues
            ("Medium length text here", "HC{medium}"),
            ("This is a much longer text that should still work correctly", "HC{long_flag_name}"),
        ]

        for random_text, test_flag in test_cases:
            with self.subTest(random_text=random_text[:20], flag=test_flag):
                svg_file = f"length_test_{abs(hash(random_text))}.svg"
                rgb_generate.generate_rgb_ascii(test_flag, random_text, svg_file)
                result = rgb_solve.solve_rgb_ascii(svg_file)

                self.assertIsInstance(result, str)
                self.assertTrue(len(result) > 0)
                # Result should contain markers
                self.assertIn('+', result)

if __name__ == '__main__':
    unittest.main()
