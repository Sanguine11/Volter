import unittest

from volter_nato_steg import (
    SteganographyError,
    decrypt_from_nato,
    encrypt_to_nato,
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


if __name__ == "__main__":
    unittest.main()
