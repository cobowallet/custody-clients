Cobo Custody Api Client Demo

## Requirements && Execute:

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
    - com/cobo/custody/demo/Main.java
    - run testGenerateKeysAndSignMessage to get API_KEY, API_SECRET
    - register API_KEY on Custody Web
    - replace API_KEY API_SECRET in testApi key, secret and run testApi

* Php
    - composer require simplito/elliptic-php
    - php custody_key.php
    - register API_KEY on Custody Web
    - replace API_KEY API_SECRET in custody_client.php
    - php custody_client.php
