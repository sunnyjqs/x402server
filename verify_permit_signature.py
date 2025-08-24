#!/usr/bin/env python3
"""
验证 Permit 签名
检查 EIP-2612 permit 签名的有效性
"""

import asyncio
import os
import time
from dotenv import load_dotenv
from web3 import Web3
from eth_account import Account
from eth_account.messages import encode_typed_data

# 加载环境变量
load_dotenv()

# 以太坊 Sepolia 配置
SEPOLIA_CONFIG = {
    "chain_id": 11155111,
    "rpc_url": "https://sepolia.infura.io/v3/9511773c563f4094b07478fb1706488b",
    "usdc_address": "0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238",
    "usdc_name": "USDC",
    "usdc_version": "1"
}

def get_domain_separator(contract_address: str, chain_id: int, token_name: str, token_version: str):
    """获取 EIP-712 域名分隔符"""
    return {
        "name": token_name,
        "version": token_version,
        "chainId": chain_id,
        "verifyingContract": contract_address,
    }

def get_permit_types():
    """获取 Permit 类型定义"""
    return {
        "Permit": [
            {"name": "owner", "type": "address"},
            {"name": "spender", "type": "address"},
            {"name": "value", "type": "uint256"},
            {"name": "nonce", "type": "uint256"},
            {"name": "deadline", "type": "uint256"},
        ]
    }

async def verify_permit_signature():
    """验证 permit 签名"""
    print("🔍 验证 Permit 签名...")
    
    # 从日志中提取的参数
    owner = "0x5844b45b669dbaac536bcb7f660dcb7df1774d0c"
    spender = "0xd29427Eee41C6cB3BCb58F84820c62E8A9ab324b"
    value = "19998"
    deadline = 1791456512
    v = 28
    r = "0x6d97bfdcaf0c01e886e0f2454c7c1be0d38261499293eac57aad65abe5ffa03b"
    s = "0x76d93637c8829520bbaa1987dadca8fc9efc630f596a5bdeaf6009b7567b1707"
    
    print(f"📝 Permit 参数:")
    print(f"   Owner: {owner}")
    print(f"   Spender: {spender}")
    print(f"   Value: {value}")
    print(f"   Deadline: {deadline}")
    print(f"   V: {v}")
    print(f"   R: {r}")
    print(f"   S: {s}")
    
    try:
        # 连接到网络
        w3 = Web3(Web3.HTTPProvider(SEPOLIA_CONFIG["rpc_url"]))
        
        if not w3.is_connected():
            print("❌ 无法连接到网络")
            return False
        
        print(f"✅ 已连接到以太坊 Sepolia")
        
        # 获取当前 nonce
        print(f"\n🔍 获取当前 nonce...")
        owner_checksum = Web3.to_checksum_address(owner)
        current_nonce = w3.eth.get_transaction_count(owner_checksum)
        print(f"   当前 nonce: {current_nonce}")
        
        # 从合约获取 nonce
        print(f"\n🔍 从合约获取 nonce...")
        usdc_contract = w3.eth.contract(
            address=SEPOLIA_CONFIG["usdc_address"],
            abi=[{
                "constant": True,
                "inputs": [{"name": "_owner", "type": "address"}],
                "name": "nonces",
                "outputs": [{"name": "", "type": "uint256"}],
                "payable": False,
                "stateMutability": "view",
                "type": "function"
            }]
        )
        
        contract_nonce = usdc_contract.functions.nonces(owner_checksum).call()
        print(f"   合约 nonce: {contract_nonce}")
        
        # 检查 deadline
        current_time = int(time.time())
        print(f"\n🔍 检查 deadline...")
        print(f"   当前时间: {current_time}")
        print(f"   Deadline: {deadline}")
        print(f"   剩余时间: {deadline - current_time} 秒")
        
        if deadline < current_time:
            print(f"   ❌ Deadline 已过期！")
            return False
        else:
            print(f"   ✅ Deadline 有效")
        
        # 构建 EIP-712 消息
        print(f"\n🔍 构建 EIP-712 消息...")
        domain = get_domain_separator(
            SEPOLIA_CONFIG["usdc_address"],
            SEPOLIA_CONFIG["chain_id"],
            SEPOLIA_CONFIG["usdc_name"],
            SEPOLIA_CONFIG["usdc_version"]
        )
        
        types = get_permit_types()
        
        message = {
            "owner": owner,
            "spender": spender,
            "value": int(value),
            "nonce": contract_nonce,  # 使用合约的 nonce
            "deadline": deadline,
        }
        
        print(f"   域名: {domain}")
        print(f"   类型: {types}")
        print(f"   消息: {message}")
        
        # 验证签名
        print(f"\n🔍 验证签名...")
        try:
            # 重建签名
            signature = r + s[2:] + hex(v)[2:].zfill(2)
            print(f"   重建的签名: {signature}")
            
            # 验证签名
            recovered_address = w3.eth.account.recover_message(
                encode_typed_data({
                    "types": {**types, "EIP712Domain": [
                        {"name": "name", "type": "string"},
                        {"name": "version", "type": "string"},
                        {"name": "chainId", "type": "uint256"},
                        {"name": "verifyingContract", "type": "address"},
                    ]},
                    "primaryType": "Permit",
                    "domain": domain,
                    "message": message,
                }),
                signature=signature
            )
            
            print(f"   恢复的地址: {recovered_address}")
            print(f"   期望的地址: {owner}")
            
            if recovered_address.lower() == owner.lower():
                print(f"   ✅ 签名验证成功！")
                return True
            else:
                print(f"   ❌ 签名验证失败！地址不匹配")
                return False
                
        except Exception as e:
            print(f"   ❌ 签名验证异常: {e}")
            return False
            
    except Exception as e:
        print(f"❌ 验证失败: {e}")
        return False

async def test_permit_call():
    """测试 permit 调用"""
    print(f"\n🔍 测试 permit 调用...")
    
    try:
        w3 = Web3(Web3.HTTPProvider(SEPOLIA_CONFIG["rpc_url"]))
        
        # 创建合约实例
        usdc_contract = w3.eth.contract(
            address=SEPOLIA_CONFIG["usdc_address"],
            abi=[{
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
            }]
        )
        
        # 测试参数
        owner = "0x5844b45b669dbaac536bcb7f660dcb7df1774d0c"
        spender = "0xd29427Eee41C6cB3BCb58F84820c62E8A9ab324b"
        value = 19998
        deadline = 1791456512
        v = 28
        r = "0x6d97bfdcaf0c01e886e0f2454c7c1be0d38261499293eac57aad65abe5ffa03b"
        s = "0x76d93637c8829520bbaa1987dadca8fc9efc630f596a5bdeaf6009b7567b1707"
        
        print(f"   测试参数:")
        print(f"     Owner: {owner}")
        print(f"     Spender: {spender}")
        print(f"     Value: {value}")
        print(f"     Deadline: {deadline}")
        print(f"     V: {v}")
        print(f"     R: {r}")
        print(f"     S: {s}")
        
        # 构建调用数据
        try:
            # 使用正确的 Web3.py 方法
            call_data = usdc_contract.functions.permit(
                owner,
                spender,
                value,
                deadline,
                v,
                bytes.fromhex(r[2:]) if r.startswith('0x') else bytes.fromhex(r),
                bytes.fromhex(s[2:]) if s.startswith('0x') else bytes.fromhex(s)
            ).build_transaction({
                'from': owner,
                'gas': 150000,
                'gasPrice': w3.eth.gas_price,
                'nonce': 0
            })
            
            print(f"   ✅ 调用数据构建成功")
            print(f"      Data: {call_data['data'][:100]}...")
            return True
            
        except Exception as e:
            print(f"   ❌ 调用数据构建失败: {e}")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

async def main():
    """主函数"""
    print("🚀 开始验证 Permit 签名...")
    print("=" * 60)
    
    # 验证签名
    signature_valid = await verify_permit_signature()
    
    # 测试 permit 调用
    call_valid = await test_permit_call()
    
    print("\n" + "=" * 60)
    if signature_valid and call_valid:
        print("✅ 所有验证通过！")
        print("📝 问题可能在于:")
        print("1. 后端钱包权限不足")
        print("2. 网络拥堵")
        print("3. Gas 费用问题")
    else:
        print("❌ 验证失败！")
        print("📝 问题在于:")
        if not signature_valid:
            print("1. Permit 签名验证失败")
        if not call_valid:
            print("2. Permit 调用参数错误")

if __name__ == "__main__":
    asyncio.run(main())
