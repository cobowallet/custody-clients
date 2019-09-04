<?php
use  mdanter\ecc;
$API_KEY = "x";
$API_SECRET = "x";
$HOST = "https://api.sandbox.cobo.com";

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
    $file_contents = curl_exec($ch);
    curl_close($ch);
    return $file_contents;
}

echo request("GET", "/v1/custody/coin_info/", ["coin" => "BTC"]);
echo request("POST", "/v1/custody/new_address/", ["coin" => "BTC"]);

