import functools
import hashlib
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

API_KEY = "x"
API_SECRET = "x"
HOST = "https://api.sandbox.cobo.com"
COBO_PUB = "032f45930f652d72e0c90f71869dfe9af7d713b1f67dc2f7cb51f9572778b9c876"

def double_hash256(content):
    return hashlib.sha256(hashlib.sha256(content.encode()).digest()).digest()


def verify(content, signature, pub_key):
    key = Key.from_sec(a2b_hex(pub_key))
    return key.verify(double_hash256(content), a2b_hex(signature))

def generate_ecc_signature(content, key):
    key = Key(secret_exponent=from_bytes_32(a2b_hex(key)))
    return b2a_hex(key.sign(double_hash256(content))).decode()


def sort_params(params):
    params = [(key, val) for key, val in params.items()]

    params.sort(key=lambda x: x[0])
    return urlencode(params)


def verify_response(response):
    content = response.content.decode()
    success = True
    try:
        timestamp = response.headers["BIZ_TIMESTAMP"]
        signature = response.headers["BIZ_RESP_SIGNATURE"]
        success = verify("%s|%s" % (content, timestamp), signature, COBO_PUB)
    except KeyError:
        pass
    return success, json.loads(content)


def request(
    method,
    path,
    params,
    api_key,
    api_secret,
):
    method = method.upper()
    nonce = str(int(time.time() * 1000))
    content = "%s|%s|%s|%s" % (method, path, nonce, sort_params(params))
    sign = generate_ecc_signature(content, api_secret)

    headers = {
        "Biz-Api-Key": api_key,
        "Biz-Api-Nonce": nonce,
        "Biz-Api-Signature": sign,
    }
    if method == "GET":
        resp = requests.get(
            "%s%s" % (HOST, path), params=urlencode(params), headers=headers
        )
    elif method == "POST":
        resp = requests.post("%s%s" % (HOST, path), data=params, headers=headers)
    else:
        raise Exception("Not support http method")
    verify_success, result = verify_response(resp)
    if not verify_success:
        raise Exception("Fatal: verify content error, maybe encounter mid man attack")
    return result


get = functools.partial(request, "GET")
post = functools.partial(request, "POST")


class Client(Cmd):
    prompt = "Custody> "
    intro = "Welcome to the Cobo Custody shell. Type help or ? to list commands. \n"

    def __init__(
        self,
        api_key=None,
        api_secret=None,
    ):
        super(Client, self).__init__()
        assert api_key
        assert api_secret
        self.key = api_key
        self.secret = api_secret

    def _request(self, method, url, data):
        res = method(url, data, self.key, self.secret)
        print(json.dumps(res, indent=4))

    def do_info(self, line):
        ("\n\tget org info\n\t" "example: \033[91minfo\033[0m\n")
        return self._request(get, "/v1/custody/org_info/", {})

    def do_coin_info(self, line):
        ("\n\tget org coin info\n\t" "example: \033[91mcoin_info [coin]\033[0m\n")
        coin = line.strip()
        return self._request(get, "/v1/custody/coin_info/", {"coin": coin})

    def do_new_address(self, coin):
        (
            "\n\tget new address of coin, format: \033[93m[coin]\033[0m "
            "\n\texample: \033[91mnew_address LONT_ONT\033[0m\n"
        )
        coin = coin.strip()
        return self._request(post, "/v1/custody/new_address/", {"coin": coin})

    def do_query_address(self, line):
        (
            "\n\tquery address of coin, format: \033[93m[coin] [address]\033[0m "
            "\n\texample: \033[91mquery_address LONT_ONT ADDRESS\033[0m\n"
        )
        if len(line.split()) != 2:
            print("format: [coin] [address]")
            return
        coin, address = line.split()
        return self._request(
            get, "/v1/custody/address_info/", {"coin": coin, "address": address}
        )

    def do_query_internal_address(self, line):
        (
            "\n\tquery internal address of coin, format: \033[93m[coin] [address] [memo]\033[0m "
            "\n\texample: \033[91mquery_internal_address LONT_ONT ADDRESS\033[0m\n"
        )
        if len(line.split()) not in [2, 3]:
            print("format: [coin] [address] [memo]")
            return
        if len(line.split()) == 2:
            coin, address = line.split()
            memo = ""
        if len(line.split()) == 3:
            coin, address, memo = line.split()
        return self._request(
            get,
            "/v1/custody/internal_address_info/",
            {"coin": coin, "address": address, "memo": memo},
        )

    def do_query_internal_addresses(self, line):
        (
            "\n\tquery internal addresses of coin, format: \033[93m[coin] [addresses]\033[0m "
            "\n\texample: \033[91mquery_internal_addresses LONT_ONT ADDRESS,ADDRESS|CCCCC\033[0m\n"
        )
        if len(line.split()) != 2:
            print("format: [coin] [addresses]")
            return
        coin, addresses = line.split()
        return self._request(
            get,
            "/v1/custody/internal_address_info_batch/",
            {"coin": coin, "address": addresses},
        )

    def do_check_address(self, line):
        (
            "\n\tquery address if coin, format: \033[93m[coin] [address]\033[0m "
            "\n\texample: \033[91mquery_address LONT_ONT ADDRESS\033[0m\n"
        )
        if len(line.split()) != 2:
            print("format: [coin] [address]")
            return
        coin, address = line.split()
        return self._request(
            get, "/v1/custody/is_valid_address/", {"coin": coin, "address": address}
        )

    def do_address_history(self, line):
        (
            "\n\tlist address of coin, format: \033[93m[coin]\033[0m "
            "\n\texample: \033[91maddress_history LONT_ONT\033[0m\n"
        )
        coin = line.strip()
        return self._request(get, "/v1/custody/address_history/", {"coin": coin})

    def do_history(self, line):
        (
            "\n\tget transaction history, "
            "format: \033[93m[coin] [side=(w/d)] [limit?=5]\033[0m "
            "\n\texample: \033[91mhistory LONT_ONT deposit 2\033[0m\n"
        )
        info = line.split()
        key = ""
        if len(info) not in (2, 3, 4, 5):
            print("format: [coin] [side] [limit?=5] [max|min=111] [need_fee_detail]")
            return
        if len(info) == 2:
            coin, side = info
            limit = 5
            need_fee_detail = ""
        elif len(info) == 3:
            coin, side, limit = info
            need_fee_detail = ""
        else:
            coin, side, limit = info[:3]
            key, key_id = info[3].split("=")
            key = key + "_id"
            need_fee_detail = "1" if len(info) == 5 else ""
        if side == "w":
            side = "withdraw"
        elif side == "d":
            side = "deposit"
        data = {
            "coin": coin,
            "side": side,
            "limit": limit,
            "need_fee_detail": need_fee_detail,
        }
        if key:
            data[key] = key_id
        return self._request(get, "/v1/custody/transaction_history/", data)

    def do_pending(self, line):
        (
            "\n\tget pending transaction, "
            "format: \033[93m[coin] [side=(w/d)] [limit?=5]\033[0m "
            "\n\texample: \033[91mhistory LONT_ONT deposit 2\033[0m\n"
        )
        info = line.split()
        key = ""
        if len(info) not in (2, 3, 4):
            print("format: [coin] [side] [limit?=5] [max|min=111]")
            return
        if len(info) == 2:
            coin, side = info
            limit = 5
        elif len(info) == 3:
            coin, side, limit = info
        else:
            coin, side, limit = info[:3]
            key, key_id = info[3].split("=")
            key = key + "_id"
        if side == "w":
            side = "withdraw"
        elif side == "d":
            side = "deposit"
        data = {"coin": coin, "side": side, "limit": limit}
        if key:
            data[key] = key_id
        return self._request(get, "/v1/custody/pending_transactions/", data)

    def do_transaction(self, unique_id):
        "\n\tget transaction by id, format: \033[93m[id]\033[0m\n"
        unique_id = unique_id.strip()
        if " " in unique_id:
            unique_id = unique_id.split(" ")[0]
            return self._request(
                get,
                "/v1/custody/transaction/",
                {
                    "id": unique_id,
                    "need_fee_detail": "t",
                    "need_source_address_detail": "t",
                },
            )
        else:
            return self._request(get, "/v1/custody/transaction/", {"id": unique_id})

    def do_withdraw(self, line):
        (
            "\n\twithdraw a coin, format: "
            "\033[93m[coin] [address] [amount] [in|ex]\033[0m "
            "\n\texample: "
            "\033[91mwithdraw LONT_ONT ASUACHaNnL4Q8UZ5tg1jFNBs1yzM3dFgrp 5\033[0m\n"
        )
        info = line.split()
        if len(info) not in [3, 4]:
            print("format: [coin] [address] [amount] [in|ex]")
            return
        if len(info) == 3:
            coin, address, amount = info
            force = ""
        if len(info) == 4:
            coin, address, amount, force = info
        if "|" in address:
            memo = address.split("|")[1]
            address = address.split("|")[0]
        else:
            memo = None
        request_id = "tool_%s%s" % (int(time.time()), random.randint(0, 1000))
        data = {
            "request_id": request_id,
            "coin": coin,
            "address": address,
            "amount": amount,
        }
        if force == "in":
            data["force_internal"] = "1"
        if force == "ex":
            data["force_external"] = "1"
        if memo is not None:
            data["memo"] = memo

        return self._request(post, "/v1/custody/new_withdraw_request/", data)

    def do_query_withdraw(self, request_id):
        (
            "\n\twithdraw a coin, format: "
            "\033[93m[request_id]\033[0m "
            "\n\texample: \033[91mquery_withdraw tool_154458886571\033[0m\n"
        )
        request_id = request_id.strip()
        if " " in request_id:
            request_id = request_id.split()[0]
            need_confirm_detail = True
        else:
            need_confirm_detail = False
        if need_confirm_detail:
            data = {"request_id": request_id, "need_confirm_detail": "1"}
        else:
            data = {"request_id": request_id}
        return self._request(get, "/v1/custody/withdraw_info_by_request_id/", data)

    def do_query_deposit(self, transaction_id):
        (
            "\n\tdeposit a coin, format: "
            "\033[93m[transaction_id]\033[0m "
            "\n\texample: \033[91mquery_deposit 2019020254458886571\033[0m\n"
        )
        transaction_id = transaction_id.strip()
        data = {"id": transaction_id}
        return self._request(get, "/v1/custody/deposit_info/", data)

    def do_add_hd_address(self, line):
        info = line.split()
        if len(info) not in (2,):
            print("format: [coin] [address]")
            return
        coin, addr = info
        return self._request(
            post, "/v1/custody/hd/add_address/", {"coin": coin, "address": addr}
        )


if __name__ == "__main__":
    # Replace by your own keys
    client = Client(
        api_key=API_KEY,
        api_secret=API_SECRET,
    )

    client.cmdloop()
