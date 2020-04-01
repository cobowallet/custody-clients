#!/usr/bin/python3
# -*- coding: utf-8 -*-
# import _4quila
import secrets
from pycoin.encoding import public_pair_to_sec, to_bytes_32
from binascii import b2a_hex
from pycoin.key import Key


def generate_new_key():
    secret = secrets.randbits(256)
    secret_hex = b2a_hex(to_bytes_32(secret)).decode()
    key = Key(secret_exponent=secret)
    sec = public_pair_to_sec(key.public_pair())
    return b2a_hex(sec).decode(), secret_hex


if __name__ == "__main__":
    _key, _secret = generate_new_key()
    print("API_KEY: %s" % _key)
    print("API_SECRET: %s" % _secret)
