import base64
import hashlib
import hmac
import secrets
import re
from typing import Dict, List

NATO_ALPHABET: List[str] = [
    "Alpha", "Bravo", "Charlie", "Delta", "Echo", "Foxtrot", "Golf", "Hotel",
    "India", "Juliett", "Kilo", "Lima", "Mike", "November", "Oscar", "Papa",
    "Quebec", "Romeo", "Sierra", "Tango", "Uniform", "Victor", "Whiskey", "X-ray",
    "Yankee", "Zulu",
]

NATO_LOOKUP: Dict[str, int] = {word.upper(): index for index, word in enumerate(NATO_ALPHABET)}

PBKDF2_ROUNDS = 200_000
KEY_SIZE = 32
SALT_SIZE = 16
IV_SIZE = 16
TAG_SIZE = 32


class SteganographyError(Exception):
    pass


def derive_key(passphrase: str, salt: bytes) -> bytes:
    if not passphrase:
        raise SteganographyError("Passphrase must not be empty.")
    return hashlib.pbkdf2_hmac("sha256", passphrase.encode("utf-8"), salt, PBKDF2_ROUNDS, dklen=KEY_SIZE)


def hmac_sha256(key: bytes, data: bytes) -> bytes:
    return hmac.new(key, data, hashlib.sha256).digest()


def keystream(key: bytes, iv: bytes, length: int) -> bytes:
    counter = 0
    output = bytearray()
    while len(output) < length:
        block = hmac_sha256(key, iv + counter.to_bytes(8, "big"))
        output.extend(block)
        counter += 1
    return bytes(output[:length])


def xor_bytes(a: bytes, b: bytes) -> bytes:
    return bytes(x ^ y for x, y in zip(a, b))


def encrypt_material(plaintext: bytes, passphrase: str) -> str:
    if not isinstance(plaintext, (bytes, bytearray)):
        raise SteganographyError("Plaintext must be bytes.")

    salt = secrets.token_bytes(SALT_SIZE)
    iv = secrets.token_bytes(IV_SIZE)
    key = derive_key(passphrase, salt)
    stream = keystream(key, iv, len(plaintext))
    ciphertext = xor_bytes(plaintext, stream)
    tag = hmac_sha256(key, salt + iv + ciphertext)
    envelope = salt + iv + ciphertext + tag
    return base64.urlsafe_b64encode(envelope).decode("utf-8")


def decrypt_material(encoded: str, passphrase: str) -> bytes:
    try:
        envelope = base64.urlsafe_b64decode(encoded.encode("utf-8"))
    except (ValueError, TypeError) as exc:
        raise SteganographyError("Input is not valid base64 data.") from exc

    if len(envelope) < SALT_SIZE + IV_SIZE + TAG_SIZE:
        raise SteganographyError("Encrypted data is too short.")

    salt = envelope[:SALT_SIZE]
    iv = envelope[SALT_SIZE:SALT_SIZE + IV_SIZE]
    tag = envelope[-TAG_SIZE:]
    ciphertext = envelope[SALT_SIZE + IV_SIZE:-TAG_SIZE]
    key = derive_key(passphrase, salt)

    expected = hmac_sha256(key, salt + iv + ciphertext)
    if not hmac.compare_digest(expected, tag):
        raise SteganographyError("Authentication failed. Wrong passphrase or corrupted data.")

    stream = keystream(key, iv, len(ciphertext))
    return xor_bytes(ciphertext, stream)


def bytes_to_nato(data: bytes) -> str:
    words = []
    for value in data:
        high = value // len(NATO_ALPHABET)
        low = value % len(NATO_ALPHABET)
        words.append(NATO_ALPHABET[high])
        words.append(NATO_ALPHABET[low])
    return " ".join(words)


def nato_to_bytes(nato_text: str) -> bytes:
    tokens = re.findall(r"[A-Za-z-]+", nato_text)
    if len(tokens) % 2 != 0:
        raise SteganographyError("NATO message must contain an even number of code words.")

    output = bytearray()
    for high_token, low_token in zip(tokens[0::2], tokens[1::2]):
        high = NATO_LOOKUP.get(high_token.upper())
        low = NATO_LOOKUP.get(low_token.upper())
        if high is None or low is None:
            raise SteganographyError(f"Invalid NATO code word: {high_token} or {low_token}")
        value = high * len(NATO_ALPHABET) + low
        if value > 0xFF:
            raise SteganographyError("Decoded byte value is out of range.")
        output.append(value)
    return bytes(output)


def encrypt_to_nato(plaintext: bytes, passphrase: str) -> str:
    encrypted = encrypt_material(plaintext, passphrase)
    encoded_bytes = encrypted.encode("utf-8")
    return bytes_to_nato(encoded_bytes)


def decrypt_from_nato(nato_text: str, passphrase: str) -> bytes:
    encoded_bytes = nato_to_bytes(nato_text)
    encrypted = encoded_bytes.decode("utf-8")
    return decrypt_material(encrypted, passphrase)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Encrypt and decode data using a NATO code-word steganography format.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    encrypt_parser = subparsers.add_parser("encrypt", help="Encrypt a file or text and output a NATO-style code-word string.")
    encrypt_parser.add_argument("passphrase", help="Passphrase for encryption.")
    encrypt_parser.add_argument("--text", help="Text to encrypt.")
    encrypt_parser.add_argument("--infile", help="Path to a file to encrypt.")

    decrypt_parser = subparsers.add_parser("decrypt", help="Decrypt a NATO-style code-word string back into original text.")
    decrypt_parser.add_argument("passphrase", help="Passphrase for decryption.")
    decrypt_parser.add_argument("nato", help="NATO-style encoded message.")

    args = parser.parse_args()
    if args.command == "encrypt":
        if args.text is None and args.infile is None:
            parser.error("Either --text or --infile must be provided.")
        data = args.text.encode("utf-8") if args.text is not None else open(args.infile, "rb").read()
        print(encrypt_to_nato(data, args.passphrase))
    else:
        plaintext = decrypt_from_nato(args.nato, args.passphrase)
        print(plaintext.decode("utf-8", errors="replace"))
