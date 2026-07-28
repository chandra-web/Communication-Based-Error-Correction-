# nlp_error_correction.py
# NLP-Powered Smart Error Correction Demo
# Simulates text transmission over a noisy PSK channel and uses NLP to fix bit errors.

import numpy as np
from spellchecker import SpellChecker
import re

def text_to_bits(text):
    """Convert string to list of binary bits."""
    bits = []
    for char in text:
        # Convert each char to 8-bit binary representation
        bin_str = format(ord(char), '08b')
        bits.extend([int(b) for b in bin_str])
    return bits

def bits_to_text(bits):
    """Convert list of binary bits back to string, replacing errors with '?'"""
    # Pad bits if length is not a multiple of 8
    padding = len(bits) % 8
    if padding != 0:
        bits = [0]*(8-padding) + bits
        
    chars = []
    for i in range(0, len(bits), 8):
        byte_val = int(''.join(map(str, bits[i:i+8])), 2)
        try:
            # Only allow standard printable ASCII to prevent terminal garbage
            if 32 <= byte_val <= 126:
                chars.append(chr(byte_val))
            else:
                chars.append('?')
        except ValueError:
            chars.append('?')
    return "".join(chars)

def simulate_psk_channel(bits, snr_db):
    """Simulate BPSK transmission over an AWGN channel."""
    # Convert bits to symbols (0 -> -1.0, 1 -> 1.0)
    symbols = np.where(np.array(bits) == 1, 1.0, -1.0)
    
    # Calculate noise power based on SNR
    snr_linear = 10 ** (snr_db / 10)
    noise_std = 1 / np.sqrt(2 * snr_linear)
    
    # Add AWGN noise
    noise = np.random.normal(0, noise_std, len(symbols))
    received_symbols = symbols + noise
    
    # Demodulate (Threshold > 0)
    received_bits = np.where(received_symbols > 0, 1, 0).tolist()
    
    # Calculate physical Bit Error Rate
    errors = sum(1 for a, b in zip(bits, received_bits) if a != b)
    ber = errors / len(bits)
    
    return received_bits, ber

def nlp_correct_text(garbled_text):
    """Use a simple spellchecker to correct corrupted words based on English language rules."""
    spell = SpellChecker(distance=2)
    
    # Split text by spaces to get words
    words = garbled_text.split(" ")
    corrected_words = []
    
    for word in words:
        # Strip outer punctuation but KEEP internal corrupted characters 
        # so the spellchecker's edit distance algorithm works properly
        clean_word = word.strip(".,!?;:\"'()")
        
        if clean_word:
            # Get correction from NLP dictionary
            correction = spell.correction(clean_word)
            if correction:
                # Naively put it back with punctuation (simple demo approach)
                corrected_word = word.replace(clean_word, correction)
                corrected_words.append(corrected_word)
            else:
                corrected_words.append(word)
        else:
            corrected_words.append(word)
            
    return " ".join(corrected_words)

def main():
    print("=" * 70)
    print(" 🤖 NLP-Powered Smart Error Correction Simulator")
    print("=" * 70)
    
    print("Please enter a text message to transmit (or press Enter for default):")
    user_input = input("> ").strip()
    original_text = user_input if user_input else "The digital modulation simulator uses math to send messages over noisy waves."
    
    print(f"\n[1] Original Text:\n    '{original_text}'")
    
    # Step 1: Text to Binary
    bits = text_to_bits(original_text)
    print(f"\n[2] Converted to Binary: {len(bits)} bits generated.")
    
    # Step 2 & 3: Transmit over Noisy PSK Channel
    print("\n[3] Enter Signal-to-Noise Ratio (SNR) in dB (e.g., 4.5) [Press Enter for default 5.5]:")
    snr_input = input("> ").strip()
    try:
        snr = float(snr_input) if snr_input else 5.5
    except ValueError:
        print("    [!] Invalid SNR. Using default 5.5")
        snr = 5.5
        
    print(f"    Transmitting over BPSK channel at SNR = {snr} dB...")
    received_bits, ber = simulate_psk_channel(bits, snr)
    print(f"    Physical Bit Error Rate (BER): {ber*100:.2f}%")
    
    # Step 4: Demodulate back to text
    corrupted_text = bits_to_text(received_bits)
    print(f"\n[4] Demodulated (Corrupted) Text:\n    '{corrupted_text}'")
    
    # Step 5: NLP Correction
    print("\n[5] Passing to NLP Language Model for Contextual Correction...")
    fixed_text = nlp_correct_text(corrupted_text)
    print(f"    NLP Fixed Text:\n    '{fixed_text}'")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()
