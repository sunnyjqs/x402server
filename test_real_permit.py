#!/usr/bin/env python3
"""
测试真实的 permit 接口
"""

import asyncio
import aiohttp
import json

async def test_real_permit():
    """测试真实的 permit 接口"""
    
    # 测试数据（这些数据需要从真实的 MetaMask 签名获取）
    test_data = {
        "owner": "0x579e306afe2f8030ac299df6c81d32e0eb67e482",
        "spender": "0x56D5A65DADC54145060F213a39B610D4DcF5DeB3", 
        "value": "20000",  # 0.02 USDC
        "deadline": 1735689600,  # 2025-01-01
        "v": 27,
        "r": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
        "s": "0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890"
    }
    
    print("🧪 测试真实的 permit 接口...")
    print(f"请求数据: {json.dumps(test_data, indent=2)}")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "http://localhost:8000/api/x402/execute-permit",
                json=test_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                print(f"状态码: {response.status}")
                
                if response.status == 200:
                    result = await response.json()
                    print("✅ Permit 接口调用成功:")
                    print(json.dumps(result, indent=2))
                else:
                    error_text = await response.text()
                    print(f"❌ Permit 接口调用失败:")
                    print(f"状态码: {response.status}")
                    print(f"错误信息: {error_text}")
                    
    except Exception as e:
        print(f"❌ 请求失败: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_real_permit())
