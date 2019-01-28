package main

import "fmt"
import "time"
import "io"
import "strings"
import "sort"
import "net/url"
import "crypto/hmac"
import ioutil "io/ioutil"
import hex "encoding/hex"
import sha256 "crypto/sha256"
import secp256k1 "github.com/decred/dcrd/dcrec/secp256k1"
import http "net/http"

const host = "https://api.sandbox.cobo.com"
const api_key = "x"
const api_secret = "x"

const SIG_TYPE = "hmac"

func SortParams(params map[string]string) string {
	keys := make([]string, len(params))
	i := 0
	for k, _ := range params {
		keys[i] = k
		i++
	}
	sort.Strings(keys)
	sorted := make([]string, len(params))
	i = 0
	for _, k := range keys {
		sorted[i] = k + "=" + url.QueryEscape(params[k])
		i++
	}
	return strings.Join(sorted, "&")
}

func Hash256(s string) string {
	hash_result := sha256.Sum256([]byte(s))
	hash_string := string(hash_result[:])
	return hash_string
}

func doubleHash256(s string) string {
	return Hash256(Hash256(s))
}

func SignEcc(message string) string {
	decoded_api_secret, _ := hex.DecodeString(api_secret)
	privKey, _ := secp256k1.PrivKeyFromBytes(decoded_api_secret)
	sig, _ := privKey.Sign([]byte(doubleHash256(message)))
	return fmt.Sprintf("%x", sig.Serialize())
}

func SignHmac(message string) string {
    h := hmac.New(sha256.New, []byte(api_secret))
    io.WriteString(h, message)
    return fmt.Sprintf("%x", h.Sum(nil))
}

func Request(method string, path string, params map[string]string) string {
	client := &http.Client{}
	nonce := fmt.Sprintf("%d", time.Now().Unix() * 1000)
	sorted := SortParams(params)
	var req *http.Request

	if method == "POST" {
		req, _ = http.NewRequest(method, host + path, strings.NewReader(sorted))
		req.Header.Set("Content-Type", "application/x-www-form-urlencoded")
	} else {
		req, _ = http.NewRequest(method, host + path + "?" + sorted, strings.NewReader(""))
	}
	content := strings.Join([]string{method, path, nonce, sorted}, "|")

	req.Header.Set("Biz-Api-Key", api_key)
	req.Header.Set("Biz-Api-Nonce", nonce)
	if SIG_TYPE == "hmac" {
        req.Header.Set("Biz-Api-Signature", SignHmac(content))
    } else if (SIG_TYPE == "ecdsa") {
        req.Header.Set("Biz-Api-Signature", SignEcc(content))
    } else {
        fmt.Printf("Not supported signature type")
        return ""
    }

	resp, _ := client.Do(req)

	defer resp.Body.Close()

	body, _ := ioutil.ReadAll(resp.Body)
	return string(body)
}

func main() {
    res := Request("GET", "/v1/custody/org_info/", map[string]string{})
	fmt.Printf("%v", res)
}
