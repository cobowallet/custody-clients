## 查询账户详情

```
coboFetch('GET', '/v1/custody/org_info/', {}, api_key, api_secret, host)
    .then(res => {
        res.json().then((data)=>{
            console.log(JSON.stringify(data, null, 4));
        })
    }).catch(err => {
        console.log(err)
    });
```

## 获取新地址

```
coboFetch('POST', '/v1/custody/new_address/', 
        {
            "coin": "ETH"
        }, 
        api_key, api_secret, host
    ).then(res => {
        res.json().then((data)=>{
            console.log(JSON.stringify(data, null, 4));
        })
    }).catch(err => {
        console.log(err)
    });
```

## 获取交易记录

```
coboFetch('GET', '/v1/custody/transaction_history/', 
        {
            "coin": "ETH",
            "side": "deposit"
        }, 
        api_key, api_secret, host
    ).then(res => {
        res.json().then((data)=>{
            console.log(JSON.stringify(data, null, 4));
        })
    }).catch(err => {
        console.log(err)
    });
```

## 提交提现申请

```
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
```

## 获取提现申请信息

```
coboFetch('GET', '/v1/custody/withdraw_info_by_request_id/', 
        {
            "request_id": "unique_123456"
        }, 
        api_key, api_secret, host
    ).then(res => {
        res.json().then((data)=>{
            console.log(JSON.stringify(data, null, 4));
        })
    }).catch(err => {
        console.log(err)
    });
```
