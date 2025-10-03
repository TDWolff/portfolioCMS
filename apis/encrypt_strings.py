import hashlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from dotenv import load_dotenv
import os

if not load_dotenv():
    raise EnvironmentError("Failed to load .env file")

def multi_pass_encrypt(input_string):
    sha256_result = hashlib.sha256(input_string.encode('utf-8')).hexdigest()
    fixed_key = os.getenv("FIXED_KEY")
    sha256_bytes = sha256_result.encode('utf-8')
    padding_length = 8 - (len(sha256_bytes) % 8)
    if padding_length != 8:
        sha256_bytes += b'\x00' * padding_length
    cipher = Cipher(algorithms.Blowfish(fixed_key), modes.ECB(), backend=default_backend())
    encryptor = cipher.encryptor()
    blowfish_result = encryptor.update(sha256_bytes) + encryptor.finalize()
    blowfish_hex = blowfish_result.hex()
    caesar_shift = 13
    result = ""
    for char in blowfish_hex:
        if char.isalpha():
            if char.islower():
                result += chr((ord(char) - ord('a') + caesar_shift) % 26 + ord('a'))
            else:
                result += chr((ord(char) - ord('A') + caesar_shift) % 26 + ord('A'))
        elif char.isdigit():
            result += str((int(char) + caesar_shift) % 10)
        else:
            result += char
    
    return result