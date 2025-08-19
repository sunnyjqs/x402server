#!/usr/bin/env python3
"""
验证 Sepolia 测试网 USDC 合约
"""

import asyncio
import os
from dotenv import load_dotenv
from web3 import Web3
import json

# 加载环境变量
load_dotenv()

# Sepolia 测试网配置
SEPOLIA_CONFIG = {
    "rpc_url": "https://sepolia.base.org",
    "usdc_address": "0x036CbD53842c5426634e7929541eC2318f3dCF7e"
}

# 最小化的 ERC20 ABI（只包含必要的函数）
MINIMAL_ERC20_ABI = [
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
        "name": "decimals",
        "outputs": [{"name": "", "type": "uint8"}],
        "payable": False,
        "stateMutability": "view",
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
        "inputs": [
            {"name": "_owner", "type": "address"},
            {"name": "_spender", "type": "address"}
        ],
        "name": "allowance",
        "outputs": [{"name": "", "type": "uint256"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": False,
        "inputs": [
            {"name": "_spender", "type": "address"},
            {"name": "_value", "type": "uint256"}
        ],
        "name": "approve",
        "outputs": [{"name": "", "type": "bool"}],
        "payable": False,
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "constant": False,
        "inputs": [
            {"name": "_to", "type": "address"},
            {"name": "_value", "type": "uint256"}
        ],
        "name": "transfer",
        "outputs": [{"name": "", "type": "bool"}],
        "payable": False,
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "constant": False,
        "inputs": [
            {"name": "_from", "type": "address"},
            {"name": "_to", "type": "address"},
            {"name": "_value", "type": "uint256"}
        ],
        "name": "transferFrom",
        "outputs": [{"name": "", "type": "bool"}],
        "payable": False,
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

# EIP-2612 Permit ABI
PERMIT_ABI = [
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
    }
]

async def verify_sepolia_usdc():
    """验证 Sepolia 测试网 USDC 合约"""
    print("🔍 验证 Sepolia 测试网 USDC 合约...")
    
    try:
        # 连接到 Sepolia 测试网
        w3 = Web3(Web3.HTTPProvider(SEPOLIA_CONFIG["rpc_url"]))
        
        if not w3.is_connected():
            print("❌ 无法连接到 Sepolia 测试网")
            return
        
        print(f"✅ 已连接到 Sepolia 测试网: {SEPOLIA_CONFIG['rpc_url']}")
        
        # 检查合约地址
        contract_address = SEPOLIA_CONFIG["usdc_address"]
        print(f"📋 检查合约地址: {contract_address}")
        
        # 检查合约代码
        code = w3.eth.get_code(contract_address)
        if code == b'':
            print("❌ 合约地址没有代码")
            return
        
        print(f"✅ 合约地址有代码，长度: {len(code)} bytes")
        
        # 尝试使用最小化 ABI 创建合约实例
        print("\n🔧 测试最小化 ERC20 ABI...")
        try:
            contract = w3.eth.contract(
                address=contract_address,
                abi=MINIMAL_ERC20_ABI
            )
            
            # 测试基本函数
            name = contract.functions.name().call()
            symbol = contract.functions.symbol().call()
            decimals = contract.functions.decimals().call()
            
            print(f"✅ 基本 ERC20 函数正常:")
            print(f"   - 名称: {name}")
            print(f"   - 符号: {symbol}")
            print(f"   - 小数位: {decimals}")
            
        except Exception as e:
            print(f"❌ 基本 ERC20 函数失败: {e}")
            return
        
        # 测试 Permit 函数
        print("\n🔧 测试 EIP-2612 Permit 函数...")
        try:
            permit_contract = w3.eth.contract(
                address=contract_address,
                abi=MINIMAL_ERC20_ABI + PERMIT_ABI
            )
            
            # 检查 permit 函数是否存在
            permit_function = permit_contract.functions.permit
            print(f"✅ Permit 函数存在: {permit_function}")
            
            # 获取函数选择器
            permit_selector = permit_contract.encodeABI(
                fn_name='permit',
                args=['0x' + '0' * 40, '0x' + '0' * 40, 0, 0, 0, '0x' + '0' * 64, '0x' + '0' * 64]
            )
            print(f"✅ Permit 函数选择器: {permit_selector[:10]}...")
            
        except Exception as e:
            print(f"❌ Permit 函数测试失败: {e}")
            return
        
        # 测试余额查询
        print("\n🔧 测试余额查询...")
        try:
            test_address = "0x56D5A65DADC54145060F213a39B610D4DcF5DeB3"
            balance = contract.functions.balanceOf(test_address).call()
            print(f"✅ 余额查询正常: {test_address} = {balance} wei")
            
        except Exception as e:
            print(f"❌ 余额查询失败: {e}")
        
        print("\n✅ Sepolia USDC 合约验证完成!")
        
        # 建议新的配置
        print("\n📝 建议的配置更新:")
        print("SEPOLIA_USDC_CONFIG = {")
        print(f'    "chain_id": 84532,')
        print(f'    "rpc_url": "{SEPOLIA_CONFIG["rpc_url"]}",')
        print(f'    "usdc_address": "{contract_address}",')
        print(f'    "usdc_abi": MINIMAL_ERC20_ABI + PERMIT_ABI')
        print("}")
        
    except Exception as e:
        print(f"❌ 验证失败: {e}")

async def test_alternative_usdc_addresses():
    """测试其他可能的 USDC 地址"""
    print("\n🔍 测试其他可能的 USDC 地址...")
    
    # 常见的 Base Sepolia USDC 地址
    possible_addresses = [
        "0x036CbD53842c5426634e7929541eC2318f3dCF7e",  # 当前使用的
        "0x4200000000000000000000000000000000000006",  # WETH
        "0x4200000000000000000000000000000000000007",  # 可能的 USDC
        "0x4200000000000000000000000000000000000008",  # 可能的 USDC
    ]
    
    try:
        w3 = Web3(Web3.HTTPProvider(SEPOLIA_CONFIG["rpc_url"]))
        
        for addr in possible_addresses:
            try:
                code = w3.eth.get_code(addr)
                if code != b'':
                    print(f"📍 {addr}: 有代码 ({len(code)} bytes)")
                    
                    # 尝试创建合约实例
                    contract = w3.eth.contract(
                        address=addr,
                        abi=MINIMAL_ERC20_ABI
                    )
                    
                    try:
                        name = contract.functions.name().call()
                        symbol = contract.functions.symbol().call()
                        print(f"   - 名称: {name}")
                        print(f"   - 符号: {symbol}")
                        
                        if "USDC" in name.upper() or "USDC" in symbol.upper():
                            print(f"   🎯 这可能是 USDC 合约!")
                            
                    except Exception:
                        print(f"   - 无法获取名称/符号")
                        
                else:
                    print(f"📍 {addr}: 无代码")
                    
            except Exception as e:
                print(f"📍 {addr}: 检查失败 - {e}")
                
    except Exception as e:
        print(f"❌ 测试其他地址失败: {e}")

if __name__ == "__main__":
    print("🚀 开始 Sepolia USDC 合约验证...")
    
    asyncio.run(verify_sepolia_usdc())
    asyncio.run(test_alternative_usdc_addresses())
    
    print("\n✅ 验证完成!")

