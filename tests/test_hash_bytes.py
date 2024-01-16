import secrets

from fake_faces_generator.download import hash_bytes


def test_same_input_produces_same_hash():
    input_bytes = secrets.token_bytes(100)
    hash1 = hash_bytes(input_bytes)
    hash2 = hash_bytes(input_bytes)
    assert hash1 == hash2


def test_different_input_produces_different_hash():
    input_bytes1 = secrets.token_bytes(100)
    input_bytes2 = secrets.token_bytes(100)
    hash1 = hash_bytes(input_bytes1)
    hash2 = hash_bytes(input_bytes2)
    assert hash1 != hash2


def test_is_hexdecimal():
    def is_hexdecimal(string):
        try:
            int(string, 16)
            return True
        except ValueError:
            return False

    input_bytes = secrets.token_bytes(100)
    assert is_hexdecimal(hash_bytes(input_bytes)) == True
