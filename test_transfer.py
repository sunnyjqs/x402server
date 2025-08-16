#!/usr/bin/env python3
"""
测试 transfer_handler 的功能
"""

import asyncio
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

async def test_transfer_handler():
    """测试 TransferHandler 的基本功能"""
    try:
        from transfer_handler import get_transfer_handler
        
        print("🔍 测试 TransferHandler...")
        
        # 获取 handler 实例
        handler = get_transfer_handler()
        if not handler:
            print("❌ 无法创建 TransferHandler 实例")
            return
        
        print(f"✅ TransferHandler 创建成功")
        print(f"📱 账户地址: {handler.account.address}")
        
        # 测试余额查询
        print("\n💰 测试 USDC 余额查询...")
        balance_result = await handler.check_usdc_balance()
        if balance_result.get("success"):
            print(f"✅ 当前 USDC 余额: {balance_result.get('balance_usdc')} USDC")
        else:
            print(f"❌ 余额查询失败: {balance_result.get('error')}")
        
        # 测试网络连接
        print("\n🌐 测试网络连接...")
        if handler.w3.is_connected():
            print(f"✅ 已连接到 Base 网络")
            print(f"🔗 RPC URL: {handler.w3.provider.endpoint_uri}")
            print(f"⛓️  Chain ID: {handler.w3.eth.chain_id}")
        else:
            print("❌ 网络连接失败")
        
        # 测试 USDC 合约
        print("\n📜 测试 USDC 合约...")
        try:
            # 尝试调用合约的 balanceOf 函数
            balance = handler.usdc_contract.functions.balanceOf(handler.account.address).call()
            print(f"✅ USDC 合约调用成功，余额: {balance / 1000000} USDC")
        except Exception as e:
            print(f"❌ USDC 合约调用失败: {e}")
        
        print("\n🎉 测试完成！")
        
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("请确保已安装 web3 依赖: pip install web3>=6.0.0")
    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    print("🚀 开始测试 TransferHandler...")
    asyncio.run(test_transfer_handler())
