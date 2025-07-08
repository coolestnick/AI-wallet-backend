import os
import sys
import json
import requests

SOLSNIFFER_API_KEY = os.getenv("SOLSNIFFER_API_KEY")

API_URL = "https://api.solsniffer.com/v1/token/"  # Solsniffer API endpoint


def read_request():
    """Read a request from stdin."""
    line = sys.stdin.readline()
    if not line:
        sys.exit(0)
    return json.loads(line)


def write_response(response):
    """Write a response to stdout."""
    sys.stdout.write(json.dumps(response) + "\n")
    sys.stdout.flush()


def analysis_token(token_address):
    headers = {"Authorization": f"Bearer {SOLSNIFFER_API_KEY}"}
    url = f"{API_URL}{token_address}"
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return {"result": data}
    except Exception as e:
        return {"error": str(e)}


def process_request(request):
    req_type = request.get("type")
    if req_type == "init":
        return {
            "actions": [
                {
                    "name": "analysis_token",
                    "description": "Analyze a Solana token for risk profile using Solsniffer API.",
                    "parameters": {
                        "token_address": {
                            "type": "string",
                            "description": "The Solana token address to analyze."
                        }
                    }
                }
            ]
        }
    elif req_type == "action":
        action = request.get("action")
        params = request.get("parameters", {})
        if action == "analysis_token":
            token_address = params.get("token_address")
            if not token_address:
                return {"error": "Missing required parameter: token_address"}
            return analysis_token(token_address)
        else:
            return {"error": f"Unknown action: {action}"}
    else:
        return {"error": f"Unknown request type: {req_type}"}


def main():
    while True:
        try:
            req = read_request()
            resp = process_request(req)
            write_response(resp)
        except Exception as e:
            write_response({"error": str(e)})


if __name__ == "__main__":
    main() 