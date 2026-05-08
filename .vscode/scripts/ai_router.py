#!/usr/bin/env python3
"""
🚀 AI 작업 자동 라우팅 시스템 v2.0
=====================================
Copilot ↔ Claude Code ↔ OpenRouter 간 작업을 거의 자동으로 넘겨줍니다.

사용법:
  python .vscode/scripts/ai_router.py start "작업 설명"
  python .vscode/scripts/ai_router.py status
  python .vscode/scripts/ai_router.py handoff --to claude_code
  python .vscode/scripts/ai_router.py handoff --to openrouter
  python .vscode/scripts/ai_router.py handoff --to copilot
  python .vscode/scripts/ai_router.py done
  python .vscode/scripts/ai_router.py cost
"""

import os
import sys
import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

# ─── 경로 설정 ───────────────────────────────────────────
WORKSPACE = Path(__file__).resolve().parent.parent.parent
CONFIG_FILE = WORKSPACE / ".ai_config.json"
HANDOFF_FILE = WORKSPACE / ".ai_handoff.md"
COST_LOG_FILE = WORKSPACE / ".ai_cost_log.jsonl"
STATE_FILE = WORKSPACE / ".ai_state.json"

# ─── 유틸 ────────────────────────────────────────────────
def load_json(path, default=None):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return default if default is not None else {}

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def iso_now():
    return datetime.now().isoformat()

# ─── 상태 관리 ────────────────────────────────────────────
def get_state():
    return load_json(STATE_FILE, {
        "current_provider": None,
        "task_description": "",
        "handoff_count": 0,
        "started_at": None,
        "history": []
    })

def save_state(state):
    state["updated_at"] = iso_now()
    save_json(STATE_FILE, state)

# ─── 비용 로깅 ───────────────────────────────────────────
def log_cost(provider, action, estimated_cost_usd=0, detail=""):
    entry = {
        "time": iso_now(),
        "provider": provider,
        "action": action,
        "estimated_cost_usd": estimated_cost_usd,
        "detail": detail
    }
    with open(COST_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

def get_cost_summary(days=30):
    if not COST_LOG_FILE.exists():
        return {"total": 0, "by_provider": {}}

    cutoff = datetime.now() - timedelta(days=days)
    total = 0
    by_provider = {}

    with open(COST_LOG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            try:
                entry = json.loads(line)
                entry_time = datetime.fromisoformat(entry["time"])
                if entry_time >= cutoff:
                    cost = entry.get("estimated_cost_usd", 0)
                    total += cost
                    p = entry.get("provider", "unknown")
                    by_provider[p] = by_provider.get(p, 0) + cost
            except:
                continue

    return {"total": round(total, 2), "by_provider": {k: round(v, 2) for k, v in by_provider.items()}}

# ─── 핸드오프 파일 생성 ───────────────────────────────────
def create_handoff_file(from_provider, to_provider, task_desc, context=""):
    config = load_json(CONFIG_FILE)
    to_info = config.get("providers", {}).get(to_provider, {})
    from_info = config.get("providers", {}).get(from_provider, {})

    content = f"""# 🔄 AI 핸드오프: {from_info.get('name', from_provider)} → {to_info.get('name', to_provider)}

> 🕐 {now_str()}
> 📋 핸드오프 #{get_state().get('handoff_count', 0) + 1}

---

## 📌 작업 내용
{task_desc}

---

## 📤 {from_info.get('name', from_provider)} → 전달 내용

{context if context else '(컨텍스트 없음 - 이전 AI가 이 파일을 채우지 않았습니다)'}

---

## 📥 {to_info.get('name', to_provider)} → 수행할 작업

위 컨텍스트를 바탕으로 다음을 수행해주세요:

1. 위 [전달 내용]을 먼저 읽고 현재 상황을 파악
2. [작업 내용]에 명시된 작업을 이어서 수행
3. 완료 후 이 파일의 [완료 보고] 섹션에 결과를 기록

---

## ✅ 완료 보고
<!-- 작업 완료 후 AI가 여기에 결과를 기록합니다 -->

(아직 완료되지 않음)

---

## 🔙 다음 단계
완료 후 `python .vscode/scripts/ai_router.py done` 실행 또는 다음 AI에게 전달
"""
    with open(HANDOFF_FILE, "w", encoding="utf-8") as f:
        f.write(content)

    return HANDOFF_FILE

# ─── 명령어 처리 ──────────────────────────────────────────
def cmd_start(task_desc):
    """새 작업 시작 - 자동으로 최적의 AI 선택"""
    config = load_json(CONFIG_FILE)
    state = get_state()

    # 워크스페이스 파일 분석
    workspace_files = list(WORKSPACE.rglob("*"))
    code_files = [f for f in workspace_files if f.suffix in [".html", ".js", ".py", ".ts", ".css", ".json", ".md"]]
    code_files = [f for f in code_files if "node_modules" not in str(f) and ".git" not in str(f)]

    total_lines = 0
    for f in code_files:
        try:
            with open(f, "r", encoding="utf-8") as fh:
                total_lines += sum(1 for _ in fh)
        except:
            pass

    # 자동 라우팅
    if total_lines < 500 and len(code_files) <= 3:
        provider = "copilot"
        reason = f"소규모 프로젝트 ({total_lines}줄, {len(code_files)}개 파일)"
    elif total_lines < 3000:
        provider = "claude_code"
        reason = f"중간 규모 ({total_lines}줄) - Claude Code 권장"
    else:
        provider = "claude_code"
        reason = f"대규모 프로젝트 ({total_lines}줄) - Claude Code 권장"

    state["current_provider"] = provider
    state["task_description"] = task_desc
    state["started_at"] = iso_now()
    state["handoff_count"] = 0
    save_state(state)

    provider_name = config.get("providers", {}).get(provider, {}).get("name", provider)

    print(f"""
╔══════════════════════════════════════════════════════════╗
║           🚀 AI 작업 라우터 v2.0                        ║
╠══════════════════════════════════════════════════════════╣
║  📋 작업: {task_desc[:50]}{'...' if len(task_desc) > 50 else ''}
║  🤖 선택: {provider_name}
║  📊 이유: {reason}
║  💰 예상비용: {'$0 (정액제)' if provider == 'copilot' else '$1~5 (종량제)'}
╠══════════════════════════════════════════════════════════╣
║  💡 다음 명령어:
║     handoff --to claude_code  → Claude Code로 넘기기
║     handoff --to openrouter   → OpenRouter로 넘기기
║     handoff --to copilot      → Copilot으로 넘기기
║     status                    → 현재 상태 확인
║     cost                      → 비용 현황
║     done                      → 작업 완료
╚══════════════════════════════════════════════════════════╝
""")

    log_cost(provider, "start", 0, task_desc)

def cmd_handoff(to_provider):
    """다른 AI로 작업 넘기기"""
    config = load_json(CONFIG_FILE)
    state = get_state()

    from_provider = state.get("current_provider", "copilot")

    if from_provider == to_provider:
        print(f"❌ 이미 {to_provider}를 사용 중입니다.")
        return

    # 핸드오프 파일 생성
    task_desc = state.get("task_description", "")
    handoff_path = create_handoff_file(from_provider, to_provider, task_desc)

    state["current_provider"] = to_provider
    state["handoff_count"] = state.get("handoff_count", 0) + 1
    state["history"].append({
        "from": from_provider,
        "to": to_provider,
        "at": iso_now(),
        "handoff_file": str(handoff_path)
    })
    save_state(state)

    to_name = config.get("providers", {}).get(to_provider, {}).get("name", to_provider)
    from_name = config.get("providers", {}).get(from_provider, {}).get("name", from_provider)

    print(f"""
╔══════════════════════════════════════════════════════════╗
║           🔄 핸드오프 완료                              ║
╠══════════════════════════════════════════════════════════╣
║  📤 보낸쪽: {from_name}
║  📥 받는쪽: {to_name}
║  📄 파일:   .ai_handoff.md
╠══════════════════════════════════════════════════════════╣
║  💬 이제 {to_name}에게 이렇게 말하세요:
║     ".ai_handoff.md 파일을 읽고 이어서 작업해줘"
╚══════════════════════════════════════════════════════════╝
""")

    log_cost(to_provider, "handoff_receive", 0.5, f"from {from_provider}")

def cmd_status():
    """현재 작업 상태 출력"""
    state = get_state()
    config = load_json(CONFIG_FILE)
    cost = get_cost_summary(30)

    provider = state.get("current_provider", "없음")
    provider_name = config.get("providers", {}).get(provider, {}).get("name", provider)

    print(f"""
╔══════════════════════════════════════════════════════════╗
║           📊 현재 작업 상태                             ║
╠══════════════════════════════════════════════════════════╣
║  🤖 현재 AI:  {provider_name}
║  📋 작업:     {state.get('task_description', '없음')[:60]}
║  🔄 핸드오프: {state.get('handoff_count', 0)}회
║  🕐 시작:     {state.get('started_at', '없음')[:19] if state.get('started_at') else '없음'}
╠══════════════════════════════════════════════════════════╣
║  💰 30일 비용: \${cost['total']}
║     Copilot:    \${cost['by_provider'].get('copilot', 0)} (정액)
║     ClaudeCode: \${cost['by_provider'].get('claude_code', 0)}
║     OpenRouter: \${cost['by_provider'].get('openrouter', 0)}
╚══════════════════════════════════════════════════════════╝
""")

def cmd_cost():
    """비용 상세 현황"""
    cost = get_cost_summary(30)
    cost_7 = get_cost_summary(7)
    cost_1 = get_cost_summary(1)

    print(f"""
╔══════════════════════════════════════════════════════════╗
║           💰 AI 비용 현황                               ║
╠══════════════════════════════════════════════════════════╣
║  오늘:       \${cost_1['total']}
║  이번 주:    \${cost_7['total']}
║  이번 달:    \${cost['total']}
╠══════════════════════════════════════════════════════════╣
║  제공자별 (30일):
║     Copilot:    \${cost['by_provider'].get('copilot', 0)} (정액제)
║     ClaudeCode: \${cost['by_provider'].get('claude_code', 0)}
║     OpenRouter: \${cost['by_provider'].get('openrouter', 0)}
╠══════════════════════════════════════════════════════════╣
║  📁 상세 로그: .ai_cost_log.jsonl
╚══════════════════════════════════════════════════════════╝
""")

def cmd_done():
    """작업 완료 처리"""
    state = get_state()
    task = state.get("task_description", "")
    handoffs = state.get("handoff_count", 0)

    state["current_provider"] = None
    state["task_description"] = ""
    state["completed_at"] = iso_now()
    save_state(state)

    print(f"""
╔══════════════════════════════════════════════════════════╗
║           ✅ 작업 완료!                                 ║
╠══════════════════════════════════════════════════════════╣
║  📋 작업:     {task[:60]}
║  🔄 핸드오프: {handoffs}회
║  🕐 완료:     {now_str()}
╚══════════════════════════════════════════════════════════╝
""")

    log_cost("system", "done", 0, task)

# ─── 메인 ─────────────────────────────────────────────────
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("""
╔══════════════════════════════════════════════════════════╗
║        🚀 AI 작업 자동 라우터 v2.0                      ║
╠══════════════════════════════════════════════════════════╣
║  사용법:                                                ║
║    python .vscode/scripts/ai_router.py start "작업설명"  ║
║    python .vscode/scripts/ai_router.py status            ║
║    python .vscode/scripts/ai_router.py handoff --to XXX  ║
║    python .vscode/scripts/ai_router.py cost              ║
║    python .vscode/scripts/ai_router.py done              ║
╠══════════════════════════════════════════════════════════╣
║  지원 대상: copilot | claude_code | openrouter          ║
╚══════════════════════════════════════════════════════════╝
""")
        sys.exit(0)

    cmd = sys.argv[1]

    if cmd == "start":
        desc = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "작업 내용 없음"
        cmd_start(desc)

    elif cmd == "handoff":
        if "--to" in sys.argv:
            idx = sys.argv.index("--to")
            if idx + 1 < len(sys.argv):
                cmd_handoff(sys.argv[idx + 1])
            else:
                print("❌ --to 다음에 대상(copilot/claude_code/openrouter)을 지정하세요.")
        else:
            print("❌ --to 옵션이 필요합니다. 예: handoff --to claude_code")

    elif cmd == "status":
        cmd_status()

    elif cmd == "cost":
        cmd_cost()

    elif cmd == "done":
        cmd_done()

    else:
        print(f"❌ 알 수 없는 명령: {cmd}")
        print("사용법: start | handoff | status | cost | done")
