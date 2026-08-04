import unittest

from volter_nato_steg import (
    SteganographyError,
    decrypt_from_nato,
    encode_operator_message,
    encrypt_to_nato,
    decode_operator_message,
)


class TestVolterNatoSteg(unittest.TestCase):
    def test_encrypt_decrypt_roundtrip(self):
        secret = b"Military key material: AES-256 key"
        passphrase = "correct horse battery staple"
        encoded = encrypt_to_nato(secret, passphrase)
        decoded = decrypt_from_nato(encoded, passphrase)
        self.assertEqual(decoded, secret)

    def test_wrong_passphrase_fails(self):
        secret = b"Confidential data"
        encoded = encrypt_to_nato(secret, "strong-passphrase")
        with self.assertRaises(SteganographyError):
            decrypt_from_nato(encoded, "wrong-passphrase")

    def test_nato_encoding_rejects_invalid_code_words(self):
        with self.assertRaises(SteganographyError):
            decrypt_from_nato("Alpha Bravo Charlie", "passphrase")

    def test_operator_message_roundtrip(self):
        message = "neutral assessment of civic stability"
        encoded = encode_operator_message(message, "correct horse battery staple")
        decoded = decode_operator_message(encoded, "correct horse battery staple")
        self.assertEqual(decoded, message)


if __name__ == "__main__":
    unittest.main()
