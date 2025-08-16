# USDC Transfer Handler 使用说明

## 概述

这个模块实现了通过 EIP-2612 Permit 授权自动获取 USDC 并支付 x402 费用的完整流程。

## 功能特性

- 🚀 **自动 USDC 转移**: 通过 `transferFrom` 从授权地址自动获取 USDC
- 🔐 **EIP-2612 支持**: 支持无 gas 的 permit 授权机制
- 💰 **x402 集成**: 自动使用获取的 USDC 支付 x402 费用
- 🌐 **Base 网络**: 专门针对 Base 网络的 USDC 合约

## 文件结构

```
server/
├── transfer_handler.py      # USDC 转移处理核心逻辑
├── x402_proxy.py           # 修改后的 API 接口
└── test_transfer.py        # 测试脚本
```

## 环境变量配置

确保在 `.env` 文件中配置以下变量：

```bash
# 你的 CDP 子账号私钥（用于执行 transferFrom）
EXISTING_PRIVATE_KEY=your_private_key_here

# 或者使用 PRIVATE_KEY（作为备选）
PRIVATE_KEY=your_private_key_here
```

## API 接口

### 1. POST `/x402/item1` - 使用 Permit 支付

**请求体:**
```json
{
  "owner": "0x...",      // 授权地址（拥有 USDC 的地址）
  "spender": "0x...",    // 被授权地址（你的 CDP 子账号）
  "value": "50000",      // 授权金额（6位小数，50000 = 0.05 USDC）
  "deadline": 1234567890, // 过期时间戳
  "v": 27,               // 签名 v 值
  "r": "0x...",          // 签名 r 值
  "s": "0x..."           // 签名 s 值
}
```

**响应:**
```json
{
  "data": "天气数据内容",
  "status_code": 200,
  "headers": {...},
  "x_payment_response": "...",
  "transfer_info": {
    "success": true,
    "message": "USDC transfer completed before x402 payment"
  }
}
```

### 2. GET `/x402/transfer/balance` - 查询 USDC 余额

**响应:**
```json
{
  "success": true,
  "balance": 1000000,
  "balance_usdc": 1.0,
  "address": "0x..."
}
```

### 3. GET `/x402/transfer/allowance/{owner_address}` - 查询授权额度

**响应:**
```json
{
  "success": true,
  "allowance": 50000,
  "allowance_usdc": 0.05,
  "owner": "0x...",
  "spender": "0x..."
}
```

### 4. POST `/x402/transfer/execute` - 手动执行转移

**参数:**
- `owner_address`: 授权地址
- `amount`: 转移金额（6位小数）

## 完整流程

### 前端流程

1. **连接 MetaMask**: 用户连接 MetaMask 钱包
2. **执行 Permit**: 调用 USDC 合约的 `permit` 函数，建立授权
3. **调用后端**: 将 permit 参数传递给后端 API
4. **显示结果**: 显示获取的数据和支付信息

### 后端流程

1. **接收 Permit 参数**: 验证 permit 签名的有效性
2. **执行 transferFrom**: 使用 `transferFrom` 从授权地址获取 USDC
3. **调用 x402**: 使用获得的 USDC 支付 x402 费用
4. **返回结果**: 将数据返回给前端

## 测试

运行测试脚本验证功能：

```bash
cd server
python test_transfer.py
```

## 依赖安装

确保安装必要的 Python 包：

```bash
pip install web3>=6.0.0 eth-account python-dotenv
```

或者使用项目配置：

```bash
cd server
uv sync
```

## 注意事项

1. **私钥安全**: 确保私钥安全存储，不要暴露在代码中
2. **网络配置**: 当前配置为 Base 主网，如需测试网请修改配置
3. **Gas 费用**: `transferFrom` 调用需要支付 gas 费用
4. **授权额度**: 确保授权额度足够支付所需的 USDC 金额

## 故障排除

### 常见错误

1. **"EXISTING_PRIVATE_KEY not configured"**
   - 检查 `.env` 文件中的私钥配置

2. **"Failed to connect to Base network"**
   - 检查网络连接和 RPC URL 配置

3. **"Insufficient allowance"**
   - 检查授权额度是否足够

4. **"Transaction failed"**
   - 检查账户余额是否足够支付 gas 费用

### 调试技巧

1. 使用 `test_transfer.py` 脚本测试基本功能
2. 检查后端日志输出
3. 验证 MetaMask 网络设置
4. 确认 USDC 合约地址正确性

## 更新日志

- **v1.0.0**: 初始版本，支持基本的 transferFrom 和 x402 集成
- 支持 EIP-2612 Permit 授权
- 自动 USDC 转移和 x402 支付
- Base 网络 USDC 合约集成
