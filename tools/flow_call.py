#!/usr/bin/env python3
"""Call one flow-mcp tool from the engine and print its answer.

    python3 tools/flow_call.py flow_status
    python3 tools/flow_call.py flow_agent_images '{"project":"daytona-plates","scenes":["…"],"aspect_ratio":"9:16"}'
    python3 tools/flow_call.py flow_wait '{"timeout_seconds":40}'

flow-mcp is a stdio MCP server (`/home/openclaw/flow-mcp/dist/index.js`) that drives Flow in its
own Chrome profile on CDP port 9333. This wrapper exists so a whole image batch can be queued,
waited on and inspected from the engine without a chat client in the middle.

`flow_status` returning `signedIn: true, inProject: false` means Flow is connected and simply has
no project open — a state, not a missing installation. Open or create one in Flow's Chrome
window (CDP 9333); a batch queued with no project lands nowhere. The route map is
.agents/manual/04-the-two-brains.md.
"""
from __future__ import annotations

import json
import os
import select
import subprocess
import sys
import time
from pathlib import Path

SERVER = os.environ.get("FLOW_MCP", "/home/openclaw/flow-mcp/dist/index.js")


class Flow:
    def __init__(self, timeout_hello=120):
        self.p = subprocess.Popen(["node", SERVER], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE, text=True, bufsize=1)
        self.n = 0
        self._req("initialize", {"protocolVersion": "2025-06-18", "capabilities": {},
                                 "clientInfo": {"name": "engine-flow", "version": "1.0"}},
                  timeout_hello)
        self._send({"jsonrpc": "2.0", "method": "notifications/initialized"})

    def _send(self, obj):
        self.p.stdin.write(json.dumps(obj) + "\n")
        self.p.stdin.flush()

    def _req(self, method, params, timeout=120):
        self.n += 1
        want = self.n
        self._send({"jsonrpc": "2.0", "id": want, "method": method, "params": params})
        end = time.time() + timeout
        while time.time() < end:
            ready, _, _ = select.select([self.p.stdout], [], [], max(0, end - time.time()))
            if not ready:
                break
            line = self.p.stdout.readline()
            if not line:
                break
            try:
                msg = json.loads(line)
            except Exception:
                continue
            if msg.get("id") == want:
                return msg
        raise SystemExit(f"flow-mcp: no reply for {method} within {timeout}s")

    def call(self, tool, args=None, timeout=180):
        r = self._req("tools/call", {"name": tool, "arguments": args or {}}, timeout)
        if "error" in r:
            return {"error": r["error"]}, True
        res = r.get("result", {})
        text = "\n".join(c.get("text", "") for c in res.get("content", []))
        return text, bool(res.get("isError"))

    def close(self):
        try:
            self.p.terminate()
            self.p.wait(timeout=5)
        except Exception:
            try:
                self.p.kill()
            except Exception:
                pass


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    tool = sys.argv[1]
    args = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    f = Flow()
    try:
        out, err = f.call(tool, args, timeout=300)
    finally:
        f.close()
    print(out if isinstance(out, str) else json.dumps(out, indent=1))
    sys.exit(1 if err else 0)


if __name__ == "__main__":
    main()
