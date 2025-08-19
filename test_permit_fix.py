#!/usr/bin/env python3
"""
测试修复后的 permit 功能
"""

import asyncio
import os
from dotenv import load_dotenv
from transfer_handler import create_sepolia_handler

# 加载环境变量
load_dotenv()

async def test_permit_functionality():
    """测试 permit 功能"""
    print("🧪 测试修复后的 permit 功能...")
    
    try:
        # 创建 Sepolia handler
        handler = create_sepolia_handler()
        print(f"✅ Sepolia handler 创建成功")
        
        # 测试合约基本信息
        print("\n🔍 测试合约基本信息...")
        try:
            name = handler.usdc_contract.functions.name().call()
            symbol = handler.usdc_contract.functions.symbol().call()
            decimals = handler.usdc_contract.functions.decimals().call()
            
            print(f"✅ 合约信息获取成功:")
            print(f"   - 名称: {name}")
            print(f"   - 符号: {symbol}")
            print(f"   - 小数位: {decimals}")
            
        except Exception as e:
            print(f"❌ 合约信息获取失败: {e}")
            return
        
        # 测试 permit 函数
        print("\n🔍 测试 permit 函数...")
        try:
            # 检查 permit 函数是否存在
            permit_function = handler.usdc_contract.functions.permit
            print(f"✅ Permit 函数存在: {permit_function}")
            
            # 获取函数签名
            permit_signature = permit_function.signature
            print(f"✅ Permit 函数签名: {permit_signature}")
            
        except Exception as e:
            print(f"❌ Permit 函数测试失败: {e}")
            return
        
        # 测试余额查询
        print("\n🔍 测试余额查询...")
        try:
            test_address = "0x56D5A65DADC54145060F213a39B610D4DcF5DeB3"
            balance = handler.usdc_contract.functions.balanceOf(test_address).call()
            print(f"✅ 余额查询成功: {test_address} = {balance} wei ({balance / 1e6:.6f} USDC)")
            
        except Exception as e:
            print(f"❌ 余额查询失败: {e}")
        
        # 测试账户状态
        print("\n🔍 测试账户状态...")
        try:
            account_address = handler.account.address
            eth_balance = await handler.get_eth_balance(account_address)
            nonce = handler.w3.eth.get_transaction_count(account_address)
            gas_price = handler.w3.eth.gas_price
            
            print(f"✅ 账户状态获取成功:")
            print(f"   - 地址: {account_address}")
            print(f"   - ETH 余额: {eth_balance} ETH")
            print(f"   - Nonce: {nonce}")
            print(f"   - Gas 价格: {gas_price} wei ({gas_price / 1e9:.2f} gwei)")
            
        except Exception as e:
            print(f"❌ 账户状态获取失败: {e}")
        
        print("\n✅ Permit 功能测试完成!")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")

async def test_permit_transaction_building():
    """测试 permit 交易构建"""
    print("\n🔧 测试 permit 交易构建...")
    
    try:
        handler = create_sepolia_handler()
        
        # 测试参数
        owner = "0x579e306afe2f8030ac299df6c81d32e0eb67e482"
        spender = "0x56D5A65DADC54145060F213a39B610D4DcF5DeB3"
        value = "20000"  # 0.02 USDC
        deadline = 1791321616
        v = 27
        r = "0x289cfd68274ca1e039b4610b2dd809d6984f62dbecf8bf146cd4853098adc4e3"
        s = "0x2c8091e888b6a777af64f9626149ae4b0356aad6f6a593c8fa3ee000dcfddcb5"
        
        print(f"📋 测试参数:")
        print(f"   - Owner: {owner}")
        print(f"   - Spender: {spender}")
        print(f"   - Value: {value}")
        print(f"   - Deadline: {deadline}")
        
        # 转换地址格式
        owner_checksum = handler.w3.to_checksum_address(owner)
        spender_checksum = handler.w3.to_checksum_address(spender)
        
        print(f"✅ 地址格式转换成功:")
        print(f"   - Owner (checksum): {owner_checksum}")
        print(f"   - Spender (checksum): {spender_checksum}")
        
        # 获取 nonce
        nonce = handler.w3.eth.get_transaction_count(handler.account.address)
        print(f"✅ Nonce 获取成功: {nonce}")
        
        # 构建 permit 交易
        try:
            permit_txn = handler.usdc_contract.functions.permit(
                owner_checksum,
                spender_checksum,
                int(value),
                deadline,
                v,
                bytes.fromhex(r[2:]) if r.startswith('0x') else bytes.fromhex(r),
                bytes.fromhex(s[2:]) if s.startswith('0x') else bytes.fromhex(s)
            ).build_transaction({
                'from': handler.account.address,
                'gas': 150000,
                'gasPrice': handler.w3.eth.gas_price,
                'nonce': nonce
            })
            
            print(f"✅ Permit 交易构建成功:")
            print(f"   - Gas Limit: {permit_txn['gas']}")
            print(f"   - Gas Price: {permit_txn['gasPrice']}")
            print(f"   - Nonce: {permit_txn['nonce']}")
            print(f"   - To: {permit_txn['to']}")
            
            # 估算 gas 费用
            estimated_gas = handler.usdc_contract.functions.permit(
                owner_checksum,
                spender_checksum,
                int(value),
                deadline,
                v,
                bytes.fromhex(r[2:]) if r.startswith('0x') else bytes.fromhex(r),
                bytes.fromhex(s[2:]) if s.startswith('0x') else bytes.fromhex(s)
            ).estimate_gas({
                'from': handler.account.address
            })
            
            print(f"✅ Gas 估算成功: {estimated_gas}")
            
            # 计算总费用
            total_cost = estimated_gas * handler.w3.eth.gas_price
            total_cost_eth = total_cost / 1e18
            print(f"💰 预估总费用: {total_cost} wei ({total_cost_eth:.6f} ETH)")
            
        except Exception as e:
            print(f"❌ Permit 交易构建失败: {e}")
            return
        
        print("\n✅ Permit 交易构建测试完成!")
        
    except Exception as e:
        print(f"❌ 交易构建测试失败: {e}")

if __name__ == "__main__":
    print("🚀 开始 permit 功能测试...")
    
    # 检查环境变量
    private_key = os.getenv("EXISTING_PRIVATE_KEY") or os.getenv("PRIVATE_KEY")
    if not private_key:
        print("❌ 未配置私钥环境变量")
        print("请设置 EXISTING_PRIVATE_KEY 或 PRIVATE_KEY")
        exit(1)
    
    print(f"🔑 私钥已配置: {private_key[:10]}...")
    
    # 运行测试
    asyncio.run(test_permit_functionality())
    asyncio.run(test_permit_transaction_building())
    
    print("\n✅ 所有测试完成!")

