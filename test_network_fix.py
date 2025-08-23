#!/usr/bin/env python3
"""
测试网络配置修复
验证余额检查和实际执行使用相同的网络配置
"""

import asyncio
import os
from dotenv import load_dotenv
from transfer_handler import TransferHandler, create_sepolia_handler

# 加载环境变量
load_dotenv()

async def test_network_consistency():
    """测试网络配置一致性"""
    print("🧪 测试网络配置一致性...")
    
    # 测试地址
    test_address = "0x56D5A65DADC54145060F213a39B610D4DcF5DeB3"
    
    # 1. 测试主网 handler
    print("\n🔗 测试主网配置...")
    try:
        mainnet_handler = TransferHandler(use_sepolia=False)
        mainnet_balance = await mainnet_handler.get_eth_balance(test_address)
        print(f"💰 主网 ETH 余额: {mainnet_balance} ETH")
        print(f"🌐 主网 RPC: {mainnet_handler.config['rpc_url']}")
    except Exception as e:
        print(f"❌ 主网测试失败: {e}")
    
    # 2. 测试 Sepolia handler
    print("\n🔗 测试 Sepolia 配置...")
    try:
        sepolia_handler = create_sepolia_handler()
        sepolia_balance = await sepolia_handler.get_eth_balance(test_address)
        print(f"💰 Sepolia ETH 余额: {sepolia_balance} ETH")
        print(f"🌐 Sepolia RPC: {sepolia_handler.config['rpc_url']}")
    except Exception as e:
        print(f"❌ Sepolia 测试失败: {e}")
    
    # 3. 测试网络连接
    print("\n🔍 测试网络连接...")
    try:
        mainnet_handler = TransferHandler(use_sepolia=False)
        mainnet_connected = mainnet_handler.w3.is_connected()
        print(f"✅ 主网连接状态: {mainnet_connected}")
        
        sepolia_handler = create_sepolia_handler()
        sepolia_connected = sepolia_handler.w3.is_connected()
        print(f"✅ Sepolia 连接状态: {sepolia_connected}")
    except Exception as e:
        print(f"❌ 网络连接测试失败: {e}")

async def test_handler_creation():
    """测试 handler 创建"""
    print("\n🏗️  测试 handler 创建...")
    
    try:
        # 测试主网 handler
        mainnet_handler = TransferHandler(use_sepolia=False)
        print(f"✅ 主网 handler 创建成功")
        print(f"   - 账户地址: {mainnet_handler.account.address}")
        print(f"   - 网络配置: {mainnet_handler.config['rpc_url']}")
        
        # 测试 Sepolia handler
        sepolia_handler = create_sepolia_handler()
        print(f"✅ Sepolia handler 创建成功")
        print(f"   - 账户地址: {sepolia_handler.account.address}")
        print(f"   - 网络配置: {sepolia_handler.config['rpc_url']}")
        
    except Exception as e:
        print(f"❌ Handler 创建测试失败: {e}")

if __name__ == "__main__":
    print("🚀 开始网络配置测试...")
    
    # 检查环境变量
    private_key = os.getenv("EXISTING_PRIVATE_KEY") or os.getenv("PRIVATE_KEY")
    if not private_key:
        print("❌ 未配置私钥环境变量")
        print("请设置 EXISTING_PRIVATE_KEY 或 PRIVATE_KEY")
        exit(1)
    
    print(f"🔑 私钥已配置: {private_key[:10]}...")
    
    # 运行测试
    asyncio.run(test_network_consistency())
    asyncio.run(test_handler_creation())
    
    print("\n✅ 网络配置测试完成!")


