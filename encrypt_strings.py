import hashlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

def multi_pass_encrypt(input_string):
    """
    Multi-pass encryption: SHA-256 → Blowfish → Caesar Cipher
    Returns encrypted string. Same input always produces same output.
    """
    # PASS 1: SHA-256 hash
    sha256_result = hashlib.sha256(input_string.encode('utf-8')).hexdigest()
    
    # PASS 2: Deterministic Blowfish encryption
    fixed_key = b"MyFixedBlowfishKey123456"  # Fixed key for deterministic results
    sha256_bytes = sha256_result.encode('utf-8')
    
    # Pad to multiple of 8 bytes (Blowfish block size)
    padding_length = 8 - (len(sha256_bytes) % 8)
    if padding_length != 8:
        sha256_bytes += b'\x00' * padding_length
    
    cipher = Cipher(algorithms.Blowfish(fixed_key), modes.ECB(), backend=default_backend())
    encryptor = cipher.encryptor()
    blowfish_result = encryptor.update(sha256_bytes) + encryptor.finalize()
    blowfish_hex = blowfish_result.hex()
    
    # PASS 3: Deterministic Caesar cipher (ROT13-style)
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

def main():
    # Get two strings from user
    print("Multi-Pass String Encryption Tool")
    print("=" * 40)
    print("Encryption process: SHA-256 → Blowfish → Caesar Cipher")
    print()
    
    string1 = input("Enter first string to encrypt: ")
    print("\nProcessing string 1:")
    encrypted1 = multi_pass_encrypt(string1)
    
    print("\n" + "-" * 50)
    
    string2 = input("Enter second string to encrypt: ")
    print("\nProcessing string 2:")
    encrypted2 = multi_pass_encrypt(string2)
    
    # Display final results
    print("\n" + "=" * 60)
    print("FINAL ENCRYPTION RESULTS:")
    print("=" * 60)
    print(f"String 1 - Original: {string1}")
    print(f"String 1 - Final Encrypted: {encrypted1}")
    print()
    print(f"String 2 - Original: {string2}")
    print(f"String 2 - Final Encrypted: {encrypted2}")
    
    # Save to file
    with open("encrypted_strings.txt", "w") as f:
        f.write("Multi-Pass Encrypted Strings\n")
        f.write("=" * 40 + "\n")
        f.write("Encryption Process: SHA-256 → Blowfish → Caesar Cipher\n\n")
        f.write(f"String 1:\n")
        f.write(f"Original: {string1}\n")
        f.write(f"Final Encrypted: {encrypted1}\n\n")
        f.write(f"String 2:\n")
        f.write(f"Original: {string2}\n")
        f.write(f"Final Encrypted: {encrypted2}\n\n")
        f.write("Note: This is multi-pass one-way encryption. Original strings cannot be recovered from encrypted versions.\n")
        f.write("Encryption uses: SHA-256 hash → Blowfish cipher → Caesar cipher\n")
    
    print(f"\nResults saved to 'encrypted_strings.txt'")
    
    # Test that same input produces same output
    print("\nTesting deterministic behavior...")
    test_encrypted1 = multi_pass_encrypt(string1)
    test_encrypted2 = multi_pass_encrypt(string2)
    
    if encrypted1 == test_encrypted1 and encrypted2 == test_encrypted2:
        print("✓ Encryption is deterministic - same inputs produce same outputs")
    else:
        print("✗ Error: Encryption is not deterministic")

if __name__ == "__main__":
    main()
