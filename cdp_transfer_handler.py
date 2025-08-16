import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv
import asyncio

# 加载环境变量
load_dotenv()

try:
    from cdp_sdk import CdpClient
    CDP_AVAILABLE = True
except ImportError:
    try:
        from cdp import CdpClient
        CDP_AVAILABLE = True
    except ImportError:
        CDP_AVAILABLE = False

class CdpTransferHandler:
    """使用 CDP 原生 API 的 USDC 转移处理器"""
    
    def __init__(self):
        if not CDP_AVAILABLE:
            raise ImportError("CDP SDK not available")
        
        self.cdp = CdpClient()
        self.api_key_id = os.getenv("CDP_API_KEY_ID")
        self.api_key_secret = os.getenv("CDP_API_KEY_SECRET")
        self.wallet_secret = os.getenv("CDP_WALLET_SECRET")
        
        if not all([self.api_key_id, self.api_key_secret, self.wallet_secret]):
            raise ValueError("CDP credentials not configured")
    
    async def execute_transfer_from(
        self, 
        owner_address: str, 
        amount: str = "10000"  # 0.05 USDC (6位小数)
    ) -> Dict[str, Any]:
        """
        使用 CDP 原生 API 执行 USDC 转移
        
        Args:
            owner_address: 授权地址
            amount: 转移金额（6位小数）
        
        Returns:
            包含转移结果的字典
        """
        try:
            print(f"🔄 尝试使用 CDP 原生 API 转移 {int(amount) / 1000000} USDC...")
            
            # 方法 1：尝试使用 CDP 的 USDC 转移 API
            try:
                # 这里需要根据实际的 CDP API 文档来调用
                # 示例：可能是这样的调用方式
                transfer_result = await self.cdp.evm.transfer_usdc(
                    from_address=owner_address,
                    to_address=await self._get_cdp_account_address(),
                    amount=int(amount),
                    use_permit=True  # 使用 permit 授权
                )
                
                return {
                    "success": True,
                    "method": "cdp_native",
                    "tx_hash": getattr(transfer_result, 'tx_hash', 'N/A'),
                    "message": f"CDP 原生 API 转移成功: {int(amount) / 1000000} USDC",
                    "cdp_response": transfer_result
                }
                
            except Exception as cdp_error:
                print(f"⚠️ CDP 原生 API 失败: {cdp_error}")
                
                # 方法 2：尝试使用 CDP 的 permit + transfer 组合
                try:
                    print("🔄 尝试 CDP permit + transfer 组合...")
                    
                    # 先调用 permit
                    permit_result = await self.cdp.evm.execute_permit(
                        token_address="0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",  # Base USDC
                        owner=owner_address,
                        spender=await self._get_cdp_account_address(),
                        value=int(amount),
                        deadline=int(asyncio.get_event_loop().time()) + 3600
                    )
                    
                    # 再执行 transfer
                    transfer_result = await self.cdp.evm.transfer_from(
                        token_address="0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
                        from_address=owner_address,
                        to_address=await self._get_cdp_account_address(),
                        amount=int(amount)
                    )
                    
                    return {
                        "success": True,
                        "method": "cdp_permit_transfer",
                        "tx_hash": getattr(transfer_result, 'tx_hash', 'N/A'),
                        "message": f"CDP permit + transfer 成功: {int(amount) / 1000000} USDC",
                        "permit_result": permit_result,
                        "transfer_result": transfer_result
                    }
                    
                except Exception as permit_error:
                    print(f"⚠️ CDP permit + transfer 失败: {permit_error}")
                    
                    # 方法 3：fallback 到 Web3 的 transferFrom
                    print("🔄 回退到 Web3 transferFrom...")
                    return await self._fallback_to_web3(owner_address, amount)
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "CDP 转移失败"
            }
    
    async def _get_cdp_account_address(self) -> str:
        """获取当前 CDP 账户地址"""
        try:
            # 从环境变量获取私钥
            private_key = os.getenv("EXISTING_PRIVATE_KEY") or os.getenv("PRIVATE_KEY")
            if not private_key:
                raise ValueError("Private key not configured")
            
            if not private_key.startswith("0x"):
                private_key = f"0x{private_key}"
            
            # 导入账户到 CDP
            imported = await self.cdp.evm.import_account(private_key=private_key)
            address = getattr(imported, "address", None)
            if address is None and isinstance(imported, dict):
                address = imported.get("address") or imported.get("Address")
            
            return address
            
        except Exception as e:
            raise ValueError(f"Failed to get CDP account address: {e}")
    
    async def _fallback_to_web3(self, owner_address: str, amount: str) -> Dict[str, Any]:
        """回退到 Web3 的 transferFrom 实现"""
        try:
            from transfer_handler import get_transfer_handler
            
            handler = get_transfer_handler()
            if handler:
                return await handler.execute_transfer_from(owner_address, amount)
            else:
                return {
                    "success": False,
                    "error": "Web3 fallback not available",
                    "message": "No transfer method available"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Web3 fallback failed"
            }
    
    async def check_usdc_balance(self) -> Dict[str, Any]:
        """检查 USDC 余额（通过 CDP API）"""
        try:
            account_address = await self._get_cdp_account_address()
            
            # 尝试使用 CDP 的余额查询 API
            try:
                balance = await self.cdp.evm.get_token_balance(
                    address=account_address,
                    token_address="0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"  # Base USDC
                )
                
                return {
                    "success": True,
                    "method": "cdp_native",
                    "balance": balance,
                    "balance_usdc": balance / 1000000,
                    "address": account_address
                }
                
            except Exception:
                # 回退到 Web3
                return await self._fallback_balance_check(account_address)
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to check USDC balance"
            }
    
    async def _fallback_balance_check(self, account_address: str) -> Dict[str, Any]:
        """回退到 Web3 的余额查询"""
        try:
            from transfer_handler import get_transfer_handler
            
            handler = get_transfer_handler()
            if handler:
                return await handler.check_usdc_balance()
            else:
                return {
                    "success": False,
                    "error": "Web3 fallback not available",
                    "message": "No balance check method available"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Web3 fallback failed"
            }

    async def execute_permit(
        self, 
        owner: str, 
        spender: str, 
        value: str, 
        deadline: int, 
        v: int, 
        r: str, 
        s: str
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
            print(f"🔄 执行 EIP-2612 permit 授权...")
            print(f"Owner: {owner}")
            print(f"Spender: {spender}")
            print(f"Value: {value}")
            print(f"Deadline: {deadline}")
            
            # 方法 1：尝试使用 CDP 的 permit API
            try:
                print("🔄 尝试使用 CDP permit API...")
                
                # 调用 CDP 的 permit 执行 API
                permit_result = await self.cdp.evm.execute_permit(
                    token_address="0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",  # Base USDC
                    owner=owner,
                    spender=spender,
                    value=int(value),
                    deadline=deadline,
                    v=v,
                    r=r,
                    s=s
                )
                
                tx_hash = getattr(permit_result, 'tx_hash', None)
                if tx_hash is None and isinstance(permit_result, dict):
                    tx_hash = permit_result.get('tx_hash') or permit_result.get('txHash')
                
                return {
                    "success": True,
                    "method": "cdp_native",
                    "tx_hash": tx_hash,
                    "message": f"CDP permit 授权成功: {int(value) / 1000000} USDC",
                    "details": permit_result
                }
                
            except Exception as cdp_error:
                print(f"⚠️ CDP permit API 失败: {cdp_error}")
                
                # 方法 2：回退到 Web3 实现
                return await self._fallback_permit_execution(
                    owner, spender, value, deadline, v, r, s
                )
                
        except Exception as e:
            print(f"❌ Permit 执行失败: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "Permit execution failed"
            }

    async def _fallback_permit_execution(
        self, 
        owner: str, 
        spender: str, 
        value: str, 
        deadline: int, 
        v: int, 
        r: str, 
        s: str
    ) -> Dict[str, Any]:
        """回退到 Web3 的 permit 执行"""
        try:
            from transfer_handler import get_transfer_handler
            
            handler = get_transfer_handler()
            if handler and hasattr(handler, 'execute_permit'):
                return await handler.execute_permit(
                    owner, spender, value, deadline, v, r, s
                )
            else:
                return {
                    "success": False,
                    "error": "Web3 permit fallback not available",
                    "message": "No permit execution method available"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Web3 permit fallback failed"
            }

# 全局实例
cdp_transfer_handler = None

def get_cdp_transfer_handler():
    """获取 CDP TransferHandler 实例"""
    global cdp_transfer_handler
    if cdp_transfer_handler is None:
        try:
            cdp_transfer_handler = CdpTransferHandler()
        except Exception as e:
            print(f"Failed to initialize CDP TransferHandler: {e}")
            return None
    return cdp_transfer_handler
