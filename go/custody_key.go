package main

import (
	"crypto/rand"
	"fmt"
)
import "github.com/btcsuite/btcd/btcec"

func GenerateRandomKeyPair() {
	apiSecret := make([]byte, 32)
	if _, err := rand.Read(apiSecret); err != nil {
		panic(err)
	}
	privKey, _ := btcec.PrivKeyFromBytes(btcec.S256(), apiSecret)
	apiKey := fmt.Sprintf("%x", privKey.PubKey().SerializeCompressed())
	apiSecretStr := fmt.Sprintf("%x", apiSecret)

	fmt.Printf("API_Key: %s\nAPI_SECRET: %s\n", apiKey, apiSecretStr)
}

func main() {
	GenerateRandomKeyPair()
}
