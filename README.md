# Volter

Volter is a small demonstration of a NATO-style steganography system for encrypting and hiding cryptographic material within a text-friendly code-word format.

## What this does

- Encrypts arbitrary bytes with a passphrase.
- Encodes the ciphertext as a sequence of NATO phonetic alphabet words.
- Allows the encoded message to be carried as text, while the original data remains recoverable only with the passphrase.

## Files

- `volter_nato_steg.py`: implementation of encryption, decryption, NATO encoding, and decoding.
- `tests/test_volter_nato_steg.py`: basic unit tests for roundtrip encryption and validation.

## Usage

Encrypt text to a NATO-style string:

```bash
python3 volter_nato_steg.py encrypt "my-secret-passphrase" --text "Top secret payload"
```

Decrypt a NATO-style message:

```bash
python3 volter_nato_steg.py decrypt "my-secret-passphrase" "Alpha Bravo ..."
```

## Security notes

- This implementation uses PBKDF2 with SHA-256 and HMAC-SHA256 for authentication.
- The NATO encoding is a visibility layer, not a cryptographic primitive.
- Keep passphrases strong, and never use hidden or covert messaging for unlawful activity.
