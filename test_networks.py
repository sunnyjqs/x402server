#!/usr/bin/env python3
"""
测试所有网络配置
验证 Base 主网、Base Sepolia 和以太坊 Sepolia 的网络连接
"""

import asyncio
import os
from dotenv import load_dotenv
from web3 import Web3
from eth_account import Account

# 加载环境变量
load_dotenv()

# 网络配置
NETWORKS = {
    "mainnet": {
        "name": "Base 主网",
        "chain_id": 8453,
        "rpc_url": "https://mainnet.base.org",
        "usdc_address": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
    },
    "baseSepolia": {
        "name": "Base Sepolia 测试网",
        "chain_id": 84532,
        "rpc_url": "https://sepolia.base.org",
        "usdc_address": "0x036CbD53842c5426634e7929541eC2318f3dCF7e"
    },
    "ethSepolia": {
        "name": "以太坊 Sepolia 测试网",
        "chain_id": 11155111,
        "rpc_url": "https://sepolia.infura.io/v3/9511773c563f4094b07478fb1706488b",
        "usdc_address": "0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238"
    }
}

async def test_network(network_key: str, network_config: dict):
    """测试单个网络"""
    print(f"\n🔍 测试 {network_config['name']}...")
    print(f"   RPC: {network_config['rpc_url']}")
    print(f"   Chain ID: {network_config['chain_id']}")
    print(f"   USDC: {network_config['usdc_address']}")
    
    try:
        # 1. 连接测试
        w3 = Web3(Web3.HTTPProvider(network_config["rpc_url"]))
        
        if not w3.is_connected():
            print(f"   ❌ 无法连接到 {network_config['name']}")
            return False
        
        print(f"   ✅ 连接成功")
        
        # 2. 检查链 ID
        actual_chain_id = w3.eth.chain_id
        if actual_chain_id != network_config["chain_id"]:
            print(f"   ⚠️  链 ID 不匹配，期望: {network_config['chain_id']}, 实际: {actual_chain_id}")
        else:
            print(f"   ✅ 链 ID 匹配")
        
        # 3. 检查最新区块
        latest_block = w3.eth.block_number
        print(f"   📦 最新区块: {latest_block}")
        
        # 4. 检查 USDC 合约
        usdc_code = w3.eth.get_code(network_config["usdc_address"])
        if usdc_code == b'':
            print(f"   ❌ USDC 合约地址没有代码")
            return False
        else:
            print(f"   ✅ USDC 合约存在 ({len(usdc_code)} bytes)")
        
        # 5. 检查 gas 价格
        gas_price = w3.eth.gas_price
        gas_price_gwei = w3.from_wei(gas_price, 'gwei')
        print(f"   ⛽ Gas 价格: {gas_price_gwei:.2f} Gwei")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 测试失败: {e}")
        return False

async def main():
    """主函数"""
    print("🚀 开始测试所有网络配置...")
    print("=" * 80)
    
    results = {}
    
    # 测试所有网络
    for network_key, network_config in NETWORKS.items():
        success = await test_network(network_key, network_config)
        results[network_key] = success
    
    # 显示测试结果
    print("\n" + "=" * 80)
    print("📊 测试结果汇总:")
    print("=" * 80)
    
    for network_key, success in results.items():
        status = "✅ 成功" if success else "❌ 失败"
        print(f"{NETWORKS[network_key]['name']}: {status}")
    
    # 显示配置建议
    print("\n📝 前端网络配置建议:")
    print("const NETWORKS = {")
    for network_key, network_config in NETWORKS.items():
        print(f"  {network_key}: {{")
        print(f"    key: '{network_key}',")
        print(f"    name: '{network_config['name']}',")
        print(f"    chainId: {network_config['chain_id']},")
        print(f"    chainIdHex: '0x{network_config['chain_id']:x}',")
        print(f"    usdcAddress: '{network_config['usdc_address']}',")
        print(f"    usdcName: 'USDC',")
        print(f"    usdcVersion: '1',")
        print(f"    rpcUrl: '{network_config['rpc_url']}'")
        print(f"  }},")
    print("};")

if __name__ == "__main__":
    asyncio.run(main())
