from __future__ import division

import functools
import hashlib
import io
import math
import string
import warnings

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
        assert isinstance(other, int) or isinstance(other, float)
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
        return math.floor(self.mean)

    def rounded_mean(self, places=2):
        return round(self.mean, places)


def choose(n, k):
    return math.factorial(n) / (math.factorial(k) * math.factorial(n - k))


# From: http://stackoverflow.com/a/2267446/4441526
digs = string.digits + string.ascii_lowercase


def int2base(x, base):
    """This function converts an int to a str using a specific base.

    Note: This function was created to support weird bases that don't already have a builtin method. So if you want to
          convert ints to base 2, 8, 16 it is better to use bin, oct, hex method respectively.
    """
    if len(digs) < base or base < 2:
        raise ValueError(f"int2base only supports bases between {2} and {len(digs)}")
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
        digits.append("-")

    digits.reverse()

    return "".join(digits)


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
            warnings.simplefilter("always", DeprecationWarning)  # turn off filter
            warnings.warn(
                "{} is a deprecated function. {}".format(func.__name__, message),
                category=DeprecationWarning,
                stacklevel=2,
            )
            warnings.simplefilter("default", DeprecationWarning)  # reset filter
            return func(*args, **kwargs)

        return new_func

    return deprecated_decorator


def hash_string(s, encoding="utf8"):
    buf = io.BytesIO()
    buf.write(bytes(s, encoding=encoding))
    buf.seek(0)
    return hash_stream(buf)


def hash_stream(fp):
    BUF_SIZE = 65536
    sha = hashlib.sha256()
    while True:
        data = fp.read(BUF_SIZE)
        if not data:
            break
        sha.update(data)
    return sha.hexdigest()
