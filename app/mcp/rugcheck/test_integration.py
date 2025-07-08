import subprocess
import sys
import json
import os

RUGCHECK_RUN = [sys.executable, "-m", "app.mcp.rugcheck.run"]

# Example Solana token address (Wrapped SOL)
TEST_TOKEN_ADDRESS = "So11111111111111111111111111111111111111112"

def send_request(proc, req):
    proc.stdin.write((json.dumps(req) + "\n").encode())
    proc.stdin.flush()
    line = proc.stdout.readline()
    return json.loads(line)

def main():
    env = os.environ.copy()
    if not env.get("SOLSNIFFER_API_KEY"):
        print("Warning: SOLSNIFFER_API_KEY not set in environment.")
    proc = subprocess.Popen(
        RUGCHECK_RUN,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
    )
    try:
        # 1. Send init request
        init_req = {"type": "init"}
        init_resp = send_request(proc, init_req)
        print("[INIT RESPONSE]")
        print(json.dumps(init_resp, indent=2))

        # 2. Send analysis_token request
        action_req = {
            "type": "action",
            "action": "analysis_token",
            "parameters": {"token_address": TEST_TOKEN_ADDRESS},
        }
        action_resp = send_request(proc, action_req)
        print("\n[ANALYSIS_TOKEN RESPONSE]")
        print(json.dumps(action_resp, indent=2))
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=2)
        except Exception:
            proc.kill()

if __name__ == "__main__":
    main() 