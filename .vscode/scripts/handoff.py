# 🤖 AI 핸드오프 자동화 스크립트
# 사용법: 터미널에서 python .vscode/scripts/handoff.py 실행

import os
import sys
from datetime import datetime

WORKSPACE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HANDOFF_FILE = os.path.join(WORKSPACE, "copilot_handoff.md")

def init_handoff(task_description):
    """새 핸드오프 세션 시작"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    content = f"""# 🤝 Copilot → OpenRouter 핸드오프

> 시작: {now}

## 📋 작업 내용
{task_description}

## 🔍 Copilot 분석 결과
<!-- Copilot이 여기에 분석 내용을 채울 예정 -->

## 🛠️ OpenRouter 해결 결과
<!-- OpenRouter가 여기에 해결 내용을 채울 예정 -->

## ✅ 최종 적용 결과
<!-- 적용 완료 후 결과 -->
"""
    with open(HANDOFF_FILE, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✅ 핸드오프 파일 생성 완료: {HANDOFF_FILE}")
    print(f"📋 이제 Copilot에게 'copilot_handoff.md에 분석 내용 써줘'라고 요청하세요.")

def check_handoff():
    """핸드오프 파일 상태 확인"""
    if not os.path.exists(HANDOFF_FILE):
        print("❌ 핸드오프 파일이 없습니다. init_handoff를 먼저 실행하세요.")
        return

    with open(HANDOFF_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    has_copilot = "Copilot 분석 결과" in content and len(content.split("## 🔍 Copilot 분석 결과")[-1].split("##")[0].strip()) > 50
    has_openrouter = "OpenRouter 해결 결과" in content and len(content.split("## 🛠️ OpenRouter 해결 결과")[-1].split("##")[0].strip()) > 50

    print(f"📊 핸드오프 상태:")
    print(f"  Copilot 분석: {'✅ 완료' if has_copilot else '⏳ 대기중'}")
    print(f"  OpenRouter 해결: {'✅ 완료' if has_openrouter else '⏳ 대기중'}")

    if has_copilot and not has_openrouter:
        print(f"\n👉 OpenRouter에게 'copilot_handoff.md 읽고 이어서 작업해줘'라고 요청하세요.")
    elif has_openrouter:
        print(f"\n👉 Copilot에게 'copilot_handoff.md 보고 적용해줘'라고 요청하세요.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용법:")
        print("  python handoff.py init '작업 설명'")
        print("  python handoff.py check")
        sys.exit(0)

    cmd = sys.argv[1]
    if cmd == "init":
        desc = sys.argv[2] if len(sys.argv) > 2 else "작업 내용 없음"
        init_handoff(desc)
    elif cmd == "check":
        check_handoff()
    else:
        print(f"알 수 없는 명령: {cmd}")
