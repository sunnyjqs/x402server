#!/usr/bin/env python3
"""
测试 Permit 请求
模拟前端发送的 permit 参数
"""

import requests
import json

def test_permit_request():
    """测试 permit 请求"""
    base_url = "http://localhost:8000"
    
    print("🚀 测试 Permit 请求...")
    
    # 模拟前端的 permit 请求数据
    permit_data = {
        "owner": "0x687edca19d27753024e767648d23f5d33223d4d9",  # 示例地址
        "spender": "0xB894712a18cE4ab381E0D6EbdB9411D092dE25E4",  # 示例地址
        "value": "20000",  # 0.02 USDC
        "deadline": 1756244475,  # 示例过期时间
        "v": 27,  # 示例签名 v
        "r": "0xc46e16e82b3491b4644b09cfcf94a43a50389351fa2261612d7951f0420d58c4",  # 示例签名 r
        "s": "0x2e4eabadef1b8afbb42e1949273aa602ed58e7b1069843df12aad53d7ea563d0",  # 示例签名 s
        "network": "ethSepolia"  # 以太坊 Sepolia 网络
    }
    
    print("📝 发送的 Permit 数据:")
    print(json.dumps(permit_data, indent=2))
    
    try:
        # 发送 POST 请求到 execute-permit 端点
        response = requests.post(
            f"{base_url}/x402/execute-permit",
            json=permit_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"\n📊 响应状态码: {response.status_code}")
        print(f"📊 响应头: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ Permit 请求成功!")
            print(f"📄 响应内容: {response.json()}")
        else:
            print("❌ Permit 请求失败!")
            print(f"📄 错误响应: {response.text}")
            
            # 尝试解析错误详情
            try:
                error_detail = response.json()
                if "detail" in error_detail:
                    print(f"🔍 错误详情: {error_detail['detail']}")
            except:
                pass
                
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到后端服务")
    except Exception as e:
        print(f"❌ 请求失败: {e}")

if __name__ == "__main__":
    test_permit_request()
