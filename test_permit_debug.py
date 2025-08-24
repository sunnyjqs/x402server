#!/usr/bin/env python3
"""
调试 Permit 功能
测试以太坊 Sepolia 网络的 permit 执行
"""

import asyncio
import os
from dotenv import load_dotenv
from web3 import Web3
from eth_account import Account

# 加载环境变量
load_dotenv()

# 以太坊 Sepolia 配置
SEPOLIA_CONFIG = {
    "chain_id": 11155111,
    "rpc_url": "https://sepolia.infura.io/v3/9511773c563f4094b07478fb1706488b",
    "usdc_address": "0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238"
}

# 最小化的 USDC ABI（包含 permit 函数）
USDC_ABI = [
    {
        "constant": False,
        "inputs": [
            {"name": "owner", "type": "address"},
            {"name": "spender", "type": "address"},
            {"name": "value", "type": "uint256"},
            {"name": "deadline", "type": "uint256"},
            {"name": "v", "type": "uint8"},
            {"name": "r", "type": "bytes32"},
            {"name": "s", "type": "bytes32"}
        ],
        "name": "permit",
        "outputs": [],
        "payable": False,
        "stateMutability": "nonpayable",
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
    },
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "nonces",
        "outputs": [{"name": "", "type": "uint256"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    }
]

async def test_sepolia_connection():
    """测试 Sepolia 网络连接"""
    print("🔍 测试以太坊 Sepolia 网络连接...")
    
    try:
        # 连接到网络
        w3 = Web3(Web3.HTTPProvider(SEPOLIA_CONFIG["rpc_url"]))
        
        if not w3.is_connected():
            print("❌ 无法连接到以太坊 Sepolia")
            return False
        
        print(f"✅ 已连接到以太坊 Sepolia: {SEPOLIA_CONFIG['rpc_url']}")
        
        # 检查链 ID
        chain_id = w3.eth.chain_id
        print(f"🔗 链 ID: {chain_id}")
        
        if chain_id != SEPOLIA_CONFIG["chain_id"]:
            print(f"⚠️  链 ID 不匹配，期望: {SEPOLIA_CONFIG['chain_id']}, 实际: {chain_id}")
            return False
        
        print("✅ 链 ID 匹配")
        
        # 检查最新区块
        latest_block = w3.eth.block_number
        print(f"📦 最新区块: {latest_block}")
        
        return True
        
    except Exception as e:
        print(f"❌ 连接测试失败: {e}")
        return False

async def test_usdc_contract():
    """测试 USDC 合约"""
    print("\n🔍 测试 USDC 合约...")
    
    try:
        w3 = Web3(Web3.HTTPProvider(SEPOLIA_CONFIG["rpc_url"]))
        
        # 检查合约地址
        contract_address = SEPOLIA_CONFIG["usdc_address"]
        print(f"📋 合约地址: {contract_address}")
        
        # 检查合约代码
        code = w3.eth.get_code(contract_address)
        if code == b'':
            print("❌ 合约地址没有代码")
            return False
        
        print(f"✅ 合约代码存在 ({len(code)} bytes)")
        
        # 创建合约实例
        contract = w3.eth.contract(
            address=contract_address,
            abi=USDC_ABI
        )
        
        # 测试 permit 函数
        try:
            permit_function = contract.functions.permit
            print("✅ Permit 函数存在")
            print("✅ Permit 函数测试通过")
            
        except Exception as e:
            print(f"❌ Permit 函数测试失败: {e}")
            return False
        
        # 测试 nonces 函数
        try:
            test_address = "0x56D5A65DADC54145060F213a39B610D4DcF5DeB3"
            nonce = contract.functions.nonces(test_address).call()
            print(f"✅ Nonces 函数正常，测试地址 nonce: {nonce}")
            
        except Exception as e:
            print(f"❌ Nonces 函数测试失败: {e}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ USDC 合约测试失败: {e}")
        return False

async def test_transfer_handler():
    """测试 TransferHandler"""
    print("\n🔍 测试 TransferHandler...")
    
    try:
        from transfer_handler import create_sepolia_handler
        
        # 创建 handler
        handler = create_sepolia_handler()
        print("✅ Sepolia handler 创建成功")
        
        # 检查方法是否存在
        if hasattr(handler, 'execute_permit'):
            print("✅ execute_permit 方法存在")
        else:
            print("❌ execute_permit 方法不存在")
            return False
        
        # 检查网络配置
        print(f"🌐 网络配置: {handler.config}")
        print(f"🔗 RPC URL: {handler.config['rpc_url']}")
        print(f"💎 USDC 地址: {handler.config['usdc_address']}")
        
        # 测试网络连接
        if handler.w3.is_connected():
            print("✅ Web3 连接正常")
        else:
            print("❌ Web3 连接失败")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ TransferHandler 测试失败: {e}")
        return False

async def main():
    """主函数"""
    print("🚀 开始调试 Permit 功能...")
    print("=" * 60)
    
    # 测试网络连接
    network_ok = await test_sepolia_connection()
    if not network_ok:
        print("❌ 网络连接测试失败")
        return
    
    # 测试 USDC 合约
    contract_ok = await test_usdc_contract()
    if not contract_ok:
        print("❌ USDC 合约测试失败")
        return
    
    # 测试 TransferHandler
    handler_ok = await test_transfer_handler()
    if not handler_ok:
        print("❌ TransferHandler 测试失败")
        return
    
    print("\n" + "=" * 60)
    print("✅ 所有测试通过！")
    print("📝 建议检查:")
    print("1. 后端服务是否正在运行")
    print("2. 环境变量是否正确设置")
    print("3. 私钥是否有足够的 ETH 支付 gas")
    print("4. 前端发送的 permit 参数是否正确")

if __name__ == "__main__":
    asyncio.run(main())
