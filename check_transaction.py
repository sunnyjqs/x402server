#!/usr/bin/env python3
"""
检查交易状态和错误详情
"""

import asyncio
import os
from dotenv import load_dotenv
from transfer_handler import create_sepolia_handler
from web3 import Web3

# 加载环境变量
load_dotenv()

async def check_transaction_status():
    """检查交易状态"""
    
    # 失败的交易哈希
    tx_hash = "0x84a9dec71095f16fafc4fa8e2f7104b486403e57a6533166e1759c666d9edeb8"
    
    print(f"🔍 检查交易状态: {tx_hash}")
    
    try:
        # 创建 Sepolia handler
        handler = create_sepolia_handler()
        
        # 获取交易收据
        receipt = handler.w3.eth.get_transaction_receipt(tx_hash)
        
        if receipt:
            print(f"✅ 交易收据获取成功")
            print(f"   - 区块号: {receipt.blockNumber}")
            print(f"   - Gas 使用: {receipt.gasUsed}")
            print(f"   - 状态: {'成功' if receipt.status == 1 else '失败'}")
            print(f"   - 合约地址: {receipt.to}")
            
            if receipt.status == 0:
                print(f"❌ 交易执行失败")
                
                # 获取交易详情
                tx = handler.w3.eth.get_transaction(tx_hash)
                if tx:
                    print(f"   - From: {tx['from']}")
                    print(f"   - To: {tx['to']}")
                    print(f"   - Gas Price: {tx['gasPrice']}")
                    print(f"   - Gas Limit: {tx['gas']}")
                    print(f"   - Nonce: {tx['nonce']}")
                    
                    # 尝试解码交易输入数据
                    try:
                        # 获取 USDC 合约 ABI
                        usdc_contract = handler.usdc_contract
                        
                        # 解码交易输入
                        decoded = usdc_contract.decode_function_input(tx['input'])
                        print(f"   - 函数名: {decoded[0].fn_name}")
                        print(f"   - 参数: {decoded[1]}")
                        
                    except Exception as decode_error:
                        print(f"   - 无法解码交易输入: {decode_error}")
                        
        else:
            print(f"❌ 交易收据不存在，可能还在 pending 状态")
            
            # 检查交易是否在 mempool 中
            try:
                tx = handler.w3.eth.get_transaction(tx_hash)
                if tx:
                    print(f"📝 交易在 mempool 中")
                    print(f"   - From: {tx['from']}")
                    print(f"   - To: {tx['to']}")
                    print(f"   - Gas Price: {tx['gasPrice']}")
                    print(f"   - Nonce: {tx['nonce']}")
                else:
                    print(f"❌ 交易不存在")
            except Exception as e:
                print(f"❌ 获取交易详情失败: {e}")
                
    except Exception as e:
        print(f"❌ 检查交易状态失败: {e}")

async def check_contract_state():
    """检查合约状态"""
    print(f"\n🔍 检查 USDC 合约状态...")
    
    try:
        handler = create_sepolia_handler()
        
        # 检查合约代码
        code = handler.w3.eth.get_code(handler.config["usdc_address"])
        if code == b'':
            print(f"❌ 合约地址 {handler.config['usdc_address']} 没有代码")
        else:
            print(f"✅ 合约地址 {handler.config['usdc_address']} 有代码")
            
        # 检查合约名称
        try:
            name = handler.usdc_contract.functions.name().call()
            symbol = handler.usdc_contract.functions.symbol().call()
            decimals = handler.usdc_contract.functions.decimals().call()
            
            print(f"   - 名称: {name}")
            print(f"   - 符号: {symbol}")
            print(f"   - 小数位: {decimals}")
            
        except Exception as e:
            print(f"   - 无法获取合约信息: {e}")
            
    except Exception as e:
        print(f"❌ 检查合约状态失败: {e}")

async def check_account_state():
    """检查账户状态"""
    print(f"\n🔍 检查账户状态...")
    
    try:
        handler = create_sepolia_handler()
        
        # 检查账户余额
        account_address = handler.account.address
        eth_balance = await handler.get_eth_balance(account_address)
        print(f"💰 账户 {account_address} ETH 余额: {eth_balance}")
        
        # 检查 nonce
        nonce = handler.w3.eth.get_transaction_count(account_address)
        print(f"🔢 账户 nonce: {nonce}")
        
        # 检查 gas 价格
        gas_price = handler.w3.eth.gas_price
        print(f"⛽ 当前 gas 价格: {gas_price} wei ({gas_price / 1e9:.2f} gwei)")
        
    except Exception as e:
        print(f"❌ 检查账户状态失败: {e}")

if __name__ == "__main__":
    print("🚀 开始交易诊断...")
    
    # 检查环境变量
    private_key = os.getenv("EXISTING_PRIVATE_KEY") or os.getenv("PRIVATE_KEY")
    if not private_key:
        print("❌ 未配置私钥环境变量")
        print("请设置 EXISTING_PRIVATE_KEY 或 PRIVATE_KEY")
        exit(1)
    
    print(f"🔑 私钥已配置: {private_key[:10]}...")
    
    # 运行诊断
    asyncio.run(check_transaction_status())
    asyncio.run(check_contract_state())
    asyncio.run(check_account_state())
    
    print("\n✅ 交易诊断完成!")

