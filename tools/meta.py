#!/usr/bin/env python3
"""Ask Meta AI a question through Browser MCP and get the answer back as text.

Browser MCP is a local MCP server (`npx -y @browsermcp/mcp@latest`) that drives
the person's real, already-signed-in **default Chrome** through its extension.
Meta AI is the page doing the thinking, so there is no API key and nothing to
pay for. The extension lives in the default profile; Flow's separate Chrome
profile (CDP 9333) is not it. If Chrome is closed, `--check` says so — that is
a closed window, not a missing install. See .agents/manual/04-the-two-brains.md.

The plan work (scoring, fact-check, script, caption, image prompts) is text,
not images: this driver fills Meta's composer, sends, and waits for the answer
to finish. Browser MCP cuts every tool reply at 10 000 characters, so the
prompt asks Meta to wrap its answer in `<<<PLAN>>>` … `<<<END>>>` and the answer
is read back in fixed-size slices of the page text between those markers.

Usage:
  python3 tools/meta.py --check                       # is the bridge alive?
  python3 tools/meta.py ask --prompt-file "video-projects/<page>/META PROMPT.md" \\
      --out video-projects/<page>/<film>/plan/META-raw.md
  python3 tools/meta.py ask "say hello" --out /tmp/hello.md
"""

from __future__ import annotations

import argparse
import json
import re
import select
import subprocess
import sys
import time
from pathlib import Path

META_URL = "https://meta.ai/"
START = "<<<PLAN>>>"
END = "<<<END>>>"
SLICE = 4200          # Browser MCP truncates a reply at 10 000 characters
COMPOSER = "div[contenteditable=true]"
SEND_MARKER = "<!-- SEND BELOW -->"   # everything under this line is what Meta reads
NO_BROWSER = "No browser is connected"
CHROME_HELP = (
    "browser-mcp: no Chrome window is connected.\n"
    "The Browser MCP extension is installed in the default Chrome profile; the window is "
    "simply not open.\n"
    "Start it, then re-run:\n"
    "  /opt/google/chrome/chrome --no-first-run --no-default-browser-check https://meta.ai/\n"
    "This is not an install, sign-in or API-key problem. Do not switch to a paid route."
)


def load_prompt(path) -> str:
    """The text to send: after the SEND marker when the file has one."""
    text = Path(path).read_text(encoding="utf-8")
    if SEND_MARKER in text:
        text = text.split(SEND_MARKER, 1)[1]
    return text.strip()


class Bridge:
    """Minimal MCP client for Browser MCP's single `browser` tool."""

    def __init__(self, cmd=None, timeout_hello=120):
        self.cmd = cmd or ["npx", "-y", "@browsermcp/mcp@latest"]
        self.p = subprocess.Popen(
            self.cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            bufsize=1,
        )
        self.n = 0
        self._req("initialize", {
            "protocolVersion": "2025-06-18",
            "capabilities": {},
            "clientInfo": {"name": "car-reel-meta", "version": "1.0"},
        }, timeout=timeout_hello)
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
        raise TimeoutError("browser mcp: no reply for id %s" % want)

    def browser(self, commands, timeout=180):
        r = self._req("tools/call", {"name": "browser",
                                     "arguments": {"commands": commands}}, timeout)
        if "error" in r:
            raise RuntimeError(r["error"].get("message", str(r["error"])))
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


class MetaText:
    def __init__(self, bridge: Bridge | None = None):
        self.bridge = bridge or Bridge()
        self.attach()

    @staticmethod
    def _payload(out: str) -> str:
        lines = [ln for ln in out.splitlines()
                 if ln.strip() and not ln.startswith(("✓", "✗", "Page:", "…", "Step ", "  "))]
        return lines[-1] if lines else ""

    def eval_js(self, js: str, timeout=120):
        out, err = self.bridge.browser('eval "%s"' % js.replace('"', '\\"'), timeout=timeout)
        if err:
            raise RuntimeError(self._payload(out) or out.strip())
        body = self._payload(out)
        try:
            return json.loads(body)
        except Exception:
            if " cut at " in out:
                raise RuntimeError("browser reply truncated — shrink the slice")
            return body

    def attach(self):
        """Select an existing meta.ai tab, or open one."""
        out, err = self.bridge.browser("tab list", timeout=60)
        if err or NO_BROWSER in out:
            raise SystemExit(CHROME_HELP)
        for line in out.splitlines():
            m = re.match(r"\s*(\d+)\s+.*?—\s+(\S+)", line)
            if m and "meta.ai" in m.group(2):
                self.bridge.browser("tab select %s" % m.group(1), timeout=60)
                return False
        opened, opened_err = self.bridge.browser("tab new %s\nwait 5000" % META_URL, timeout=120)
        if opened_err:
            raise SystemExit("browser-mcp is connected, but opening meta.ai failed: %s"
                             % (self._payload(opened) or opened.strip())[:300])
        for _ in range(30):
            if self.composer_ready(quiet=True):
                return True
            time.sleep(1)
        raise SystemExit("the meta.ai tab is open but the composer is not there — "
                         "sign in to Meta AI once in that Chrome window, or check the page loaded.")

    def composer_ready(self, quiet=False) -> bool:
        try:
            return self.eval_js("() => !!document.querySelector('%s')" % COMPOSER, 30) is True
        except Exception:
            if quiet:
                return False
            raise

    def submit(self, prompt: str):
        clean = re.sub(r"\s+", " ", prompt).strip().replace('"', "'").replace("\\", "/")
        out, err = self.bridge.browser('fill %s "%s"' % (COMPOSER, clean), timeout=180)
        if err:
            raise RuntimeError(self._payload(out) or out.strip())
        # never press Enter on an empty or half-filled composer
        held = self.eval_js("() => { const e=document.querySelector('%s');"
                            " return e ? (e.innerText||'').length : -1; }" % COMPOSER, 30)
        if not isinstance(held, int) or held < max(20, len(clean) // 2):
            raise RuntimeError("the composer holds %r characters, not the prompt — nothing sent"
                               % (held,))
        self._ends = self.count_ends()          # the prompt itself may carry the markers
        out, err = self.bridge.browser("press Enter", timeout=60)
        if err:
            raise RuntimeError(self._payload(out) or out.strip())
        time.sleep(2)
        url = self.bridge.browser("get url", timeout=60)[0]
        if "/prompt/" not in url:
            self.eval_js("() => { const b=document.querySelector('button[aria-label=Send]');"
                         " if(b)b.click(); }", 30)

    def count_ends(self) -> int:
        js = ("() => { const t=document.body.innerText||'';"
              " return t.split('%s').length - 1; }" % END)
        n = self.eval_js(js, 60)
        return n if isinstance(n, int) else 0

    def _answer_ready(self) -> bool:
        return self.count_ends() > getattr(self, "_ends", 0)

    def read_answer(self) -> str:
        """The text between the markers, in slices small enough for Browser MCP."""
        head = ("() => { const t=document.body.innerText||'';"
                " const b=t.lastIndexOf('%s'); const a=t.lastIndexOf('%s', b);"
                " return {a:a, b:b, n:Math.min(40000, Math.max(0, b-a))}; }" % (END, START))
        info = self.eval_js(head, 60)
        if not isinstance(info, dict) or info.get("a", -1) < 0 or info["b"] <= info["a"]:
            raise RuntimeError("no finished answer with the markers on the page")
        total = int(info.get("n") or 0)
        js = ("() => { const t=document.body.innerText||'';"            " const b=t.lastIndexOf('%s'); const a=t.lastIndexOf('%s', b);"
            " return t.slice(a+%d, a+%d); }")
        parts, offset = [], 0
        while offset < total:
            chunk = self.eval_js(js % (END, START, offset, offset + SLICE), 60)
            if not isinstance(chunk, str) or not chunk:
                break
            parts.append(chunk)
            offset += len(chunk)
            if END in chunk:
                break
        text = "".join(parts)
        if END in text:
            text = text.split(END)[0]
        return text.replace(START, "").strip()

    def ask(self, prompt: str, timeout=360, quiet=False) -> str:
        if not self.composer_ready(quiet=True):
            raise SystemExit("the meta.ai composer is not on this tab")
        self.submit(prompt)
        if not quiet:
            print("sent %d characters to meta.ai — waiting for the answer"
                  % len(prompt), flush=True)
        deadline = time.time() + timeout
        while time.time() < deadline:
            time.sleep(6)
            try:
                if self._answer_ready():
                    break
            except Exception:
                continue
        else:
            raise SystemExit("no answer within %ds (look at the meta.ai tab)" % timeout)
        time.sleep(2)
        return self.read_answer()

    def close(self):
        self.bridge.close()


def main():
    ap = argparse.ArgumentParser(description="Ask Meta AI through Browser MCP, as text.")
    sub = ap.add_subparsers(dest="cmd")
    ask = sub.add_parser("ask")
    ask.add_argument("prompt", nargs="?", help="the question, inline")
    ask.add_argument("--prompt-file", help="read the question from a file")
    ask.add_argument("--out", help="save the raw answer here")
    ask.add_argument("--timeout", type=int, default=360)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    if args.check or args.cmd is None:
        bridge = Bridge()
        try:
            try:
                out, err = bridge.browser("tab list", timeout=60)
            except Exception as e:  # noqa: BLE001 - the check reports, it does not crash
                print("browser-mcp: no reply (%s). Is @browsermcp/mcp installed?" % e)
                return
            if err or NO_BROWSER in out:
                print(CHROME_HELP)
                return
            print(out.strip()[:900])
            ai = MetaText(bridge)
            ready = ai.composer_ready(quiet=True)
            print("composer on the meta.ai tab:", ready)
            if not ready:
                print("browser-mcp is connected, but the meta.ai composer is not there — "
                      "check that this Chrome window is signed in to Meta AI.")
        finally:
            bridge.close()
        return

    if args.prompt_file:
        prompt = load_prompt(args.prompt_file)
        print("prompt: %d characters after the SEND marker" % len(prompt), flush=True)
    elif args.prompt:
        prompt = args.prompt
    else:
        ap.error("give a prompt, --prompt-file, or --check")

    ai = MetaText()
    try:
        answer = ai.ask(prompt, args.timeout)
    finally:
        ai.close()
    if args.out:
        path = Path(args.out)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(answer + "\n", encoding="utf-8")
        print("saved %s (%d characters)" % (path, len(answer)))
    print(answer)


if __name__ == "__main__":
    main()
