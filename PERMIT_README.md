# EIP-2612 Permit 执行接口

## 概述

新增的 `/execute-permit` 接口允许后端执行 EIP-2612 permit 授权，建立 USDC 授权关系。这个接口解决了前端需要支付 gas 费用的问题，让后端承担所有交易成本。

## 接口详情

### 端点
```
POST /x402/execute-permit
```

### 请求参数

```json
{
  "owner": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
  "spender": "0x1234567890123456789012345678901234567890",
  "value": "1000000",
  "deadline": 1735689600,
  "v": 27,
  "r": "0x1234567890123456789012345678901234567890123456789012345678901234",
  "s": "0x5678901234567890123456789012345678901234567890123456789012345678"
}
```

### 参数说明

- `owner`: 代币持有者地址（MetaMask 钱包地址）
- `spender`: 被授权地址（后端钱包地址）
- `value`: 授权金额，以 6 位小数表示（如 "1000000" 表示 1 USDC）
- `deadline`: 授权过期时间戳（Unix 时间戳）
- `v`, `r`, `s`: EIP-712 签名的参数

### 响应格式

#### 成功响应
```json
{
  "success": true,
  "txHash": "0x1234567890abcdef...",
  "message": "Permit executed successfully",
  "details": {
    "method": "cdp_native",
    "tx_hash": "0x1234567890abcdef...",
    "message": "CDP permit 授权成功: 1.0 USDC"
  }
}
```

#### 错误响应
```json
{
  "detail": "Permit execution failed: Invalid signature"
}
```

## 实现架构

### 1. 前端流程
1. 用户使用 MetaMask 对 permit 数据进行 EIP-712 签名
2. 将签名数据发送给后端 `/execute-permit` 接口
3. 后端执行 permit 授权，建立 USDC 授权关系

### 2. 后端实现
- **优先使用 CDP API**: 如果 CDP SDK 支持 permit 功能，优先使用
- **Web3 回退**: 如果 CDP 不支持，回退到 Web3 实现
- **错误处理**: 完善的错误处理和日志记录

### 3. 支持的方法

#### CDP 原生 API
```python
await cdp.evm.execute_permit(
    token_address="0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
    owner=owner,
    spender=spender,
    value=int(value),
    deadline=deadline,
    v=v,
    r=r,
    s=s
)
```

#### Web3 回退
```python
permit_txn = usdc_contract.functions.permit(
    owner_checksum,
    spender_checksum,
    int(value),
    deadline,
    v,
    bytes.fromhex(r[2:]),
    bytes.fromhex(s[2:])
).build_transaction({...})
```

## 使用示例

### 前端调用
```javascript
// 1. 用户签名 permit 数据
const signature = await ethereum.request({
  method: 'eth_signTypedData_v4',
  params: [account, JSON.stringify(permitData)]
});

// 2. 解析签名
const r = signature.slice(0, 66);
const s = '0x' + signature.slice(66, 130);
const v = parseInt(signature.slice(130, 132), 16);

// 3. 调用后端接口
const response = await fetch('/api/x402/execute-permit', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    owner: account,
    spender: backendAddress,
    value: "1000000",
    deadline: Math.floor(Date.now() / 1000) + 3600,
    v: v,
    r: r,
    s: s
  })
});

const result = await response.json();
console.log('Permit 执行结果:', result);
```

### 后端测试
```bash
# 运行测试脚本
python test_permit.py

# 或者使用 curl 测试
curl -X POST http://localhost:8000/x402/execute-permit \
  -H "Content-Type: application/json" \
  -d '{
    "owner": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
    "spender": "0x1234567890123456789012345678901234567890",
    "value": "1000000",
    "deadline": 1735689600,
    "v": 27,
    "r": "0x1234567890123456789012345678901234567890123456789012345678901234",
    "s": "0x5678901234567890123456789012345678901234567890123456789012345678"
  }'
```

## 配置要求

### 环境变量
```bash
# CDP 配置
CDP_API_KEY_ID=your_cdp_api_key_id
CDP_API_KEY_SECRET=your_cdp_api_key_secret
CDP_WALLET_SECRET=your_cdp_wallet_secret

# Web3 回退配置
EXISTING_PRIVATE_KEY=your_private_key
```

### 依赖包
```bash
# CDP SDK
pip install cdp-sdk

# Web3 依赖
pip install web3 eth-account

# HTTP 客户端
pip install httpx
```

## 错误处理

### 常见错误
1. **签名无效**: 检查 permit 签名参数是否正确
2. **过期时间**: 确保 deadline 大于当前时间
3. **网络错误**: 检查 RPC 连接和网络状态
4. **权限不足**: 确保后端有足够的权限执行交易

### 调试信息
接口会输出详细的调试信息：
```
🔄 执行 permit 授权...
Owner: 0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6
Spender: 0x1234567890123456789012345678901234567890
Value: 1000000
Deadline: 1735689600
Signature: v=27, r=0x1234..., s=0x5678...
```

## 优势

1. **用户体验**: 用户无需支付 gas 费用
2. **安全性**: 后端控制所有交易执行
3. **灵活性**: 支持多种实现方式（CDP/Web3）
4. **可靠性**: 完善的错误处理和回退机制

## 注意事项

1. **签名验证**: 确保前端生成的签名是有效的 EIP-712 签名
2. **时间同步**: 确保服务器时间与区块链时间同步
3. **Gas 费用**: 后端需要承担所有 permit 交易的 gas 费用
4. **权限管理**: 确保后端私钥安全，只用于必要的交易
