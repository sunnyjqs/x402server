#!/usr/bin/env python3
"""
测试 /execute-permit 接口的脚本
"""

import asyncio
import httpx
import json
from typing import Dict, Any

async def test_execute_permit():
    """测试 execute-permit 接口"""
    
    # 测试数据（这些是示例数据，实际使用时需要真实的签名）
    test_permit_data = {
        "owner": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",  # 示例 owner 地址
        "spender": "0x1234567890123456789012345678901234567890",  # 示例 spender 地址
        "value": "1000000",  # 1 USDC (6位小数)
        "deadline": 1735689600,  # 示例过期时间
        "v": 27,  # 示例签名 v
        "r": "0x1234567890123456789012345678901234567890123456789012345678901234",  # 示例签名 r
        "s": "0x5678901234567890123456789012345678901234567890123456789012345678"   # 示例签名 s
    }
    
    print("🧪 测试 /execute-permit 接口...")
    print(f"测试数据: {json.dumps(test_permit_data, indent=2)}")
    
    try:
        async with httpx.AsyncClient() as client:
            # 测试接口
            response = await client.post(
                "http://localhost:8000/x402/execute-permit",
                json=test_permit_data,
                timeout=30.0
            )
            
            print(f"状态码: {response.status_code}")
            print(f"响应头: {dict(response.headers)}")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ 接口调用成功!")
                print(f"响应数据: {json.dumps(result, indent=2)}")
            else:
                print("❌ 接口调用失败!")
                print(f"错误响应: {response.text}")
                
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")

async def test_transfer_handler():
    """测试 transfer handler 的 permit 功能"""
    
    print("\n🧪 测试 transfer handler 的 permit 功能...")
    
    try:
        # 导入并测试 transfer handler
        from transfer_handler import get_transfer_handler
        
        handler = get_transfer_handler()
        if handler:
            print("✅ Transfer handler 初始化成功")
            
            # 测试 permit 方法是否存在
            if hasattr(handler, 'execute_permit'):
                print("✅ execute_permit 方法存在")
                
                # 测试 permit 执行（使用示例数据）
                test_data = {
                    "owner": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
                    "spender": "0x1234567890123456789012345678901234567890",
                    "value": "1000000",
                    "deadline": 1735689600,
                    "v": 27,
                    "r": "0x1234567890123456789012345678901234567890123456789012345678901234",
                    "s": "0x5678901234567890123456789012345678901234567890123456789012345678"
                }
                
                print("🔄 尝试执行 permit...")
                result = await handler.execute_permit(**test_data)
                print(f"Permit 执行结果: {json.dumps(result, indent=2)}")
            else:
                print("❌ execute_permit 方法不存在")
        else:
            print("❌ Transfer handler 初始化失败")
            
    except Exception as e:
        print(f"❌ Transfer handler 测试失败: {str(e)}")

async def test_cdp_transfer_handler():
    """测试 CDP transfer handler 的 permit 功能"""
    
    print("\n🧪 测试 CDP transfer handler 的 permit 功能...")
    
    try:
        # 导入并测试 CDP transfer handler
        from cdp_transfer_handler import get_cdp_transfer_handler
        
        handler = get_cdp_transfer_handler()
        if handler:
            print("✅ CDP Transfer handler 初始化成功")
            
            # 测试 permit 方法是否存在
            if hasattr(handler, 'execute_permit'):
                print("✅ execute_permit 方法存在")
                
                # 测试 permit 执行（使用示例数据）
                test_data = {
                    "owner": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
                    "spender": "0x1234567890123456789012345678901234567890",
                    "value": "1000000",
                    "deadline": 1735689600,
                    "v": 27,
                    "r": "0x1234567890123456789012345678901234567890123456789012345678901234",
                    "s": "0x5678901234567890123456789012345678901234567890123456789012345678"
                }
                
                print("🔄 尝试执行 permit...")
                result = await handler.execute_permit(**test_data)
                print(f"Permit 执行结果: {json.dumps(result, indent=2)}")
            else:
                print("❌ execute_permit 方法不存在")
        else:
            print("❌ CDP Transfer handler 初始化失败")
            
    except Exception as e:
        print(f"❌ CDP Transfer handler 测试失败: {str(e)}")

async def main():
    """主测试函数"""
    print("🚀 开始测试 /execute-permit 接口...")
    
    # 测试 transfer handlers
    await test_transfer_handler()
    await test_cdp_transfer_handler()
    
    # 测试 API 接口（需要服务器运行）
    print("\n" + "="*50)
    print("注意: 以下测试需要服务器在 localhost:8000 运行")
    print("="*50)
    
    await test_execute_permit()
    
    print("\n✅ 测试完成!")

if __name__ == "__main__":
    asyncio.run(main())
