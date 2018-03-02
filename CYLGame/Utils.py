from __future__ import division

import string

from Crypto.Cipher import AES


class OnlineMean:
    def __init__(self, i=0, mean=0):
        self.i = i
        self.mean = mean

    def __add__(self, other):
        new_obj = OnlineMean(self.i, self.mean)
        new_obj.add(other)
        return new_obj

    def add(self, n):
        n = float(n)
        if self.i == 0:
            self.mean = n
        else:
            self.mean = ((self.mean * self.i) / (self.i + 1)) + (n / (self.i + 1))
        self.i += 1
        return self.mean

    @property
    def floored_mean(self):
        return int(self.mean)


# From: http://stackoverflow.com/a/2267446/4441526
digs = string.digits + string.ascii_letters
def int2base(x, base):
    if x < 0:
        sign = -1
    elif x == 0:
        return digs[0]
    else:
        sign = 1

    x *= sign
    digits = []

    while x:
        digits.append(digs[x % base])
        x //= base

    if sign < 0:
        digits.append('-')

    digits.reverse()

    return ''.join(digits)


def encrypt_token_list(tokens, key):
    cipher = AES.new(key, AES.MODE_ECB)
    out = []
    for token in tokens:
        padded_token = "!" * -(len(token) % -len(key)) + token
        out += [cipher.encrypt(bytes(padded_token, encoding="utf-8")).hex()]
    return out


def decrypt_token_list(tokens, key):
    cipher = AES.new(key, AES.MODE_ECB)
    out = []
    for token in tokens:
        plain_token = cipher.decrypt(bytes.fromhex(token))
        out += [plain_token.decode(encoding="utf-8").lstrip("!")]
    return out
