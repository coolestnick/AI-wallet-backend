import subprocess
import sys
import json
import os

DEFIYIELDS_RUN = ["uvx", "defi-yields-mcp"]

def get_yield_pools(chain=None, project=None):
    proc = subprocess.Popen(
        DEFIYIELDS_RUN,
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

        # Send get_yield_pools action
        params = {}
        if chain:
            params["chain"] = chain
        if project:
            params["project"] = project
        req = {
            "type": "action",
            "action": "get_yield_pools",
            "parameters": params
        }
        proc.stdin.write((json.dumps(req) + "\n").encode())
        proc.stdin.flush()
        resp = json.loads(proc.stdout.readline())
        return resp
    finally:
        proc.terminate()

def analyze_yields(pools):
    proc = subprocess.Popen(
        DEFIYIELDS_RUN,
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

        # Send analyze_yields action
        req = {
            "type": "action",
            "action": "analyze_yields",
            "parameters": {"pools": pools}
        }
        proc.stdin.write((json.dumps(req) + "\n").encode())
        proc.stdin.flush()
        resp = json.loads(proc.stdout.readline())
        return resp
    finally:
        proc.terminate() 