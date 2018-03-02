import pytest

from CYLGame.Utils import encrypt_token_list, decrypt_token_list


@pytest.mark.parametrize("tokens", [["12345678", "00000000"],
                                    ["8E4A1D8"]])
@pytest.mark.parametrize("key", [b'0123456789012345',
                                 b"=\x18t\xdf'\xff\xc3\xde#\xb8\n\x12j:\x04\x7f"])
def test_encrypt_decrypt_tokens(tokens, key):
    e_tokens = encrypt_token_list(tokens, key)
    for real_token, decrypted_token in zip(tokens, decrypt_token_list(e_tokens, key)):
        assert real_token == decrypted_token
