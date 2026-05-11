#!/usr/bin/env python3
"""
Cursor afterFileEdit hook.

Agent/Tab 편집 직후 index.html 자동 점검을 한 번 실행한다.
실패하더라도 편집 자체를 막지 않도록 fail-open 방식으로 동작한다.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys


def main() -> int:
    try:
        json.load(sys.stdin)
    except Exception:
        pass

    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    auto_check = os.path.join(repo_root, ".vscode", "scripts", "auto_check.py")
    html_path = os.path.join(repo_root, "index.html")

    if not (os.path.isfile(auto_check) and os.path.isfile(html_path)):
        print("{}")
        return 0

    try:
        subprocess.run([sys.executable, auto_check, html_path, repo_root], cwd=repo_root, check=False)
    finally:
        print("{}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
