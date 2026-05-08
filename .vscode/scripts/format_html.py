"""
HTML/CSS/JS 기본 포맷 정리 스크립트
- 들여쓰기 정리
- 연속된 빈 줄 제거
- 줄 끝 공백 제거
- UTF-8 인코딩 유지
보안: 로컬 파일만 읽고 쓰며, 외부 통신 없음
"""
import sys
import re
import os


def format_html(filepath: str) -> bool:
    if not os.path.exists(filepath):
        print(f"ERROR: 파일을 찾을 수 없습니다: {filepath}")
        return False

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    original = content

    # 1. 줄 끝 공백 제거
    content = re.sub(r"[ \t]+$", "", content, flags=re.MULTILINE)

    # 2. 연속된 빈 줄을 하나로
    content = re.sub(r"\n{3,}", "\n\n", content)

    # 3. 파일 끝에 정확히 하나의 개행만
    content = content.rstrip("\n") + "\n"

    # 4. 탭을 스페이스 2개로 변환
    content = content.replace("\t", "  ")

    if content != original:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"OK: {filepath} 포맷 정리 완료")
        return True
    else:
        print(f"OK: {filepath} 이미 정리된 상태입니다")
        return True


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용법: python format_html.py <파일경로>")
        sys.exit(1)

    success = format_html(sys.argv[1])
    sys.exit(0 if success else 1)
