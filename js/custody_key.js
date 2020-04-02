const ec = new require('elliptic').ec('secp256k1')
const generate = () => {
    let key = ec.genKeyPair()
    return [key.getPublic(true, "hex"), key.getPrivate("hex")]
}
pair = generate();
console.log("API_KEY: " + pair[0]);
console.log("API_SECRET: " + pair[1]);
