import os
from fastapi import APIRouter, HTTPException
from x402.clients.httpx import x402HttpxClient
from eth_account import Account
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

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
            
            # 配置 x402 客户端，使用基本配置
            async with x402HttpxClient(
                account=account
                # 暂时不设置 max_value，让 x402 自动处理
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
