## 查询账户详情

```
Request("GET", "/v1/custody/org_info/", map[string]string{})
```

## 获取新地址

```
Request("POST", "/v1/custody/new_address/", map[string]string{
    "coin": "ETH",
})
```

## 获取交易记录

```
Request("GET", "/v1/custody/transaction_history/", map[string]string{
    "coin": "ETH",
    "side": "deposit",
})
```

## 提交提现申请

```
Request("POST", "/v1/custody/new_withdraw_request/", map[string]string{
    "coin": "ETH", 
    "address": "0x8e2782aabdf80fbb69399ce3d9bd5ae69a60462c", 
    "amount": "100000000000000", 
    "request_id": "unique_123456",
    "memo": "hello test",
})
```

## 获取提现申请信息

```
Request("GET", "/v1/custody/withdraw_info_by_request_id/", map[string]string{
    "request_id": "unique_123456",
})
```
