import httpx

BASE_URL = "http://localhost:8080"

def get_protocols():
    resp = httpx.get(f"{BASE_URL}/protocols")
    resp.raise_for_status()
    return resp.json()

def get_protocol_tvl(protocol: str):
    resp = httpx.post(f"{BASE_URL}/tools/get_protocol_tvl", json={"protocol": protocol})
    resp.raise_for_status()
    return resp.json()

def get_chain_tvl(chain: str):
    resp = httpx.post(f"{BASE_URL}/tools/get_chain_tvl", json={"chain": chain})
    resp.raise_for_status()
    return resp.json()

def get_token_prices(tokens: list):
    resp = httpx.post(f"{BASE_URL}/tools/get_token_prices", json={"tokens": tokens})
    resp.raise_for_status()
    return resp.json()

def get_pools():
    resp = httpx.get(f"{BASE_URL}/pools")
    resp.raise_for_status()
    return resp.json()

def get_pool_tvl(pool_id: str):
    resp = httpx.post(f"{BASE_URL}/tools/get_pool_tvl", json={"pool": pool_id})
    resp.raise_for_status()
    return resp.json() 