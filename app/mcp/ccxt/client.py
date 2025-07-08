import subprocess
import sys
import json
import os

CCXT_RUN = [sys.executable, "-m", "app.mcp.ccxt.run"]

DEFAULT_EXCHANGE = "hyperliquid"

def get_price(symbol, quote="USDT", exchange=DEFAULT_EXCHANGE):
    proc = subprocess.Popen(
        CCXT_RUN,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=os.environ.copy(),
    )
    try:
        # Send init
        proc.stdin.write((json.dumps({"type": "init"}) + "\n").encode())
        proc.stdin.flush()
        proc.stdout.readline()  # read and discard init response

        # Send get-price action
        req = {
            "type": "action",
            "action": "get-price",
            "parameters": {"symbol": f"{symbol}/{quote}", "exchange": exchange}
        }
        proc.stdin.write((json.dumps(req) + "\n").encode())
        proc.stdin.flush()
        resp = json.loads(proc.stdout.readline())
        return resp
    finally:
        proc.terminate() 