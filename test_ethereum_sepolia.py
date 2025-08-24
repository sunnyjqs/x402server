#!/usr/bin/env python3
"""
测试以太坊 Sepolia 网络配置
验证 RPC 连接、USDC 合约和网络参数
"""

import asyncio
import os
from dotenv import load_dotenv
from web3 import Web3
from eth_account import Account

# 加载环境变量
load_dotenv()

# 以太坊 Sepolia 测试网配置
SEPOLIA_CONFIG = {
    "chain_id": 11155111,  # 以太坊 Sepolia testnet
    "rpc_url": "https://sepolia.infura.io/v3/9511773c563f4094b07478fb1706488b",
    "usdc_address": "0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238"
}

# 最小化的 ERC20 ABI（只包含必要的函数）
MINIMAL_ERC20_ABI = [
    {
        "constant": True,
        "inputs": [],
        "name": "name",
        "outputs": [{"name": "", "type": "string"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "symbol",
        "outputs": [{"name": "", "type": "string"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "decimals",
        "outputs": [{"name": "", "type": "uint8"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    }
]

async def test_ethereum_sepolia():
    """测试以太坊 Sepolia 测试网配置"""
    print("🔍 测试以太坊 Sepolia 测试网配置...")
    
    try:
        # 1. 连接到以太坊 Sepolia 测试网
        w3 = Web3(Web3.HTTPProvider(SEPOLIA_CONFIG["rpc_url"]))
        
        if not w3.is_connected():
            print("❌ 无法连接到以太坊 Sepolia 测试网")
            return False
        
        print(f"✅ 已连接到以太坊 Sepolia 测试网: {SEPOLIA_CONFIG['rpc_url']}")
        
        # 2. 检查网络信息
        chain_id = w3.eth.chain_id
        print(f"🔗 链 ID: {chain_id}")
        
        if chain_id != SEPOLIA_CONFIG["chain_id"]:
            print(f"⚠️  警告: 链 ID 不匹配，期望: {SEPOLIA_CONFIG['chain_id']}, 实际: {chain_id}")
        else:
            print("✅ 链 ID 匹配正确")
        
        # 3. 检查最新区块
        latest_block = w3.eth.block_number
        print(f"📦 最新区块号: {latest_block}")
        
        # 4. 验证 USDC 合约
        contract_address = SEPOLIA_CONFIG["usdc_address"]
        print(f"🔍 验证 USDC 合约: {contract_address}")
        
        # 检查地址格式
        if not Web3.is_address(contract_address):
            print("❌ USDC 合约地址格式无效")
            return False
        
        # 创建合约实例
        usdc_contract = w3.eth.contract(
            address=contract_address,
            abi=MINIMAL_ERC20_ABI
        )
        
        # 测试合约调用
        try:
            name = usdc_contract.functions.name().call()
            symbol = usdc_contract.functions.symbol().call()
            decimals = usdc_contract.functions.decimals().call()
            
            print(f"✅ USDC 合约验证成功:")
            print(f"   - 名称: {name}")
            print(f"   - 符号: {symbol}")
            print(f"   - 小数位数: {decimals}")
            
        except Exception as e:
            print(f"❌ USDC 合约调用失败: {e}")
            return False
        
        # 5. 检查 gas 价格
        gas_price = w3.eth.gas_price
        gas_price_gwei = w3.from_wei(gas_price, 'gwei')
        print(f"⛽ Gas 价格: {gas_price_gwei:.2f} Gwei")
        
        print("\n✅ 以太坊 Sepolia 测试网配置验证完成!")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

async def main():
    """主函数"""
    print("🚀 开始以太坊 Sepolia 测试网配置验证...")
    print("=" * 60)
    
    success = await test_ethereum_sepolia()
    
    if success:
        print("\n📝 配置信息:")
        print("SEPOLIA_USDC_CONFIG = {")
        print(f'    "chain_id": {SEPOLIA_CONFIG["chain_id"]},')
        print(f'    "rpc_url": "{SEPOLIA_CONFIG["rpc_url"]}",')
        print(f'    "usdc_address": "{SEPOLIA_CONFIG["usdc_address"]}",')
        print("}")
    else:
        print("\n❌ 配置验证失败，请检查网络连接和合约地址")

if __name__ == "__main__":
    asyncio.run(main())
