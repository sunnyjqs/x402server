import os
import asyncio
from fastapi import APIRouter, HTTPException
from x402.clients.httpx import x402HttpxClient
from x402.clients.base import PaymentError
from eth_account import Account
from dotenv import load_dotenv
from types import SimpleNamespace
from pydantic import BaseModel

# 加载环境变量
load_dotenv()

# 数据模型
class ExecutePermitRequest(BaseModel):
    owner: str
    spender: str
    value: str
    deadline: int
    v: int
    r: str
    s: str
    network: str = "sepolia"  # 新增：网络选择，默认 sepolia

class TransferFromRequest(BaseModel):
    owner: str  # 被扣款的地址（MetaMask 所在地址）
    amount: str = "10000"  # 6 位小数（默认 0.01 USDC）
    network: str = "sepolia"

router = APIRouter(prefix="/x402", tags=["x402"])

@router.get("/test")
async def test_x402():
    """测试 x402 包是否正确安装"""
    try:
        import x402
        return {
            "status": "success",
            "x402_version": x402.__version__ if hasattr(x402, '__version__') else "unknown",
            "message": "x402 package is available"
        }
    except ImportError as e:
        return {
            "status": "error",
            "message": f"x402 package not available: {str(e)}"
        }

@router.get("/test-account")
async def test_account():
    """测试账户创建"""
    try:
        private_key = os.getenv("EXISTING_PRIVATE_KEY") or os.getenv("PRIVATE_KEY")
        if not private_key:
            return {"status": "error", "message": "Private key not configured"}
        
        if not private_key.startswith("0x"):
            private_key = f"0x{private_key}"
        
        account = Account.from_key(private_key)
        return {
            "status": "success",
            "address": account.address,
            "private_key_length": len(private_key),
            "private_key_prefix": private_key[:10] + "..." if len(private_key) > 10 else private_key
        }
    except Exception as e:
        return {"status": "error", "message": f"Account creation failed: {str(e)}"}

@router.get("/test-network")
async def test_network():
    """测试网络连接"""
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.get("https://pay.zen7.com/crypto/item1", timeout=10.0)
            return {
                "status": "success",
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "message": "Network connection successful"
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Network connection failed: {str(e)}"
        }

@router.get("/test-x402-config")
async def test_x402_config():
    """测试 x402 客户端配置"""
    try:
        private_key = os.getenv("EXISTING_PRIVATE_KEY") or os.getenv("PRIVATE_KEY")
        if not private_key:
            return {"status": "error", "message": "Private key not configured"}
        
        if not private_key.startswith("0x"):
            private_key = f"0x{private_key}"
        
        account = Account.from_key(private_key)
        
        # 测试不同的配置方式
        configs = [
            {"name": "basic", "params": {"account": account}},
            {"name": "minimal", "params": {"account": account}},
        ]
        results = {}
        
        for config in configs:
            try:
                async with x402HttpxClient(**config["params"]) as client:
                    # 测试是否能成功发起请求
                    response = await client.get("https://pay.zen7.com/crypto/item1")
                    results[config["name"]] = "success"
            except Exception as e:
                results[config["name"]] = f"failed: {str(e)}"
        
        return {
            "status": "success",
            "account_address": account.address,
            "network_tests": results
        }
    except Exception as e:
        return {"status": "error", "message": f"x402 config test failed: {str(e)}"}

@router.get("/test-x402-imports")
async def test_x402_imports():
    """测试 x402 包的导入和可用性"""
    try:
        import x402
        import inspect
        
        # 获取 x402HttpxClient 的参数信息
        client_class = x402.clients.httpx.x402HttpxClient
        sig = inspect.signature(client_class.__init__)
        
        return {
            "status": "success",
            "x402_version": getattr(x402, '__version__', 'unknown'),
            "client_params": list(sig.parameters.keys()),
            "client_doc": client_class.__doc__ or "No documentation available"
        }
    except Exception as e:
        return {"status": "error", "message": f"Import test failed: {str(e)}"}

@router.get("/item1")
async def get_item1():
    """代理 x402 付费请求到 https://pay.zen7.com/crypto/item1"""
    try:
        # 从环境变量获取私钥
        private_key = os.getenv("EXISTING_PRIVATE_KEY") or os.getenv("PRIVATE_KEY")
        if not private_key:
            raise HTTPException(status_code=500, detail="Private key not configured")
        
        # 验证私钥格式
        if not private_key.startswith("0x"):
            private_key = f"0x{private_key}"
        
        # 创建账户对象
        try:
            account = Account.from_key(private_key)
            print(f"Account created: {account.address}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Invalid private key: {str(e)}")
        
        # 使用 x402 客户端发起付费请求
        try:
            print(f"Creating x402HttpxClient with account: {account.address}")
            print(f"Base URL: https://pay.zen7.com/crypto")

            # 使用 minimal 配置（不传 max_value 与 selector）
            async with x402HttpxClient(
                account=account
            ) as client:
                print(f"Making request to: https://pay.zen7.com/crypto/item1")
                
                # 先尝试简单的 GET 请求
                try:
                    response = await client.get("https://pay.zen7.com/crypto/item1")
                    print(f"Response received: {response}")
                    print(f"Response status: {response.status_code}")
                    
                    response_data = await response.aread()
                    print(f"Response data type: {type(response_data)}")
                    print(f"Response data length: {len(response_data) if hasattr(response_data, '__len__') else 'N/A'}")
                    
                    # 获取响应头
                    headers = dict(response.headers)
                    print(f"Response headers: {headers}")
                    
                    # 处理响应数据
                    if isinstance(response_data, bytes):
                        data_content = response_data.decode('utf-8')
                    else:
                        data_content = response_data
                    
                    print(f"Processed data: {data_content[:200]}...")  # 只显示前200个字符
                    
                    return {
                        "data": data_content,
                        "status_code": response.status_code,
                        "headers": headers,
                        "x_payment_response": headers.get("x-payment-response")
                    }
                    
                except PaymentError as request_error:
                    # 支付失败时，附带原始 402 响应体，便于诊断
                    detail = {"message": f"Payment failed: {request_error}", "account": account.address}
                    raise HTTPException(status_code=500, detail=detail)
                except Exception as request_error:
                    print(f"Request error: {str(request_error)}")
                    print(f"Error type: {type(request_error)}")
                    raise HTTPException(status_code=500, detail=f"Request failed: {str(request_error)}")
                    
        except Exception as e:
            print(f"x402HttpxClient creation error: {str(e)}")
            print(f"Error type: {type(e)}")
            print(f"Error details: {e}")
            raise HTTPException(status_code=500, detail=f"x402 client error: {str(e)}")
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"x402 request failed: {str(e)}")

@router.post("/execute-permit")
async def execute_permit(permit_request: ExecutePermitRequest):
    """执行 EIP-2612 permit 授权，建立 USDC 授权关系"""
    try:
        print(f"🔄 执行 permit 授权...")
        print(f"Owner: {permit_request.owner}")
        print(f"Spender: {permit_request.spender}")
        print(f"Value: {permit_request.value}")
        print(f"Deadline: {permit_request.deadline}")
        print(f"Signature: v={permit_request.v}, r={permit_request.r}, s={permit_request.s}")
        
        # 获取 transfer handler
        from transfer_handler import get_transfer_handler, create_sepolia_handler
        handler = None
        
        # 根据网络信息创建对应的 handler
        if permit_request.network == "sepolia":
            handler = create_sepolia_handler()
        else:
            handler = get_transfer_handler()
            
        if not handler:
            raise HTTPException(status_code=500, detail="Transfer handler not available")
        
        # 检查 spender 地址的 ETH 余额
        try:
            eth_balance = await handler.get_eth_balance(permit_request.spender)
            print(f"💰 Spender ETH 余额 (网络: {permit_request.network}): {eth_balance} ETH")
            if eth_balance < 0.0001:
                print(f"⚠️  警告: Spender ETH 余额过低 ({eth_balance} ETH), 可能无法支付 gas 费用")
        except Exception as e:
            print(f"⚠️  无法获取 ETH 余额: {e}")
        
        # 调用真实的 permit 执行方法
        result = await handler.execute_permit(
            owner=permit_request.owner,
            spender=permit_request.spender,
            value=permit_request.value,
            deadline=permit_request.deadline,
            v=permit_request.v,
            r=permit_request.r,
            s=permit_request.s,
            network=permit_request.network  # 传递网络信息
        )
        
        if result.get("success"):
            return {
                "success": True,
                "txHash": result.get("tx_hash"),
                "message": result.get("message", "Permit executed successfully"),
                "details": result.get("details", {})
            }
        else:
            raise HTTPException(
                status_code=500, 
                detail=result.get("error", "Permit execution failed")
            )
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Permit 执行失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Permit execution failed: {str(e)}")

@router.post("/transfer-from")
async def transfer_from(req: TransferFromRequest):
    """使用已建立的 allowance，从 owner 转 USDC 到后端钱包地址（spender 自己）。"""
    try:
        print("🔄 执行 transferFrom...")
        print(f"Owner: {req.owner}")
        print(f"Amount: {req.amount}")
        print(f"Network: {req.network}")

        from transfer_handler import get_transfer_handler, create_sepolia_handler
        if req.network == "sepolia":
            handler = create_sepolia_handler()
        else:
            handler = get_transfer_handler()

        if not handler:
            raise HTTPException(status_code=500, detail="Transfer handler not available")

        result = await handler.execute_transfer_from(req.owner, req.amount)
        if result.get("success"):
            return {
                "success": True,
                "txHash": result.get("tx_hash"),
                "message": result.get("message", "transferFrom executed"),
                "final_balance": result.get("final_balance"),
                "final_balance_usdc": result.get("final_balance_usdc"),
            }
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "transferFrom failed"))
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ transferFrom 执行失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"transferFrom execution failed: {str(e)}")
