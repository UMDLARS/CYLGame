from __future__ import division

import string
import warnings
import functools

from Crypto.Cipher import AES


class OnlineMean:
    def __init__(self, i=0, mean=0, roll_after_n=-1):
        """

        Args:
            i:              The current number of numbers in the mean
            mean:           The current mean
            roll_after_n:   The number of numbers which to start "rolling the mean after"
        """
        self.i = i
        self.mean = mean
        self.roll_after = roll_after_n

    def __add__(self, other):
        assert isinstance(other, int)
        new_obj = OnlineMean(self.i, self.mean, self.roll_after)
        new_obj.add(other)
        return new_obj

    def add(self, n):
        n = float(n)
        if self.i == 0:
            self.mean = n
            self.i += 1
        else:
            if self.roll_after != -1 and self.i >= self.roll_after:
                # Roll After is enabled and we are past it.
                self.i = self.roll_after - 1
            self.mean = ((self.mean * self.i) / (self.i + 1)) + (n / (self.i + 1))
            self.i += 1
        return self.mean

    @property
    def floored_mean(self):
        return int(self.mean)

    @property
    def rounded_mean(self, places=2):
        return int(self.mean * 10**places) / (10**places)


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


# Taken from: https://stackoverflow.com/questions/2536307/how-do-i-deprecate-python-functions
def deprecated(message=""):
    def deprecated_decorator(func):
        """This is a decorator which can be used to mark functions
        as deprecated. It will result in a warning being emitted
        when the function is used."""
        @functools.wraps(func)
        def new_func(*args, **kwargs):
            warnings.simplefilter('always', DeprecationWarning)  # turn off filter
            warnings.warn("{} is a deprecated function. {}".format(func.__name__, message),
                          category=DeprecationWarning,
                          stacklevel=2)
            warnings.simplefilter('default', DeprecationWarning)  # reset filter
            return func(*args, **kwargs)
        return new_func
    return deprecated_decorator