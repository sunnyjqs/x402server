#!/usr/bin/env python3
"""
调试 Permit 错误
分析交易失败的具体原因
"""

import asyncio
import os
from dotenv import load_dotenv
from web3 import Web3
from eth_account import Account

# 加载环境变量
load_dotenv()

# 以太坊 Sepolia 配置
SEPOLIA_CONFIG = {
    "chain_id": 11155111,
    "rpc_url": "https://sepolia.infura.io/v3/9511773c563f4094b07478fb1706488b",
    "usdc_address": "0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238"
}

async def debug_transaction():
    """调试失败的交易"""
    print("🔍 调试失败的 Permit 交易...")
    
    # 失败的交易哈希
    failed_tx_hash = "50d781a3e6109aabf49b65d0f5ae6946bf4290c4bb9bbaf467c8fb5caea408a7"
    
    try:
        # 连接到网络
        w3 = Web3(Web3.HTTPProvider(SEPOLIA_CONFIG["rpc_url"]))
        
        if not w3.is_connected():
            print("❌ 无法连接到网络")
            return
        
        print(f"✅ 已连接到以太坊 Sepolia")
        
        # 获取交易详情
        print(f"\n📋 获取交易详情: {failed_tx_hash}")
        tx = w3.eth.get_transaction(failed_tx_hash)
        
        if tx:
            print(f"✅ 交易存在")
            print(f"   From: {tx.get('from', 'N/A')}")
            print(f"   To: {tx.get('to', 'N/A')}")
            print(f"   Gas: {tx.get('gas', 'N/A')}")
            print(f"   Gas Price: {tx.get('gasPrice', 'N/A')} wei")
            print(f"   Nonce: {tx.get('nonce', 'N/A')}")
            print(f"   Value: {tx.get('value', 'N/A')} wei")
            if 'data' in tx and tx['data']:
                print(f"   Data: {tx['data'][:100]}...")
            else:
                print(f"   Data: None")
            
            # 解析交易数据
            if 'data' in tx and tx['data'] and tx['data'] != b'0x':
                print(f"\n🔍 解析交易数据...")
                
                # 检查是否是 permit 调用
                if tx['data'].startswith(b'0xd505accf'):  # permit function selector
                    print(f"✅ 确认是 permit 函数调用")
                    
                    # 解析参数
                    try:
                        # 移除函数选择器，解析剩余数据
                        params_data = tx['data'][4:]  # 移除 4 字节的选择器
                        
                        # permit 函数有 7 个参数，每个 32 字节
                        if len(params_data) >= 7 * 32:
                            owner = '0x' + params_data[0:32].hex()[-40:]  # 最后20字节是地址
                            spender = '0x' + params_data[32:64].hex()[-40:]
                            value = int.from_bytes(params_data[64:96], 'big')
                            deadline = int.from_bytes(params_data[96:128], 'big')
                            v = int.from_bytes(params_data[128:160], 'big')
                            r = '0x' + params_data[160:192].hex()
                            s = '0x' + params_data[192:224].hex()
                            
                            print(f"📝 Permit 参数:")
                            print(f"   Owner: {owner}")
                            print(f"   Spender: {spender}")
                            print(f"   Value: {value} (wei) = {value/1e6} USDC")
                            print(f"   Deadline: {deadline} ({deadline - int(time.time())} 秒后过期)")
                            print(f"   V: {v}")
                            print(f"   R: {r}")
                            print(f"   S: {s}")
                            
                            # 检查参数合理性
                            current_time = int(time.time())
                            if deadline < current_time:
                                print(f"❌ Deadline 已过期！当前时间: {current_time}, Deadline: {deadline}")
                            else:
                                print(f"✅ Deadline 有效")
                                
                        else:
                            print(f"⚠️  参数数据长度不足: {len(params_data)} bytes")
                            
                    except Exception as e:
                        print(f"❌ 参数解析失败: {e}")
                else:
                    print(f"⚠️  不是 permit 函数调用，选择器: {tx['data'][:4].hex()}")
            else:
                print(f"⚠️  交易没有数据")
        else:
            print(f"❌ 交易不存在")
        
        # 获取交易收据
        print(f"\n📋 获取交易收据...")
        receipt = w3.eth.get_transaction_receipt(failed_tx_hash)
        
        if receipt:
            print(f"✅ 收据存在")
            print(f"   Status: {'成功' if receipt['status'] == 1 else '失败'}")
            print(f"   Block Number: {receipt['blockNumber']}")
            print(f"   Gas Used: {receipt['gasUsed']}")
            print(f"   Cumulative Gas Used: {receipt['cumulativeGasUsed']}")
            
            if receipt['status'] == 0:
                print(f"❌ 交易执行失败")
                
                # 尝试获取失败原因
                try:
                    # 获取交易失败的详细信息
                    trace = w3.provider.make_request('debug_traceTransaction', [failed_tx_hash])
                    if trace and 'result' in trace:
                        print(f"🔍 交易追踪信息: {trace['result']}")
                except Exception as e:
                    print(f"⚠️  无法获取交易追踪: {e}")
                    
                    # 尝试从区块获取日志
                    try:
                        logs = w3.eth.get_logs({
                            'fromBlock': receipt['blockNumber'],
                            'toBlock': receipt['blockNumber'],
                            'topics': [None, None, None]
                        })
                        
                        if logs:
                            print(f"📝 区块日志:")
                            for log in logs:
                                print(f"   Log: {log}")
                        else:
                            print(f"📝 无区块日志")
                    except Exception as e:
                        print(f"⚠️  无法获取区块日志: {e}")
        else:
            print(f"❌ 收据不存在")
            
    except Exception as e:
        print(f"❌ 调试失败: {e}")

async def main():
    """主函数"""
    print("🚀 开始调试 Permit 交易失败...")
    print("=" * 60)
    
    await debug_transaction()
    
    print("\n" + "=" * 60)
    print("📝 建议检查:")
    print("1. 前端生成的签名参数是否正确")
    print("2. 签名是否在正确的网络上生成")
    print("3. 参数格式是否匹配合约要求")
    print("4. 后端钱包是否有足够的 ETH 支付 gas")

if __name__ == "__main__":
    import time
    asyncio.run(main())
