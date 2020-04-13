## Cobo Custody Api Client Demo

Cobo Custody offers a RESTful API to integrate WaaS (Wallet as a service) for over 43 main chains and 1000+ tokens with your application through a simple and unified interface. Here's some samples guiding you how to generate API Key pairs (Key & Secret) and interact with Cobo Custody.

More info: [API Documentation](https://doc.custody.cobo.com/)

## Requirements && Execute

* Python
    - python3.6
    - pip install -r requirements.txt
    - python custody_key.py
    - register API_KEY on Custody Web
    - replace API_KEY, API_SECRET in custody_client.py
    - python custody_client.py

* Go
    - go run custody_key.go
    - register API_KEY on Custody Web
    - replace API_KEY, API_SECRET in custody_client.go
    - go run custody_client.go

* Js
    - npm install
    - node custody_key.js
    - register API_KEY on Custody Web
    - replace API_KEY API_SECRET in custody_client.js
    - node custody_client.js

* Java
    - use your IDE to manage com/cobo/custody/demo/Main.java
    - OR
    - gradle build
    - gradle key
    - register API_KEY on Custody Web
    - replace API_KEY API_SECRET in com/cobo/custody/demo/Main.java
    - gradle build
    - gradle run

* Php
    - composer require simplito/elliptic-php
    - php custody_key.php
    - register API_KEY on Custody Web
    - replace API_KEY API_SECRET in custody_client.php
    - php custody_client.php

## Support

Please contact your VIP Customer Service or custodyservice@cobo.com
