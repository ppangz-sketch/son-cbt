#!/usr/bin/env python3
"""
🌐 VS Code 글로벌 AI 라우터
============================
모든 워크스페이스에서 사용 가능한 AI 작업 자동화 시스템.

설치:
  python .vscode/scripts/install_global_router.py

사용 (어느 워크스페이스에서나):
  ai-router start "작업 설명"
  ai-router handoff --to claude_code
  ai-router status
  ai-router cost
  ai-router done
"""

import os
import sys
import json
import shutil
from pathlib import Path

GLOBAL_DIR = Path.home() / ".vscode-ai-router"
GLOBAL_SCRIPT = GLOBAL_DIR / "ai_router.py"
GLOBAL_CONFIG = GLOBAL_DIR / "config.json"
PROFILE_FILE = Path.home() / "Documents" / "WindowsPowerShell" / "Microsoft.PowerShell_profile.ps1"

def install():
    """글로벌 설치"""
    print("🚀 VS Code 글로벌 AI 라우터 설치 중...\n")

    # 1. 글로벌 디렉토리 생성
    GLOBAL_DIR.mkdir(parents=True, exist_ok=True)

    # 2. 현재 ai_router.py 복사
    current_script = Path(__file__).resolve().parent / "ai_router.py"
    if current_script.exists():
        shutil.copy2(current_script, GLOBAL_SCRIPT)
        print(f"✅ 스크립트 복사: {GLOBAL_SCRIPT}")

    # 3. 글로벌 설정 파일 생성
    config = {
        "version": "2.0",
        "installed_at": __import__('datetime').datetime.now().isoformat(),
        "providers": {
            "copilot": {"name": "GitHub Copilot", "type": "extension", "monthlyCost": 10},
            "claude_code": {"name": "Claude Code", "type": "cli", "installCmd": "npm install -g @anthropic-ai/claude-code", "runCmd": "claude"},
            "openrouter": {"name": "OpenRouter", "type": "api", "note": "최종 병기로만 사용"}
        },
        "routing": {
            "small_project": "copilot",
            "medium_project": "claude_code",
            "large_audit": "claude_code",
            "last_resort": "openrouter"
        }
    }
    with open(GLOBAL_CONFIG, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    print(f"✅ 설정 파일 생성: {GLOBAL_CONFIG}")

    # 4. PowerShell 프로필에 alias 등록
    profile_dir = PROFILE_FILE.parent
    profile_dir.mkdir(parents=True, exist_ok=True)

    alias_cmd = f'\n# AI Router alias (자동 생성)\nfunction ai-router {{ python "{GLOBAL_SCRIPT}" $args }}\n'

    if PROFILE_FILE.exists():
        with open(PROFILE_FILE, "r", encoding="utf-8") as f:
            content = f.read()
        if "ai-router" not in content:
            with open(PROFILE_FILE, "a", encoding="utf-8") as f:
                f.write(alias_cmd)
            print(f"✅ PowerShell alias 등록: {PROFILE_FILE}")
        else:
            print(f"ℹ️ 이미 등록된 alias: {PROFILE_FILE}")
    else:
        with open(PROFILE_FILE, "w", encoding="utf-8") as f:
            f.write(alias_cmd)
        print(f"✅ PowerShell 프로필 생성 + alias 등록: {PROFILE_FILE}")

    # 5. VS Code settings.json에 태스크 자동 등록 안내
    vscode_settings = Path.home() / "AppData" / "Roaming" / "Code" / "User" / "settings.json"

    print(f"""
╔══════════════════════════════════════════════════════════╗
║           ✅ 설치 완료!                                 ║
╠══════════════════════════════════════════════════════════╣
║  사용법 (PowerShell 재시작 후):                         ║
║    ai-router start "작업 설명"                          ║
║    ai-router handoff --to claude_code                   ║
║    ai-router handoff --to openrouter                    ║
║    ai-router handoff --to copilot                       ║
║    ai-router status                                     ║
║    ai-router cost                                       ║
║    ai-router done                                       ║
╠══════════════════════════════════════════════════════════╣
║  📂 설치 경로: {GLOBAL_DIR}
║  🔄 PowerShell 재시작: . $PROFILE
╚══════════════════════════════════════════════════════════╝
""")

if __name__ == "__main__":
    install()
