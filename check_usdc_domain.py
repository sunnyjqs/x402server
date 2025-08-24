#!/usr/bin/env python3
"""
检查 USDC 合约的 EIP-712 域名配置
验证前端使用的域名是否与合约一致
"""

import asyncio
import os
from dotenv import load_dotenv
from web3 import Web3

# 加载环境变量
load_dotenv()

# 以太坊 Sepolia 配置
SEPOLIA_CONFIG = {
    "chain_id": 11155111,
    "rpc_url": "https://sepolia.infura.io/v3/9511773c563f4094b07478fb1706488b",
    "usdc_address": "0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238"
}

# 完整的 ERC20 + EIP-2612 ABI
USDC_ABI = [
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
        "name": "version",
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
        "inputs": [],
        "name": "DOMAIN_SEPARATOR",
        "outputs": [{"name": "", "type": "bytes32"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "PERMIT_TYPEHASH",
        "outputs": [{"name": "", "type": "bytes32"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [{"name": "owner", "type": "address"}],
        "name": "nonces",
        "outputs": [{"name": "", "type": "uint256"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    }
]

async def check_usdc_contract():
    """检查 USDC 合约配置"""
    print("🔍 检查以太坊 Sepolia USDC 合约...")
    print(f"📋 合约地址: {SEPOLIA_CONFIG['usdc_address']}")
    
    try:
        # 连接到网络
        w3 = Web3(Web3.HTTPProvider(SEPOLIA_CONFIG["rpc_url"]))
        
        if not w3.is_connected():
            print("❌ 无法连接到网络")
            return False
        
        print(f"✅ 已连接到以太坊 Sepolia")
        
        # 创建合约实例
        contract = w3.eth.contract(
            address=SEPOLIA_CONFIG["usdc_address"],
            abi=USDC_ABI
        )
        
        print(f"\n🔍 读取合约基本信息...")
        
        # 获取基本信息
        try:
            name = contract.functions.name().call()
            print(f"   Name: {name}")
        except Exception as e:
            print(f"   Name: 获取失败 ({e})")
            name = "Unknown"
        
        try:
            symbol = contract.functions.symbol().call()
            print(f"   Symbol: {symbol}")
        except Exception as e:
            print(f"   Symbol: 获取失败 ({e})")
            symbol = "Unknown"
        
        try:
            version = contract.functions.version().call()
            print(f"   Version: {version}")
        except Exception as e:
            print(f"   Version: 获取失败 ({e})")
            version = "Unknown"
        
        try:
            decimals = contract.functions.decimals().call()
            print(f"   Decimals: {decimals}")
        except Exception as e:
            print(f"   Decimals: 获取失败 ({e})")
        
        # 获取 EIP-712 相关信息
        print(f"\n🔍 读取 EIP-712 配置...")
        
        try:
            domain_separator = contract.functions.DOMAIN_SEPARATOR().call()
            print(f"   DOMAIN_SEPARATOR: {domain_separator.hex()}")
        except Exception as e:
            print(f"   DOMAIN_SEPARATOR: 获取失败 ({e})")
            domain_separator = None
        
        try:
            permit_typehash = contract.functions.PERMIT_TYPEHASH().call()
            print(f"   PERMIT_TYPEHASH: {permit_typehash.hex()}")
        except Exception as e:
            print(f"   PERMIT_TYPEHASH: 获取失败 ({e})")
            permit_typehash = None
        
        # 测试 nonces 函数
        print(f"\n🔍 测试 nonces 函数...")
        test_address = "0x5844b45b669dbaac536bcb7f660dcb7df1774d0c"  # 从日志中提取的地址
        try:
            nonce = contract.functions.nonces(test_address).call()
            print(f"   地址 {test_address} 的 nonce: {nonce}")
        except Exception as e:
            print(f"   Nonces 函数测试失败: {e}")
        
        # 计算期望的域名分隔符
        print(f"\n🔍 计算期望的域名分隔符...")
        
        # 使用前端的配置
        frontend_config = {
            "name": "USDC",
            "version": "1", 
            "chainId": 11155111,
            "verifyingContract": SEPOLIA_CONFIG["usdc_address"]
        }
        
        print(f"   前端使用的配置:")
        print(f"     Name: {frontend_config['name']}")
        print(f"     Version: {frontend_config['version']}")
        print(f"     ChainId: {frontend_config['chainId']}")
        print(f"     VerifyingContract: {frontend_config['verifyingContract']}")
        
        # 使用实际合约的配置
        actual_config = {
            "name": name,
            "version": version,
            "chainId": 11155111,
            "verifyingContract": SEPOLIA_CONFIG["usdc_address"]
        }
        
        print(f"\n   实际合约的配置:")
        print(f"     Name: {actual_config['name']}")
        print(f"     Version: {actual_config['version']}")
        print(f"     ChainId: {actual_config['chainId']}")
        print(f"     VerifyingContract: {actual_config['verifyingContract']}")
        
        # 比较配置
        print(f"\n🔍 配置对比:")
        config_match = True
        
        if frontend_config['name'] != actual_config['name']:
            print(f"   ❌ Name 不匹配: 前端='{frontend_config['name']}', 合约='{actual_config['name']}'")
            config_match = False
        else:
            print(f"   ✅ Name 匹配: '{actual_config['name']}'")
        
        if frontend_config['version'] != actual_config['version']:
            print(f"   ❌ Version 不匹配: 前端='{frontend_config['version']}', 合约='{actual_config['version']}'")
            config_match = False
        else:
            print(f"   ✅ Version 匹配: '{actual_config['version']}'")
        
        if frontend_config['chainId'] != actual_config['chainId']:
            print(f"   ❌ ChainId 不匹配: 前端={frontend_config['chainId']}, 合约={actual_config['chainId']}")
            config_match = False
        else:
            print(f"   ✅ ChainId 匹配: {actual_config['chainId']}")
        
        if frontend_config['verifyingContract'].lower() != actual_config['verifyingContract'].lower():
            print(f"   ❌ VerifyingContract 不匹配")
            config_match = False
        else:
            print(f"   ✅ VerifyingContract 匹配")
        
        if config_match:
            print(f"\n✅ 所有配置匹配！")
            return True
        else:
            print(f"\n❌ 配置不匹配！需要更新前端配置")
            return False
            
    except Exception as e:
        print(f"❌ 检查失败: {e}")
        return False

async def main():
    """主函数"""
    print("🚀 开始检查 USDC 合约配置...")
    print("=" * 60)
    
    success = await check_usdc_contract()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ 检查完成！")
        print("📝 如果配置匹配但签名仍然失败，请检查:")
        print("1. 签名参数的字节序和格式")
        print("2. v, r, s 参数的解析是否正确")
        print("3. 合约是否支持标准的 EIP-2612")
    else:
        print("❌ 发现配置问题！")
        print("📝 请根据上述输出更新前端配置")

if __name__ == "__main__":
    asyncio.run(main())
