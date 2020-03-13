//var bitcoin = require('bitcoinjs-lib') // v3.x.x
//var keyPair = bitcoin.ECPair.fromWIF('L3oe5Wz3wmbxq9tar8nS5bqqCfjMZJNKPXAbbemoHWKXR1SAN8j2')
//var privateKey = keyPair.privateKey
/* global require Buffer*/
const sha256 = require('sha256');
const bip66 = require('bip66');
const fetch = require('node-fetch');
const ec = new require('elliptic').ec('secp256k1')

const { URLSearchParams } = require('url');

const ZERO = Buffer.alloc(1, 0)
function toDER(x){
    let i = 0
    while (x[i] === 0) ++i
    if (i === x.length) return ZERO
    x = x.slice(i)
    if (x[0] & 0x80) return Buffer.concat([ZERO, x], 1 + x.length)
    return x
}

const generate = () => {
    let key = ec.genKeyPair()
    return [key.getPublic(true, "hex"), key.getPrivate("hex")]
}


const sign = (message, api_hex) =>{
    //let message = 'GET|/v1/custody/org_info/|1541560385699|'
    let privateKey = Buffer.from(api_hex, 'hex')
    let result = ec.sign(Buffer.from(sha256.x2(message), 'hex'), privateKey)
    var r = new Buffer(result.r.toString(16, 64), 'hex')
    var s = new Buffer(result.s.toString(16, 64), 'hex')
    r = toDER(r);
    s = toDER(s);
    return bip66.encode(r, s).toString('hex');
};

const coboFetch = (method, path, params, api_key, api_hex, base = 'https://api.sandbox.cobo.com') => {
    let nonce = String(new Date().getTime());
    let sort_params = Object.keys(params).sort().map((k) => {
        return k + '=' + encodeURIComponent(params[k]).replace(/%20/g, "+");
    }).join('&');
    let content = [method, path, nonce, sort_params].join('|');
    let headers = {
        'Biz-Api-Key': api_key,
        'Biz-Api-Nonce': nonce,
        'Biz-Api-Signature': sign(content, api_hex)
    };
    if (method == 'GET'){
        return fetch(base + path + '?' + sort_params, {
            'method': method,
            'headers': headers,
        });
    }else if (method == 'POST'){

        let urlParams = new URLSearchParams();
        for (let k in params){
            urlParams.append(k, params[k])
        }

        return fetch(base + path, {
            'method': method,
            'headers': headers,
            'body': urlParams
        });
    }else{
        throw "unexpected method " + method;
    }
}


let api_key = 'x'
let api_hex = 'x'

coboFetch('GET', '/v1/custody/org_info/', {}, api_key, api_hex)
    .then(res => {
        console.log(res.status);
        res.json().then((data)=>{
            console.log(data);
        })
    }).catch(err => {
        console.log(err)
    });
coboFetch('GET', '/v1/custody/transaction_history/', {'coin': 'ETH', 'side': 'deposit'}, api_key, api_hex)
    .then(res => {
        console.log(res.status);
        res.json().then((data)=>{
            console.log(data);
        })
    }).catch(err => {
        console.log(err)
    });
coboFetch('POST', '/v1/custody/new_address/', {"coin": "ETH"}, api_key, api_hex)
    .then(res => {
        console.log(res.status);
        res.json().then((data)=>{
            console.log(data);
        })
    }).catch(err => {
        console.log(err)
    });
