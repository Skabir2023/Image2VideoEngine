#!/usr/bin/env python3
"""One preflight for the three free routes: Meta AI, Flow and Kokoro.

    python3 tools/brain.py

Meta AI is Browser MCP in the **default** Chrome profile. Flow is flow-mcp in its **own**
Chrome profile (CDP 9333). Kokoro is the local voice server. A closed window or an unopened
Flow project is a state, not a missing installation — this command says which one it is and
what to do next, so no agent has to guess.
"""
from __future__ import annotations

import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from meta import Bridge, MetaText  # noqa: E402
from flow_call import Flow  # noqa: E402

CHROME_HELP = (
    "no Chrome window connected. The extension is installed in the default profile; "
    "start it:\n"
    "    /opt/google/chrome/chrome --no-first-run --no-default-browser-check https://meta.ai/\n"
    "  This is a closed window, not an install or sign-in problem."
)


def meta_status() -> tuple[bool, str]:
    bridge = Bridge()
    try:
        out, err = bridge.browser("tab list", timeout=60)
    except Exception as e:  # noqa: BLE001 - a preflight reports, it does not crash
        return False, f"no reply from browser-mcp ({e}). Is @browsermcp/mcp installed?"
    finally:
        bridge.close()
    if err or "No browser is connected" in out:
        return False, CHROME_HELP
    try:
        ai = MetaText(bridge)
        ready = ai.composer_ready(quiet=True)
    except SystemExit as e:
        return False, str(e)
    except Exception as e:  # noqa: BLE001
        return False, f"browser-mcp connected, but the meta.ai tab could not be read: {e}"
    if not ready:
        return False, (
            "browser-mcp is connected, but the meta.ai composer is not there — sign in to "
            "Meta AI once in that Chrome window, or check that the page loaded."
        )
    tabs = [line for line in out.splitlines() if "meta.ai" in line]
    return True, f"connected — composer ready ({max(1, len(tabs))} meta.ai tab(s))"


def flow_status() -> tuple[bool, str]:
    flow = Flow()
    try:
        out, err = flow.call("flow_status", {}, timeout=90)
    except Exception as e:  # noqa: BLE001
        return False, (
            f"no reply from flow-mcp ({e}). Its Chrome profile or server is not up; "
            "this is not an install problem. Check /home/openclaw/flow-mcp/dist/index.js."
        )
    finally:
        flow.close()
    if err:
        return False, f"flow-mcp returned an error: {out.strip()[:300]}"
    match = re.search(r"\{.*\}", out, re.S)
    if not match:
        return False, f"flow-mcp answered in an unexpected shape: {out.strip()[:300]}"
    try:
        status = json.loads(match.group(0))
    except json.JSONDecodeError:
        return False, f"flow-mcp answered with unreadable JSON: {out.strip()[:300]}"
    flow_info = status.get("flow", {})
    if not flow_info.get("signedIn"):
        return False, (
            "the Flow Chrome window is open but not signed in to Google — sign in once "
            "in that window (CDP 9333)."
        )
    if not flow_info.get("inProject"):
        return True, (
            "signed in; no Flow project open — that is a normal state, not a failure. "
            "Open or create a project in the Flow Chrome window (CDP 9333) before queueing plates. "
            "Images cost 0 credits in Agent mode."
        )
    project = (
        flow_info.get("project")
        or flow_info.get("projectName")
        or flow_info.get("title")
        or status.get("project")
        or "open"
    )
    return True, f"signed in, project open: {project}"


def kokoro_status() -> tuple[bool, str]:
    try:
        with urllib.request.urlopen("http://localhost:8880/health", timeout=3) as r:
            return r.status == 200, f"up (HTTP {r.status})"
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        return False, f"not answering on localhost:8880 ({e}) — start the local Kokoro server"


def main() -> int:
    checks = [
        ("Meta AI (browser-mcp)", meta_status),
        ("Flow (flow-mcp)", flow_status),
        ("Kokoro (voice)", kokoro_status),
    ]
    results = []
    for name, check in checks:
        try:
            ok, detail = check()
        except Exception as e:  # noqa: BLE001
            ok, detail = False, f"check failed: {e}"
        results.append((name, ok, detail))
        print(f"{'OK  ' if ok else '--  '}{name:<24} {detail}")
    good = sum(1 for _, ok, _ in results if ok)
    needs_project = any("no Flow project" in detail for _, _, detail in results)
    print()
    if good == len(results):
        if needs_project:
            print("all three routes are reachable — Flow needs a project opened before plates")
        else:
            print("all three routes are ready")
        return 0
    print(f"{good}/{len(results)} routes reachable — fix the lines marked -- above")
    return 1


if __name__ == "__main__":
    sys.exit(main())
