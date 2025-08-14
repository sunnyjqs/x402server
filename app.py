import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from eth_account import Account
try:
    # Prefer explicit SDK package to avoid name collisions with other 'cdp' packages
    from cdp_sdk import CdpClient  # type: ignore
except Exception:  # pragma: no cover
    # Fallback to 'cdp' if available
    from cdp import CdpClient  # type: ignore

# Import x402 proxy router
from x402_proxy import router as x402_router

# Load environment variables from common locations
load_dotenv(override=False)
load_dotenv(dotenv_path=Path(__file__).resolve().parent / ".env", override=False)
load_dotenv(dotenv_path=Path(__file__).resolve().parents[1] / ".env", override=False)

CDP_API_KEY_ID = os.getenv("CDP_API_KEY_ID")
CDP_API_KEY_SECRET = os.getenv("CDP_API_KEY_SECRET")
CDP_WALLET_SECRET = os.getenv("CDP_WALLET_SECRET")

if not (CDP_API_KEY_ID and CDP_API_KEY_SECRET and CDP_WALLET_SECRET):
    raise RuntimeError(
        "Missing CDP credentials. Please set CDP_API_KEY_ID, CDP_API_KEY_SECRET, CDP_WALLET_SECRET"
    )

cdp = CdpClient()

app = FastAPI()

# 注册 x402 路由
app.include_router(x402_router)


class ImportAccountRequest(BaseModel):
    private_key: str | None = None
    name: str | None = None


@app.post("/cdp/accounts")
async def create_cdp_account():
    new_account = await cdp.evm.create_account()
    address = getattr(new_account, "address", None)
    if address is None and isinstance(new_account, dict):
        address = new_account.get("address") or new_account.get("Address")
    return {"address": address}


@app.post("/cdp/accounts/import")
async def import_cdp_account(payload: ImportAccountRequest | None = None):
    # prefer request body; fallback to env
    candidate_key = (payload.private_key if payload else None) or os.getenv("EXISTING_PRIVATE_KEY") or os.getenv("PRIVATE_KEY")
    if not candidate_key:
        raise HTTPException(status_code=400, detail="Missing private_key (body) or EXISTING_PRIVATE_KEY/PRIVATE_KEY (env)")

    try:
        imported = await cdp.evm.import_account(private_key=candidate_key, name=(payload.name if payload else None))
        address = getattr(imported, "address", None)
        if address is None and isinstance(imported, dict):
            address = imported.get("address") or imported.get("Address")
        
        # 只返回地址，不返回私钥
        return {
            "address": address
        }
    except Exception as e:
        # If already imported, derive the address locally and return it (or verify via get_account)
        message = str(e)
        if "already_exists" in message or "http_code=409" in message:
            try:
                derived_address = Account.from_key(candidate_key if candidate_key.startswith("0x") else f"0x{candidate_key}").address
                # Best-effort: confirm it exists in CDP (optional)
                try:
                    _ = await cdp.evm.get_account(address=derived_address)
                except Exception:
                    pass
                # 只返回地址，即使账户已存在
                return {
                    "address": derived_address
                }
            except Exception as ie:
                raise HTTPException(status_code=500, detail=f"Import conflict; failed to derive address: {ie}")
        raise HTTPException(status_code=500, detail=f"Import failed: {e}")


@app.get("/cdp/accounts/by_name")
async def get_account_by_name(name: str):
    try:
        acc = await cdp.evm.get_account(name=name)
        address = getattr(acc, "address", None)
        if address is None and isinstance(acc, dict):
            address = acc.get("address") or acc.get("Address")
        return {"address": address}
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Account not found: {e}")


@app.get("/cdp/accounts/by_address")
async def get_account_by_address(address: str):
    try:
        acc = await cdp.evm.get_account(address=address)
        address_out = getattr(acc, "address", None) or address
        return {"address": address_out}
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Account not found: {e}")


@app.get("/cdp/accounts/from_env")
async def get_account_from_env():
    addr = os.getenv("EXISTING_ACCOUNT_ADDRESS")
    if addr:
        return {"address": addr}
    key = os.getenv("EXISTING_PRIVATE_KEY") or os.getenv("PRIVATE_KEY")
    if not key:
        raise HTTPException(status_code=404, detail="EXISTING_ACCOUNT_ADDRESS not set; also no private key in env")
    try:
        derived = Account.from_key(key if key.startswith("0x") else f"0x{key}").address
        return {"address": derived}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to derive address from env private key: {e}")


class ExportAccountRequest(BaseModel):
    address: str | None = None
    name: str | None = None


@app.post("/cdp/accounts/export")
async def export_cdp_account(payload: ExportAccountRequest):
    if not (payload.address or payload.name):
        raise HTTPException(status_code=400, detail="Provide either address or name")
    try:
        private_key_no_prefix = await cdp.evm.export_account(
            address=payload.address, name=payload.name
        )
        # cdp SDK returns hex without 0x. Return both forms for convenience.
        private_key_with_prefix = (
            private_key_no_prefix
            if private_key_no_prefix.startswith("0x")
            else f"0x{private_key_no_prefix}"
        )
        return {
            "private_key_hex": private_key_no_prefix,
            "private_key_hex_prefixed": private_key_with_prefix,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {e}")


@app.get("/health")
def health():
    return {"ok": True}




 
