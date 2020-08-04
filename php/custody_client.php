<?php
use  mdanter\ecc;
$API_KEY = "037ae1542d92b6c80fb4fc3550faf78a23d79aa7dc46c78580ae4b8d862750ca04";
$API_SECRET = "f6eba4694090e1abe5ae048b5d0d7cc75a59d1adda03a3e4d84492456cff9b7c";
$COBO_PUB = "032f45930f652d72e0c90f71869dfe9af7d713b1f67dc2f7cb51f9572778b9c876";
$HOST = "https://custody.stage.cobowallet.cn";

require __DIR__ . "/vendor/autoload.php";

use Elliptic\EC;

function sign_hmac($message){
    global $API_SECRET;
    return hash_hmac("sha256", $message, $API_SECRET);
}
function sign_ecdsa($message){
    global $API_SECRET;
    $message = hash("sha256", hash("sha256", $message, True), True);
    $ec = new EC('secp256k1');
    $key = $ec->keyFromPrivate($API_SECRET);
    return $key->sign(bin2hex($message))->toDER('hex');
}
function verify_ecdsa($message, $timestamp, $signature){
    global $COBO_PUB;
    $message = hash("sha256", hash("sha256", "{$message}|{$timestamp}", True), True);
    $ec = new EC('secp256k1');
    $key = $ec->keyFromPublic($COBO_PUB, "hex");
    return $key->verify(bin2hex($message), $signature);
}
function sort_data($data){
    ksort($data);
    $result = [];
    foreach ($data as $key => $val) {
        array_push($result, $key."=".urlencode($val));
    }
    return join("&", $result);
}
function request($method, $path, $data){
    global $HOST;
    global $API_KEY;
    $ch = curl_init();
    $sorted_data = sort_data($data);
    $nonce = time() * 1000;
    curl_setopt ($ch, CURLOPT_RETURNTRANSFER, 1);
    curl_setopt ($ch, CURLOPT_HEADER, 1);
    curl_setopt ($ch, CURLOPT_CONNECTTIMEOUT, 10);
    curl_setopt ($ch, CURLOPT_HTTPHEADER, [
        "Biz-Api-Key:".$API_KEY,
        "Biz-Api-Nonce:".$nonce,
        "Biz-Api-Signature:".sign_ecdsa(join("|", [$method, $path, $nonce, $sorted_data]))
    ]);
    if ($method == "POST"){
        curl_setopt ($ch, CURLOPT_URL, $HOST.$path);
        curl_setopt ($ch, CURLOPT_POST, 1);
        curl_setopt ($ch, CURLOPT_POSTFIELDS, $data);
    } else {
        curl_setopt ($ch, CURLOPT_URL, $HOST.$path."?".$sorted_data);
    }
    list($header, $body) = explode("\r\n\r\n", curl_exec($ch), 2);
    preg_match("/biz_timestamp: (?<timestamp>[0-9]*)/i", $header, $match);
    $timestamp = $match["timestamp"];
    preg_match("/biz_resp_signature: (?<signature>[0-9abcdef]*)/i", $header, $match);
    $signature = $match["signature"];
    if (verify_ecdsa($body, $timestamp, $signature) != 1){
        throw new Exception("signature verify fail");
    }
    curl_close($ch);
    return $body;
}
echo request("GET", "/v1/custody/coin_info/", ["coin" => "BTC"]);
echo request("POST", "/v1/custody/new_address/", ["coin" => "BTC"]);
