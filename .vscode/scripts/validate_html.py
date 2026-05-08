"""
HTML 기본 구조 검증 스크립트
- 태그 짝 확인
- 필수 요소 존재 확인
- 기본적인 문법 오류 감지
보안: 로컬 파일만 읽으며, 외부 통신 없음
"""
import sys
import re
import os


def validate_html(filepath: str) -> bool:
    if not os.path.exists(filepath):
        print(f"ERROR: 파일을 찾을 수 없습니다: {filepath}")
        return False

    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()
        content = "".join(lines)

    issues = []

    # 1. DOCTYPE 확인
    if "<!DOCTYPE html>" not in content and "<!doctype html>" not in content:
        issues.append(("WARNING", "DOCTYPE 선언이 없습니다", 1))

    # 2. <html> 태그 확인
    if "<html" not in content:
        issues.append(("ERROR", "<html> 태그가 없습니다", 1))
    if "</html>" not in content:
        issues.append(("ERROR", "</html> 닫는 태그가 없습니다", len(lines)))

    # 3. <head> / </head> 확인
    has_head_open = "<head>" in content or "<head " in content
    has_head_close = "</head>" in content
    if not has_head_open:
        issues.append(("WARNING", "<head> 태그가 없습니다", 1))
    if not has_head_close:
        issues.append(("WARNING", "</head> 닫는 태그가 없습니다", 1))

    # 4. <body> / </body> 확인
    has_body_open = "<body>" in content or "<body " in content
    has_body_close = "</body>" in content
    if not has_body_open:
        issues.append(("WARNING", "<body> 태그가 없습니다", 1))
    if not has_body_close:
        issues.append(("WARNING", "</body> 닫는 태그가 없습니다", 1))

    # 5. <script> / </script> 짝 확인
    script_opens = len(re.findall(r"<script[>\s]", content))
    script_closes = len(re.findall(r"</script>", content))
    if script_opens != script_closes:
        issues.append(("ERROR", f"<script> 태그 불일치: 열림={script_opens}, 닫힘={script_closes}", 1))

    # 6. <style> / </style> 짝 확인
    style_opens = len(re.findall(r"<style[>\s]", content))
    style_closes = len(re.findall(r"</style>", content))
    if style_opens != style_closes:
        issues.append(("ERROR", f"<style> 태그 불일치: 열림={style_opens}, 닫힘={style_closes}", 1))

    # 7. 주석 짝 확인
    comment_opens = len(re.findall(r"<!--", content))
    comment_closes = len(re.findall(r"-->", content))
    if comment_opens != comment_closes:
        issues.append(("ERROR", f"HTML 주석 불일치: 열림={comment_opens}, 닫힘={comment_closes}", 1))

    # 8. charset 확인
    if 'charset' not in content.lower():
        issues.append(("WARNING", "charset 선언이 없습니다", 1))

    # 결과 출력
    if issues:
        for severity, msg, line in issues:
            print(f"{severity}: {msg} (line {line})")
        print(f"\n총 {len(issues)}개 이슈 발견")
        return False
    else:
        print("OK: 기본 구조 검증 통과")
        return True


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용법: python validate_html.py <파일경로>")
        sys.exit(1)

    success = validate_html(sys.argv[1])
    sys.exit(0 if success else 1)
