import os
from web3 import Web3
from eth_account import Account
from dotenv import load_dotenv
import asyncio
from typing import Dict, Any

# 加载环境变量
load_dotenv()

# Base 网络 USDC 配置
BASE_USDC_CONFIG = {
    "chain_id": 8453,  # Base mainnet
    "rpc_url": "https://mainnet.base.org",
    "usdc_address": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",  # Base USDC
    "usdc_abi": [
        {
            "constant": False,
            "inputs": [
                {"name": "from", "type": "address"},
                {"name": "to", "type": "address"},
                {"name": "value", "type": "uint256"}
            ],
            "name": "transferFrom",
            "outputs": [{"name": "", "type": "bool"}],
            "payable": False,
            "stateMutability": "nonpayable",
            "type": "function"
        },
        {
            "constant": True,
            "inputs": [{"name": "account", "type": "address"}],
            "name": "balanceOf",
            "outputs": [{"name": "", "type": "uint256"}],
            "payable": False,
            "stateMutability": "view",
            "type": "function"
        },
        {
            "constant": True,
            "inputs": [
                {"name": "owner", "type": "address"},
                {"name": "spender", "type": "address"}
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
}

# 以太坊 Sepolia 测试网 USDC 配置
SEPOLIA_USDC_CONFIG = {
    "chain_id": 11155111,  # 以太坊 Sepolia testnet
    "rpc_url": "https://sepolia.infura.io/v3/9511773c563f4094b07478fb1706488b",  # 使用 Alchemy 的免费节点
    "usdc_address": "0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238",  # 以太坊 Sepolia USDC
    "usdc_abi": [
        # 基本 ERC20 函数
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
        },
        # EIP-2612 Permit 函数
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
}

def create_sepolia_handler():
    """创建 Sepolia 测试网的 TransferHandler 实例"""
    return TransferHandler(use_sepolia=True)

class TransferHandler:
    def __init__(self, use_sepolia=False):
        self.private_key = os.getenv("EXISTING_PRIVATE_KEY") or os.getenv("PRIVATE_KEY")
        if not self.private_key:
            raise ValueError("EXISTING_PRIVATE_KEY not configured")
        
        if not self.private_key.startswith("0x"):
            self.private_key = f"0x{self.private_key}"
        
        self.account = Account.from_key(self.private_key)
        
        # 根据参数选择网络配置
        if use_sepolia:
            self.config = SEPOLIA_USDC_CONFIG
            print(f"🔗 连接到以太坊 Sepolia 测试网: {self.config['rpc_url']}")
        else:
            self.config = BASE_USDC_CONFIG
            print(f"🔗 连接到 Base 主网: {self.config['rpc_url']}")
        
        self.w3 = Web3(Web3.HTTPProvider(self.config["rpc_url"]))
        
        # 检查网络连接
        if not self.w3.is_connected():
            raise ConnectionError(f"Failed to connect to {self.config['rpc_url']}")
        
        # 创建 USDC 合约实例
        self.usdc_contract = self.w3.eth.contract(
            address=self.config["usdc_address"],
            abi=self.config["usdc_abi"]
        )
    
    async def execute_transfer_from(
        self, 
        owner_address: str, 
        amount: str = "10000"  # 0.05 USDC (6位小数)
    ) -> Dict[str, Any]:
        """
        执行 transferFrom 调用，从 owner 地址转移 USDC 到当前账户
        
        Args:
            owner_address: 授权给你的地址
            amount: 转移金额（6位小数）
        
        Returns:
            包含交易结果的字典
        """
        try:
            # 0. 转换地址格式为 checksum 地址
            owner_address_checksum = Web3.to_checksum_address(owner_address)
            
            # 1. 检查授权额度
            allowance = self.usdc_contract.functions.allowance(
                owner_address_checksum, 
                self.account.address
            ).call()
            
            if allowance < int(amount):
                return {
                    "success": False,
                    "error": f"Insufficient allowance. Required: {int(amount)}, Available: {allowance}"
                }
            
            # 2. 获取当前 nonce
            nonce = self.w3.eth.get_transaction_count(self.account.address)
            
            # 3. 构建 transferFrom 交易
            transfer_txn = self.usdc_contract.functions.transferFrom(
                owner_address_checksum,      # from (owner)
                self.account.address,  # to (spender - 你的 CDP 子账号)
                int(amount)         # amount
            ).build_transaction({
                'from': self.account.address,
                'gas': 100000,
                'gasPrice': self.w3.eth.gas_price,
                'nonce': nonce
            })
            
            # 4. 签名并发送交易
            signed_txn = self.account.sign_transaction(transfer_txn)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.raw_transaction)
            
            # 5. 等待交易确认
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if receipt.status == 1:
                # 6. 检查最终余额
                final_balance = self.usdc_contract.functions.balanceOf(self.account.address).call()
                return {
                    "success": True,
                    "tx_hash": tx_hash.hex(),
                    "final_balance": final_balance,
                    "final_balance_usdc": final_balance / 1000000,
                    "amount_transferred": int(amount) / 1000000,
                    "message": f"Successfully transferred {int(amount) / 1000000} USDC"
                }
            else:
                return {
                    "success": False,
                    "error": f"Transaction failed: {tx_hash.hex()}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to execute transferFrom"
            }
    
    async def check_usdc_balance(self) -> Dict[str, Any]:
        """检查当前地址的 USDC 余额"""
        try:
            balance = self.usdc_contract.functions.balanceOf(self.account.address).call()
            return {
                "success": True,
                "balance": balance,
                "balance_usdc": balance / 1000000,
                "address": self.account.address
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to check USDC balance"
            }
    
    async def check_allowance(self, owner_address: str) -> Dict[str, Any]:
        """检查授权额度"""
        try:
            # 转换地址格式为 checksum 地址
            owner_address_checksum = Web3.to_checksum_address(owner_address)
            allowance = self.usdc_contract.functions.allowance(
                owner_address_checksum, 
                self.account.address
            ).call()
            return {
                "success": True,
                "allowance": allowance,
                "allowance_usdc": allowance / 1000000,
                "owner": owner_address_checksum,
                "spender": self.account.address
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to check allowance"
            }

    async def get_eth_balance(self, address: str) -> float:
        """获取指定地址的 ETH 余额"""
        try:
            balance_wei = self.w3.eth.get_balance(address)
            balance_eth = self.w3.from_wei(balance_wei, 'ether')
            return float(balance_eth)
        except Exception as e:
            print(f"❌ 获取 ETH 余额失败: {e}")
            return 0.0

    async def execute_permit(
        self, 
        owner: str, 
        spender: str, 
        value: str, 
        deadline: int, 
        v: int, 
        r: str, 
        s: str,
        network: str = "mainnet"  # 新增：网络参数
    ) -> Dict[str, Any]:
        """
        执行 EIP-2612 permit 授权
        
        Args:
            owner: 代币持有者地址
            spender: 被授权地址
            value: 授权金额（6位小数）
            deadline: 过期时间戳
            v, r, s: 签名参数
        
        Returns:
            包含执行结果的字典
        """
        try:
            print(f"🔄 执行 EIP-2612 permit 授权 (Web3)...")
            print(f"Owner: {owner}")
            print(f"Spender: {spender}")
            print(f"Value: {value}")
            print(f"Deadline: {deadline}")
            
            # 检查 spender 地址的 ETH 余额
            spender_eth_balance = await self.get_eth_balance(spender)
            print(f"💰 Spender ETH 余额: {spender_eth_balance} ETH")
            
            # 转换地址格式为 checksum 地址
            owner_checksum = Web3.to_checksum_address(owner)
            spender_checksum = Web3.to_checksum_address(spender)
            
            # 获取当前 nonce
            nonce = self.w3.eth.get_transaction_count(self.account.address)
            
            # 构建 permit 交易
            print(f"🔍 构建 permit 交易...")
            print(f"   USDC 合约地址: {self.config['usdc_address']}")
            print(f"   USDC 合约实例: {self.usdc_contract}")
            print(f"   Permit 函数: {self.usdc_contract.functions.permit}")
            
            # 检查合约是否有 permit 函数
            if not hasattr(self.usdc_contract.functions, 'permit'):
                raise ValueError("USDC 合约没有 permit 函数")
            
            permit_txn = self.usdc_contract.functions.permit(
                owner_checksum,
                spender_checksum,
                int(value),
                deadline,
                v,
                bytes.fromhex(r[2:]) if r.startswith('0x') else bytes.fromhex(r),  # 移除 0x 前缀
                bytes.fromhex(s[2:]) if s.startswith('0x') else bytes.fromhex(s)   # 移除 0x 前缀
            ).build_transaction({
                'from': self.account.address,
                'gas': 150000,
                'gasPrice': self.w3.eth.gas_price,
                'nonce': nonce
            })
            
            print(f"✅ Permit 交易构建成功")
            print(f"   To: {permit_txn['to']}")
            print(f"   Data: {permit_txn['data'][:100]}...")
            print(f"   Gas: {permit_txn['gas']}")
            print(f"   Nonce: {permit_txn['nonce']}")
            
            # 签名并发送交易
            signed_txn = self.account.sign_transaction(permit_txn)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.raw_transaction)
            
            # 等待交易确认
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if receipt.status == 1:
                return {
                    "success": True,
                    "method": "web3",
                    "tx_hash": tx_hash.hex(),
                    "message": f"Web3 permit 授权成功: {int(value) / 1000000} USDC",
                    "details": {
                        "owner": owner_checksum,
                        "spender": spender_checksum,
                        "value": int(value),
                        "deadline": deadline,
                        "gas_used": receipt.gasUsed,
                        "block_number": receipt.blockNumber
                    }
                }
            else:
                return {
                    "success": False,
                    "error": f"Transaction failed: {tx_hash.hex()}",
                    "message": "Permit transaction failed"
                }
                
        except Exception as e:
            print(f"❌ Web3 permit 执行失败: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "Web3 permit execution failed"
            }

# 全局实例
transfer_handler = None

def get_transfer_handler():
    """获取 TransferHandler 实例"""
    global transfer_handler
    if transfer_handler is None:
        try:
            transfer_handler = TransferHandler()
        except Exception as e:
            print(f"Failed to initialize TransferHandler: {e}")
            return None
    return transfer_handler
