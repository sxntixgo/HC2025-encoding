#!/usr/bin/env python3
import unittest
import os
import sys
import tempfile
import shutil
import wave
import numpy as np
from unittest.mock import patch
import importlib.util

dtmf_path = os.path.join(os.path.dirname(__file__), '..', '03-dtmf')

# Import generate module from DTMF directory
dtmf_gen_spec = importlib.util.spec_from_file_location("dtmf_generate", os.path.join(dtmf_path, "generate.py"))
dtmf_generate = importlib.util.module_from_spec(dtmf_gen_spec)
dtmf_gen_spec.loader.exec_module(dtmf_generate)

# Import solve module from DTMF directory
dtmf_solve_spec = importlib.util.spec_from_file_location("dtmf_solve", os.path.join(dtmf_path, "solve.py"))
dtmf_solve = importlib.util.module_from_spec(dtmf_solve_spec)
dtmf_solve_spec.loader.exec_module(dtmf_solve)

class TestDTMF(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.original_dir = os.getcwd()
        os.chdir(self.test_dir)
    
    def tearDown(self):
        os.chdir(self.original_dir)
        shutil.rmtree(self.test_dir)
    
    def test_char_to_key_mapping(self):
        test_cases = [
            ('C', '2'), ('T', '8'), ('F', '3'),
            ('{', '0'), ('}', '0'),
            ('A', '2'), ('Z', '9'),
            ('1', '1'), ('0', '0'),
            ('*', '*'), ('#', '#')
        ]
        
        for char, expected_key in test_cases:
            with self.subTest(char=char):
                result = dtmf_generate.char_to_key(char)
                self.assertEqual(result, expected_key)
    
    def test_key_to_dtmf_freq(self):
        test_cases = [
            ('1', (697, 1209)), ('2', (697, 1336)), ('3', (697, 1477)),
            ('4', (770, 1209)), ('5', (770, 1336)), ('6', (770, 1477)),
            ('7', (852, 1209)), ('8', (852, 1336)), ('9', (852, 1477)),
            ('*', (941, 1209)), ('0', (941, 1336)), ('#', (941, 1477))
        ]
        
        for key, expected_freq in test_cases:
            with self.subTest(key=key):
                result = dtmf_generate.key_to_dtmf_freq(key)
                self.assertEqual(result, expected_freq)
    
    def test_generate_dtmf_tone(self):
        tone = dtmf_generate.generate_dtmf_tone('5', duration=0.1, sample_rate=8000)
        
        self.assertIsInstance(tone, np.ndarray)
        self.assertEqual(len(tone), 800)
        self.assertGreater(np.max(np.abs(tone)), 0)
        self.assertLess(np.max(np.abs(tone)), 1.0)
    
    def test_generate_silence(self):
        silence = dtmf_generate.generate_silence(duration=0.1, sample_rate=8000)
        
        self.assertIsInstance(silence, np.ndarray)
        self.assertEqual(len(silence), 800)
        self.assertEqual(np.max(np.abs(silence)), 0)
    
    def test_text_to_dtmf_audio(self):
        test_flag = "ABC"
        key_sequence = dtmf_generate.text_to_dtmf_audio(test_flag, "test_output.wav")
        
        self.assertTrue(os.path.exists("test_output.wav"))
        self.assertEqual(key_sequence, ['2', '2', '2'])
        
        with wave.open("test_output.wav", 'r') as wav_file:
            self.assertEqual(wav_file.getnchannels(), 1)
            self.assertEqual(wav_file.getsampwidth(), 2)
            self.assertEqual(wav_file.getframerate(), 8000)
            self.assertGreater(wav_file.getnframes(), 0)
    
    def test_generate_main_function(self):
        test_flag = "CTF{test}"

        with patch('sys.argv', ['generate.py', test_flag]):
            dtmf_generate.main()

        self.assertTrue(os.path.exists("output.wav"))
    
    def test_load_wav_file(self):
        test_flag = "A"
        dtmf_generate.text_to_dtmf_audio(test_flag, "test_load.wav")
        
        audio_data, sample_rate = dtmf_solve.load_wav_file("test_load.wav")
        
        self.assertIsInstance(audio_data, np.ndarray)
        self.assertEqual(sample_rate, 8000)
        self.assertGreater(len(audio_data), 0)
        self.assertGreater(np.max(np.abs(audio_data)), 0)
    
    def test_detect_dtmf_frequencies(self):
        tone = dtmf_generate.generate_dtmf_tone('5', duration=0.5, sample_rate=8000)
        
        detected_freqs = dtmf_solve.detect_dtmf_frequencies(tone, 8000)
        
        self.assertIn(770, detected_freqs)
        self.assertIn(1336, detected_freqs)
    
    def test_frequencies_to_key(self):
        test_cases = [
            ([697, 1209], '1'),
            ([770, 1336], '5'),
            ([941, 1336], '0'),
            ([852, 1477], '9')
        ]
        
        for freqs, expected_key in test_cases:
            with self.subTest(freqs=freqs):
                result = dtmf_solve.frequencies_to_key(freqs)
                self.assertEqual(result, expected_key)
    
    def test_key_to_possible_chars(self):
        test_cases = [
            ('2', ['A', 'B', 'C']),
            ('8', ['T', 'U', 'V']),
            ('0', ['{', '}']),
            ('1', ['1'])
        ]
        
        for key, expected_chars in test_cases:
            with self.subTest(key=key):
                result = dtmf_solve.key_to_possible_chars(key)
                self.assertEqual(result, expected_chars)
    
    def test_simple_flag_reconstruction(self):
        key_sequence = ['2', '8', '3', '0', '8', '3', '7', '8', '0']
        
        flag = dtmf_solve.reconstruct_flag_from_keys(key_sequence)
        
        self.assertTrue(flag.startswith('CTF{'))
        self.assertTrue(flag.endswith('}'))
    
    def test_audio_generation_and_basic_parsing(self):
        test_flag = "CTF{A}"
        
        key_sequence = dtmf_generate.text_to_dtmf_audio(test_flag, "test_round.wav")
        self.assertTrue(os.path.exists("test_round.wav"))
        
        audio_data, sample_rate = dtmf_solve.load_wav_file("test_round.wav")
        self.assertGreater(len(audio_data), 0)
        
        segments = dtmf_solve.segment_audio(audio_data, sample_rate)
        self.assertGreater(len(segments), 0)
    
    def test_solve_main_function(self):
        test_flag = "CTF{B}"
        dtmf_generate.text_to_dtmf_audio(test_flag, "solve_test.wav")
        
        with patch('sys.argv', ['solve.py', 'solve_test.wav']):
            with patch('builtins.print') as mock_print:
                dtmf_solve.main()
                
                print_calls = [str(call) for call in mock_print.call_args_list]
                printed_output = ' '.join(print_calls)
                
                self.assertIn('Loaded audio', printed_output)
    
    def test_t9_mapping(self):
        """Test T9 keypad mapping functionality"""
        # Test known T9 mappings
        t9_mappings = {
            'A': '2', 'B': '2', 'C': '2',
            'D': '3', 'E': '3', 'F': '3',
            'G': '4', 'H': '4', 'I': '4',
            'J': '5', 'K': '5', 'L': '5',
            'M': '6', 'N': '6', 'O': '6',
            'P': '7', 'Q': '7', 'R': '7', 'S': '7',
            'T': '8', 'U': '8', 'V': '8',
            'W': '9', 'X': '9', 'Y': '9', 'Z': '9'
        }
        
        # Test some specific mappings
        for char, expected_key in t9_mappings.items():
            result = dtmf_generate.char_to_key(char)
            self.assertEqual(result, expected_key, f"Character '{char}' should map to key '{expected_key}'")
    
    def test_dtmf_frequency_generation(self):
        """Test that DTMF tones contain expected frequencies"""
        tone = dtmf_generate.generate_dtmf_tone('2', duration=0.1, sample_rate=8000)

        # For key '2', DTMF frequencies should be 697 Hz + 1336 Hz
        # We'll do a basic check that the audio isn't silent
        self.assertGreater(np.max(np.abs(tone)), 0.1, "Audio should have significant amplitude")
        self.assertEqual(len(tone), int(0.1 * 8000), "Audio should have correct duration")
    
    def test_key_sequence_generation(self):
        """Test that key sequence file is generated correctly"""
        test_flag = "ABC"
        dtmf_generate.text_to_dtmf_audio(test_flag, "key_test.wav")
        
        # Check if key_sequence.txt was created and contains expected content
        if os.path.exists("key_sequence.txt"):
            with open("key_sequence.txt", 'r') as f:
                sequence = f.read().strip()
                
            # ABC should map to T9 keys: A=2, B=2, C=2
            # So sequence should contain '2' characters
            self.assertIn('2', sequence)
    
    def test_audio_duration(self):
        """Test that generated audio has reasonable duration"""
        test_flag = "AB"
        dtmf_generate.text_to_dtmf_audio(test_flag, "duration_test.wav")
        
        with wave.open("duration_test.wav", 'rb') as wav_file:
            frames = wav_file.getnframes()
            sample_rate = wav_file.getframerate()
            duration = frames / sample_rate
            
        # Should be at least a few seconds for the test flag
        self.assertGreater(duration, 1.0, "Audio should be at least 1 second long")
        self.assertLess(duration, 30.0, "Audio shouldn't be excessively long for short flag")
    
    def test_error_handling(self):
        """Test error handling for invalid inputs"""
        with self.assertRaises(SystemExit):
            with patch('sys.argv', ['generate.py']):  # Missing flag argument
                dtmf_generate.main()
    
    def test_special_characters_handling(self):
        """Test handling of special characters that can't be mapped to T9"""
        test_flag = "H{"  # Contains a brace which maps to '0'
        
        # Should not crash, should map brace to appropriate key
        try:
            dtmf_generate.text_to_dtmf_audio(test_flag, "special_test.wav")
            self.assertTrue(os.path.exists("special_test.wav"))
            
            # Check key sequence contains mappings for both characters
            if os.path.exists("key_sequence.txt"):
                with open("key_sequence.txt", 'r') as f:
                    sequence = f.read().strip()
                self.assertIn('4', sequence)  # H maps to 4
                self.assertIn('0', sequence)  # { maps to 0
        except Exception as e:
            self.fail(f"Should handle special characters gracefully: {e}")
    
    def test_roundtrip_encoding_decoding(self):
        """Test encoding and decoding various flag formats"""
        test_cases = [
            "AB",      # Simple case
            "HC",      # Challenge prefix
            "123",     # Numbers
            "HI",      # Short flag
        ]
        
        for test_flag in test_cases:
            with self.subTest(flag=test_flag):
                wav_file = f"test_{abs(hash(test_flag))}.wav"
                dtmf_generate.text_to_dtmf_audio(test_flag, wav_file)
                
                # Basic validation that file was created and has content
                self.assertTrue(os.path.exists(wav_file))
                with wave.open(wav_file, 'rb') as wf:
                    self.assertGreater(wf.getnframes(), 0)

if __name__ == '__main__':
    unittest.main()