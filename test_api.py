#!/usr/bin/env python3
"""
测试后端 API 是否正常运行
"""

import requests
import json

def test_backend_api():
    """测试后端 API"""
    base_url = "http://localhost:8000"
    
    print("🚀 测试后端 API...")
    
    # 测试健康检查
    try:
        response = requests.get(f"{base_url}/docs")
        if response.status_code == 200:
            print("✅ 后端服务正在运行")
        else:
            print(f"⚠️  后端服务响应异常: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到后端服务 (http://localhost:8000)")
        print("请确保后端服务正在运行:")
        print("cd server && uv run uvicorn app:app --reload --port 8000")
        return False
    
    # 测试 x402 代理
    try:
        response = requests.get(f"{base_url}/x402/test")
        if response.status_code == 200:
            print("✅ x402 代理正常")
            print(f"响应: {response.json()}")
        else:
            print(f"⚠️  x402 代理异常: {response.status_code}")
    except Exception as e:
        print(f"❌ x402 代理测试失败: {e}")
    
    return True

if __name__ == "__main__":
    test_backend_api()
