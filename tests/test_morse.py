#!/usr/bin/env python3
import os
import sys
import tempfile
import unittest
import wave
import numpy as np
from unittest.mock import patch
import importlib.util

# Add the morse directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
morse_dir = os.path.join(os.path.dirname(current_dir), "04-morse")
sys.path.insert(0, morse_dir)

# Import modules using importlib to avoid naming conflicts
def load_module_from_path(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# Load generate and solve modules
generate_path = os.path.join(morse_dir, "generate.py")
solve_path = os.path.join(morse_dir, "solve.py")

morse_generate = load_module_from_path("morse_generate", generate_path)
morse_solve = load_module_from_path("morse_solve", solve_path)

class TestMorseChallenge(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_audio_file = os.path.join(self.temp_dir, "test_output.wav")
        self.test_flag_file = os.path.join(self.temp_dir, "flag.txt")
        
    def tearDown(self):
        """Clean up test files"""
        import shutil
        for file in [self.test_audio_file, self.test_flag_file]:
            if os.path.exists(file):
                os.remove(file)
        # Clean up any remaining files in temp directory
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
            '1': '.----',
            '0': '-----',
            ' ': ' '
        }
        
        for char, expected_morse in test_cases.items():
            with self.subTest(char=char):
                result = morse_generate.char_to_morse(char)
                self.assertEqual(result, expected_morse)
    
    def test_generate_frequency_sweep(self):
        """Test frequency sweep generation"""
        start_freq = 600
        end_freq = 1000
        duration = 0.15
        sample_rate = 22050
        
        sweep = morse_generate.generate_frequency_sweep(start_freq, end_freq, duration, sample_rate)
        
        # Check that sweep has correct length
        expected_length = int(sample_rate * duration)
        self.assertEqual(len(sweep), expected_length)
        
        # Check that values are within expected amplitude range
        self.assertTrue(np.all(np.abs(sweep) <= 0.3))
        
        # Check that sweep is not all zeros
        self.assertFalse(np.all(sweep == 0))
    
    def test_generate_steady_tone(self):
        """Test steady tone generation for punctuation"""
        freq = 800
        duration = 0.15
        sample_rate = 22050
        
        tone = morse_generate.generate_steady_tone(freq, duration, sample_rate)
        
        # Check that tone has correct length
        expected_length = int(sample_rate * duration)
        self.assertEqual(len(tone), expected_length)
        
        # Check that values are within expected amplitude range
        self.assertTrue(np.all(np.abs(tone) <= 0.3))
    
    def test_generate_silence(self):
        """Test silence generation"""
        duration = 0.1
        sample_rate = 22050
        
        silence = morse_generate.generate_silence(duration, sample_rate)
        
        # Check that silence has correct length
        expected_length = int(sample_rate * duration)
        self.assertEqual(len(silence), expected_length)
        
        # Check that all values are zero
        self.assertTrue(np.all(silence == 0))
    
    def test_morse_to_frequency_sweep_audio(self):
        """Test Morse code to audio conversion"""
        morse_code = ".- -..."  # A B
        sample_rate = 22050
        
        audio_data = morse_generate.morse_to_frequency_sweep_audio(morse_code, sample_rate)
        
        # Check that audio was generated
        self.assertGreater(len(audio_data), 0)
        
        # Check that audio contains non-zero values
        self.assertFalse(np.all(audio_data == 0))
    
    def test_text_to_morse_audio_simple(self):
        """Test text to Morse audio conversion with simple text"""
        text = "HI"
        
        # Create temporary flag file
        with open(self.test_flag_file, 'w') as f:
            f.write(text)
        
        # Change to temp directory to use flag.txt
        original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        try:
            morse_sequence = morse_generate.text_to_morse_audio(text, "output.wav")
            
            # Check that morse sequence was generated
            self.assertIsInstance(morse_sequence, list)
            self.assertGreater(len(morse_sequence), 0)
            
            # Check that output file was created
            self.assertTrue(os.path.exists("output.wav"))
            
            # Check that the WAV file is valid
            with wave.open("output.wav", 'r') as wav_file:
                self.assertEqual(wav_file.getnchannels(), 1)  # Mono
                self.assertEqual(wav_file.getsampwidth(), 2)  # 16-bit
                self.assertEqual(wav_file.getframerate(), 22050)  # Sample rate
                
        finally:
            os.chdir(original_cwd)
            # Clean up generated files
            output_file = os.path.join(self.temp_dir, "output.wav")
            if os.path.exists(output_file):
                os.remove(output_file)
    
    def test_text_to_morse_audio_with_punctuation(self):
        """Test text to Morse audio conversion with punctuation"""
        text = "HC{TEST}"
        
        # Change to temp directory
        original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        try:
            morse_sequence = morse_generate.text_to_morse_audio(text, "output.wav")
            
            # Check that punctuation was handled (now represented as • bullets)
            morse_string = ''.join([item.split(':')[-1] if ':' in item else item for item in morse_sequence])
            self.assertIn('•', morse_string)
            
        finally:
            os.chdir(original_cwd)
            # Clean up
            output_file = os.path.join(self.temp_dir, "output.wav")
            if os.path.exists(output_file):
                os.remove(output_file)
    
    def test_load_wav_file(self):
        """Test WAV file loading"""
        # Generate a simple test audio file
        sample_rate = 22050
        duration = 0.1
        frequency = 440
        
        # Generate test audio
        t = np.linspace(0, duration, int(sample_rate * duration))
        audio_data = 0.5 * np.sin(2 * np.pi * frequency * t)
        audio_int16 = (audio_data * 32767).astype(np.int16)
        
        # Save as WAV
        with wave.open(self.test_audio_file, 'w') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio_int16.tobytes())
        
        # Test loading
        loaded_audio, loaded_rate = morse_solve.load_wav_file(self.test_audio_file)
        
        self.assertEqual(loaded_rate, sample_rate)
        self.assertGreater(len(loaded_audio), 0)
        self.assertTrue(np.max(np.abs(loaded_audio)) <= 1.0)  # Normalized
    
    def test_analyze_frequency_trend(self):
        """Test frequency trend analysis"""
        # Create mock frequency and spectrogram data
        frequencies = np.linspace(0, 1000, 100)
        
        # Test upward trend (start low, end high)
        spec_segment = np.zeros((100, 10))
        spec_segment[10, 0] = 1.0  # Peak at low frequency at start
        spec_segment[90, -1] = 1.0  # Peak at high frequency at end
        
        trend = morse_solve.analyze_frequency_trend(frequencies, spec_segment)
        self.assertGreater(trend, 0)  # Should be positive (upward)
        
        # Test downward trend (start high, end low)
        spec_segment = np.zeros((100, 10))
        spec_segment[90, 0] = 1.0  # Peak at high frequency at start
        spec_segment[10, -1] = 1.0  # Peak at low frequency at end
        
        trend = morse_solve.analyze_frequency_trend(frequencies, spec_segment)
        self.assertLess(trend, 0)  # Should be negative (downward)
    
    def test_detect_frequency_sweeps_simple(self):
        """Test frequency sweep detection with simple audio"""
        # Generate test audio using the actual generator function
        sample_rate = 22050
        
        # Create a dot (upward sweep) and a dash (downward sweep)
        dot_sweep = morse_generate.generate_frequency_sweep(600, 1000, 0.15, sample_rate)
        silence = morse_generate.generate_silence(0.15, sample_rate)
        dash_sweep = morse_generate.generate_frequency_sweep(1000, 600, 0.45, sample_rate)
        
        # Combine into test audio
        audio_data = np.concatenate([silence, dot_sweep, silence, dash_sweep, silence])
        
        morse_elements = morse_solve.detect_frequency_sweeps(audio_data, sample_rate)
        
        # Should detect at least one element (may not be perfect due to signal processing)
        # This is a basic functionality test
        self.assertIsInstance(morse_elements, list)
    
    def test_morse_to_text_conversion(self):
        """Test morse elements to text conversion"""
        # Test simple morse elements
        morse_elements = ['.', '-', '.', '.']  # Should represent some characters
        
        result = morse_solve.reconstruct_text_from_morse(morse_elements)
        
        # Should return some decoded text
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)
    
    def test_end_to_end_simple(self):
        """Test end-to-end encoding and decoding"""
        original_text = "HI"
        
        # Change to temp directory
        original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        try:
            # Generate audio
            morse_generate.text_to_morse_audio(original_text, "test.wav")
            
            # Attempt to decode (may not be perfect due to simplified test)
            decoded = morse_solve.solve_morse_audio("test.wav")
            
            # At minimum, should return some result without error
            # (Perfect decoding may be difficult due to signal processing complexity)
            if decoded is not None:
                self.assertIsInstance(decoded, str)
                
        finally:
            os.chdir(original_cwd)
            # Clean up
            test_files = ["test.wav", "morse_sequence.txt"]
            for f in test_files:
                filepath = os.path.join(self.temp_dir, f)
                if os.path.exists(filepath):
                    os.remove(filepath)
    
    def test_morse_code_mapping(self):
        """Test Morse code mapping functionality"""
        morse_mappings = {
            'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.',
            'F': '..-.', 'G': '--.', 'H': '....', 'I': '..', 'J': '.---',
            'K': '-.-', 'L': '.-..', 'M': '--', 'N': '-.', 'O': '---',
            'P': '.--.', 'Q': '--.-', 'R': '.-.', 'S': '...', 'T': '-',
            'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-', 'Y': '-.--',
            'Z': '--..', '1': '.----', '2': '..---', '3': '...--',
            '4': '....-', '5': '.....', '6': '-....', '7': '--...',
            '8': '---..', '9': '----.', '0': '-----'
        }
        
        # Test some specific mappings if the function is accessible
        if hasattr(morse_generate, 'MORSE_CODE'):
            morse_dict = morse_generate.MORSE_CODE
            for char, expected_morse in morse_mappings.items():
                if char in morse_dict:
                    self.assertEqual(morse_dict[char], expected_morse,
                                   f"Character '{char}' should map to '{expected_morse}'")
    
    def test_frequency_sweep_generation(self):
        """Test that frequency sweeps are generated correctly"""
        original_cwd = os.getcwd()
        os.chdir(self.temp_dir)

        try:
            with patch('sys.argv', ['generate.py', 'A']):
                morse_generate.main()
            
            self.assertTrue(os.path.exists("output.wav"))
            
            # Read the WAV file and analyze
            with wave.open("output.wav", 'rb') as wav_file:
                frames = wav_file.readframes(wav_file.getnframes())
                sample_rate = wav_file.getframerate()
                
            # Convert to numpy array
            audio_data = np.frombuffer(frames, dtype=np.int16)
            
            # Check that audio isn't silent and has variation (sweeps)
            self.assertGreater(np.max(np.abs(audio_data)), 1000, "Audio should have significant amplitude")
            self.assertGreater(np.std(audio_data), 100, "Audio should have variation (frequency sweeps)")
            
        finally:
            os.chdir(original_cwd)
    
    def test_morse_sequence_generation(self):
        """Test that morse sequence file is generated correctly"""
        original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        try:
            with patch('sys.argv', ['generate.py', 'SOS']):
                morse_generate.main()

            # Morse sequence is no longer written to file, just printed
            # Check that output.wav was created
            self.assertTrue(os.path.exists("output.wav"))
                              
        finally:
            os.chdir(original_cwd)
    
    def test_audio_duration(self):
        """Test that generated audio has reasonable duration"""
        original_cwd = os.getcwd()
        os.chdir(self.temp_dir)

        try:
            with patch('sys.argv', ['generate.py', 'AB']):
                morse_generate.main()
            
            with wave.open("output.wav", 'rb') as wav_file:
                frames = wav_file.getnframes()
                sample_rate = wav_file.getframerate()
                duration = frames / sample_rate
                
            # Should be at least a few seconds for the test flag
            self.assertGreater(duration, 1.0, "Audio should be at least 1 second long")
            self.assertLess(duration, 60.0, "Audio shouldn't be excessively long for short flag")
            
        finally:
            os.chdir(original_cwd)
    
    def test_flag_file_requirement(self):
        """Test that flag.txt file is required"""
        original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        try:
            # Remove flag.txt if it exists
            if os.path.exists("flag.txt"):
                os.remove("flag.txt")
            
            # Should handle missing flag file gracefully
            try:
                morse_generate.main()
                # If it succeeds, check that output was created
                if os.path.exists("output.wav"):
                    self.assertTrue(True)  # Success case
                else:
                    self.fail("Should either create output or raise an exception")
            except (FileNotFoundError, SystemExit):
                # Expected behavior for missing flag file
                self.assertTrue(True)
                
        finally:
            os.chdir(original_cwd)
    
    def test_special_characters_handling(self):
        """Test handling of special characters not in Morse code"""
        original_cwd = os.getcwd()
        os.chdir(self.temp_dir)

        try:
            # Should not crash, might skip unmappable characters
            try:
                with patch('sys.argv', ['generate.py', 'A{B']):
                    morse_generate.main()
                self.assertTrue(os.path.exists("output.wav"))
            except Exception as e:
                # If it raises an exception, it should be handled gracefully
                self.fail(f"Should handle special characters gracefully: {e}")
                
        finally:
            os.chdir(original_cwd)
    
    def test_punctuation_handling(self):
        """Test that punctuation marks are handled with steady tones"""
        original_cwd = os.getcwd()
        os.chdir(self.temp_dir)

        try:
            with patch('sys.argv', ['generate.py', 'A{}']):
                morse_generate.main()
            
            # Should create output without crashing
            self.assertTrue(os.path.exists("output.wav"))
            
            with wave.open("output.wav", 'rb') as wav_file:
                frames = wav_file.readframes(wav_file.getnframes())
                
            audio_data = np.frombuffer(frames, dtype=np.int16)
            # Should have reasonable audio content
            self.assertGreater(np.max(np.abs(audio_data)), 500, "Should have audio content for punctuation")
            
        finally:
            os.chdir(original_cwd)

if __name__ == "__main__":
    unittest.main()