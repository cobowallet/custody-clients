const crypto = require('crypto');
const sha256 = require('sha256');
const bip66 = require('bip66');
const fetch = require('node-fetch');
const ec = new require('elliptic').ec('secp256k1')

const ZERO = Buffer.alloc(1, 0)

let host = "https://api.sandbox.cobo.com";
let api_key = "x";
let api_secret = "x";
let sig_type = 'hmac'

function toDER(x){
    let i = 0
    while (x[i] === 0) ++i
    if (i === x.length) return ZERO
    x = x.slice(i)
    if (x[0] & 0x80) return Buffer.concat([ZERO, x], 1 + x.length)
    return x
}

const sign_ecc = (message, api_secret) =>{
    let privateKey = Buffer.from(api_secret, 'hex')
    let result = ec.sign(Buffer.from(sha256.x2(message), 'hex'), privateKey)
    var r = new Buffer(result.r.toString(16, 64), 'hex')
    var s = new Buffer(result.s.toString(16, 64), 'hex')
    r = toDER(r);
    s = toDER(s);
    return bip66.encode(r, s).toString('hex');
};

const sign_hmac = (message, api_secret) => {
    console.log(message)
    var x = crypto.createHmac('sha256', api_secret)
                    .update(message)
                    .digest('hex');
    console.log(x);
    return x
}

const coboFetch = (method, path, params, api_key, api_secret, host = 'https://api.sandbox.cobo.com') => {
    let nonce = String(new Date().getTime());
    let sort_params = Object.keys(params).sort().map((k) => {
        return k + '=' + encodeURIComponent(params[k]).replace(/%20/g,'+');
    }).join('&');
    let content = [method, path, nonce, sort_params].join('|');
    var signature = '';
    if (sig_type == 'ecdsa') {
        signature = sign_ecc(content, api_secret) 
    } else if (sig_type == 'hmac') {
        signature = sign_hmac(content, api_secret) 
    } else {
        throw "unexpected sig_type " + sig_type;
    }

    let headers = {
        'Biz-Api-Key': api_key,
        'Biz-Api-Nonce': nonce,
        'Biz-Api-Signature': signature
    };

    if (method == 'GET') {
        return fetch(host + path + '?' + sort_params, {
            'method': method,
            'headers': headers,
        });
    } else if (method == 'POST') {
        headers['Content-Type'] = "application/x-www-form-urlencoded";
        return fetch(host + path, {
            'method': method,
            'headers': headers,
            'body': sort_params
        });
    }else{
        throw "unexpected method " + method;
    }
}

coboFetch('POST', '/v1/custody/new_withdraw_request/', 
        {
            "coin": "ETH", 
            "address": "0x8e2782aabdf80fbb69399ce3d9bd5ae69a60462c", 
            "amount": "100000000000000", 
            "request_id": "unique_123456",
            "memo": "hello test"
        }, 
        api_key, api_secret, host
    ).then(res => {
        res.json().then((data)=>{
            console.log(JSON.stringify(data, null, 4));
        })
    }).catch(err => {
        console.log(err)
    });
