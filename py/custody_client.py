import functools
import hashlib
import hmac
import json
import random
import time
from binascii import b2a_hex, a2b_hex
from cmd import Cmd

try:
    from urllib.parse import urlencode
except Exception:
    from urllib import urlencode

from pycoin.key import Key

from pycoin.encoding import from_bytes_32

import requests

COBO_PUB = '032f45930f652d72e0c90f71869dfe9af7d713b1f67dc2f7cb51f9572778b9c876'


def double_hash256(content):
    return hashlib.sha256(
        hashlib.sha256(content.encode()).digest()).digest()


def verify(content, signature, pub_key):
    key = Key.from_sec(a2b_hex(pub_key))
    return key.verify(double_hash256(content),
                      a2b_hex(signature))


def generate_ecc_signature(content, key):
    key = Key(secret_exponent=from_bytes_32(a2b_hex(key)))
    return b2a_hex(
        key.sign(double_hash256(content))
    ).decode()


def generate_hmac_signature(content, key):
    return hmac.new(key.encode(), content.encode(),
                    hashlib.sha256).hexdigest()


def sort_params(params):
    params = [(key, val) for key, val in params.items()]

    params.sort(key=lambda x: x[0])
    return urlencode(params)


def verify_response(response):
    content = response.content.decode()
    success = True
    try:
        timestamp = response.headers['BIZ_TIMESTAMP']
        signature = response.headers['BIZ_RESP_SIGNATURE']
        success = verify('%s|%s' % (content, timestamp), signature, COBO_PUB)
    except KeyError:
        pass

    return success, json.loads(content)


def request(method, path, params, api_key, api_secret,
            host="https://api.cobo.com", sign_type='hmac'):
    method = method.upper()
    nonce = str(int(time.time() * 1000))
    content = '%s|%s|%s|%s' % (method,
                               path, nonce, sort_params(params))
    if sign_type == 'hmac':
        sign = generate_hmac_signature(content, api_secret)
    else:
        sign = generate_ecc_signature(content, api_secret)

    headers = {
        'Biz-Api-Key': api_key,
        'Biz-Api-Nonce': nonce,
        'Biz-Api-Signature': sign
    }
    if method == 'GET':
        resp = requests.get('%s%s' % (host, path), params=urlencode(params),
                            headers=headers)
    elif method == 'POST':
        resp = requests.post('%s%s' % (host, path), data=params,
                             headers=headers)
    else:
        raise Exception("Not support http method")
    verify_success, result = verify_response(resp)
    if not verify_success:
        raise Exception(
            'Fatal: verify content error, maybe encounter mid man attack')
    return result


get = functools.partial(request, 'GET')
post = functools.partial(request, 'POST')


class Client(Cmd):
    prompt = 'Custody> '
    intro = 'Welcome to the Cobo Custody shell. Type help or ? to list commands. \n'

    def __init__(self,
                 api_key=None,
                 api_secret=None,
                 host="https://api.sandbox.cobo.com",
                 sign_type="hmac"):
        super(Client, self).__init__()
        assert api_key
        assert api_secret
        assert sign_type in ('hmac', 'ecdsa')
        self.key = api_key
        self.secret = api_secret
        self.host = host
        self.sign_type = sign_type

    def _request(self, method, url, data):
        res = method(url, data, self.key, self.secret, self.host,
                     self.sign_type)
        print(json.dumps(res, indent=4))

    def do_info(self, line):
        '\n\tget org info\n\texample: \033[91minfo\033[0m\n'
        return self._request(get, '/v1/custody/org_info/', {})

    def do_new_address(self, coin):
        '\n\tget new address if coin, format: \033[93m[coin]\033[0m \n\texample: \033[91mnew_address LONT_ONT\033[0m\n'
        coin = coin.strip()
        return self._request(post, "/v1/custody/new_address/", {"coin": coin})

    def do_history(self, line):
        '\n\tget transaction history, format: \033[93m[coin] [side=(w/d)] [limit?=5]\033[0m \n\texample: \033[91mhistory LONT_ONT deposit 2\033[0m\n'
        info = line.split()
        if len(info) not in (2, 3):
            print("format: [coin] [side] [limit?=5]")
            return
        if len(info) == 2:
            coin, side = info
            limit = 5
        else:
            coin, side, limit = info
        if side == 'w':
            side = 'withdraw'
        elif side == 'd':
            side = 'deposit'
        data = {
            'coin': coin,
            'side': side,
            'limit': limit
        }
        return self._request(get, '/v1/custody/transaction_history/', data)

    def do_transaction(self, unique_id):
        '\n\tget transaction by id, format: \033[93m[id]\033[0m\n'
        unique_id = unique_id.strip()
        return self._request(get, '/v1/custody/transaction/',
                             {"id": unique_id})

    def do_withdraw(self, line):
        '\n\twithdraw a coin, format: \033[93m[coin] [address] [amount]\033[0m \n\texample: \033[91mwithdraw LONT_ONT ASUACHaNnL4Q8UZ5tg1jFNBs1yzM3dFgrp 5\033[0m\n'
        info = line.split()
        if len(info) != 3:
            print("format: [coin] [address] [amount]")
            return
        coin, address, amount = info
        request_id = 'tool_%s%s' % (
            int(time.time()), random.randint(0, 1000))
        data = {
            "request_id": request_id,
            "coin": coin,
            "address": address,
            "amount": amount
        }
        return self._request(post, '/v1/custody/new_withdraw_request/', data)

    def do_query_withdraw(self, request_id):
        '\n\twithdraw a coin, format: \033[93m[request_id]\033[0m \n\texample: \033[91mquery_withdraw tool_154458886571\033[0m\n'
        request_id = request_id.strip()
        return self._request(get, '/v1/custody/withdraw_info_by_request_id/',
                             {'request_id': request_id})

    def do_get_test_coin(self, line):
        '\n\tget test coin, format: \033[93m[coin] [address] [amount]\033[0m \n\texample: \033[91mget_test_coin LONT_ONT AZJ1tsVtzHB2LDGtj7xiEbAovBZg58NXss 8\033[0m\n'
        info = line.split()
        if len(info) not in (3,):
            print("format: [coin] [address] [amount]")
            return
        coin, addr, amount = info

        return self._request(post, '/v1/custody/faucet_test_coin/',
                             {'coin': coin, 'address': addr, 'amount': amount})


if __name__ == '__main__':
    # Replace by your own keys
    client = Client(
        api_key="x",
        api_secret="x",
        host="https://api.sandbox.cobo.com",
        sign_type="hmac"
    )

    client.cmdloop()
