#!/usr/bin/env python3
import unittest
import os
import sys
import tempfile
import shutil
from unittest.mock import patch
import importlib.util

all_white_qr_path = os.path.join(os.path.dirname(__file__), '..', '01-all-white-qr')

# Import generate module from All White QR directory
qr_gen_spec = importlib.util.spec_from_file_location("qr_generate", os.path.join(all_white_qr_path, "generate.py"))
qr_generate = importlib.util.module_from_spec(qr_gen_spec)
qr_gen_spec.loader.exec_module(qr_generate)

# Import solve module from All White QR directory
try:
    qr_solve_spec = importlib.util.spec_from_file_location("qr_solve", os.path.join(all_white_qr_path, "solve.py"))
    qr_solve = importlib.util.module_from_spec(qr_solve_spec)
    qr_solve_spec.loader.exec_module(qr_solve)
    HAS_SOLVE = True
except ImportError:
    HAS_SOLVE = False

class TestAllWhiteQR(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.original_dir = os.getcwd()
        os.chdir(self.test_dir)
    
    def tearDown(self):
        os.chdir(self.original_dir)
        shutil.rmtree(self.test_dir)
    
    def test_generate_creates_svg_file(self):
        test_flag = "CTF{test_flag}"
        qr_generate.generate_inverted_qr(test_flag, "test_output.svg")
        
        self.assertTrue(os.path.exists("test_output.svg"))
        
        with open("test_output.svg", 'r') as f:
            content = f.read()
            self.assertIn('<?xml version="1.0"', content)
            self.assertIn('<svg', content)
            self.assertIn('</svg>', content)
    
    def test_generate_creates_svg_only(self):
        test_flag = "CTF{test_flag}"

        with patch('sys.argv', ['generate.py', test_flag]):
            qr_generate.main()

        self.assertTrue(os.path.exists("output.svg"))
        self.assertFalse(os.path.exists("flag.txt"))
    
    @unittest.skipUnless(HAS_SOLVE, "solve module not available due to missing dependencies")
    def test_solve_recovers_flag(self):
        test_flag = "CTF{test_flag_solve}"
        qr_generate.generate_inverted_qr(test_flag, "test_qr_solve.svg")
        
        result = qr_solve.solve_inverted_qr("test_qr_solve.svg")
        self.assertEqual(result, test_flag)
    
    def test_generate_main_function(self):
        test_flag = "CTF{main_test}"

        with patch('sys.argv', ['qrcode.py', test_flag]):
            qr_generate.main()

        self.assertTrue(os.path.exists("output.svg"))
    
    @unittest.skipUnless(HAS_SOLVE, "solve module not available due to missing dependencies")
    def test_solve_main_function(self):
        test_flag = "CTF{solve_main_test}"
        qr_generate.generate_inverted_qr(test_flag, "solve_main_test.svg")
        
        with patch('sys.argv', ['qr_solve.py', 'solve_main_test.svg']):
            with patch('builtins.print') as mock_print:
                qr_solve.main()
                mock_print.assert_called_with(f"Flag found: {test_flag}")
    
    @unittest.skipUnless(HAS_SOLVE, "solve module not available due to missing dependencies")
    def test_svg_color_inversion(self):
        """Test that the generated SVG uses white-on-white (invisible) colors"""
        test_flag = "HC{color_test}"
        qr_generate.generate_inverted_qr(test_flag, "color_test.svg")

        with open("color_test.svg", 'r') as f:
            content = f.read()

        # Check that white fills are present (white-on-white QR)
        self.assertIn('fill="white"', content)
        self.assertIn('<rect', content)
    
    def test_error_handling(self):
        """Test error handling for invalid inputs"""
        with self.assertRaises(SystemExit):
            with patch('sys.argv', ['qrcode.py']):  # Missing flag argument
                qr_generate.main()
    
    @unittest.skipUnless(HAS_SOLVE, "solve module not available due to missing dependencies")
    def test_roundtrip_encoding_decoding(self):
        """Test encoding and decoding various flag formats"""
        test_cases = [
            "HC{short}",
            "HC{longer_flag_with_more_characters}",
            "HC{sp3c14l_ch4r5_!@#$%}",
            "HC{numbers_123456789}",
            "HC{mixed_Case_And_123_Numbers}",
        ]
        
        for test_flag in test_cases:
            with self.subTest(flag=test_flag):
                svg_file = f"test_{abs(hash(test_flag))}.svg"
                qr_generate.generate_inverted_qr(test_flag, svg_file)
                result = qr_solve.solve_inverted_qr(svg_file)
                self.assertEqual(result, test_flag)
    
    def test_svg_structure(self):
        test_flag = "CTF{structure_test}"
        qr_generate.generate_inverted_qr(test_flag, "structure_test.svg")

        with open("structure_test.svg", 'r') as f:
            content = f.read()

        self.assertIn('fill="white"', content)
        self.assertIn('<rect', content)

if __name__ == '__main__':
    unittest.main()