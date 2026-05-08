"""
전체 자동화 체크 스크립트
1. HTML 포맷 정리
2. HTML 기본 검증
3. Git 변경사항 확인
보안: 로컬 파일 및 git 명령어만 사용, 외부 통신 없음
"""
import subprocess
import sys
import os


def run_script(script: str, *args) -> bool:
    result = subprocess.run(
        [sys.executable, script] + list(args),
    )
    return result.returncode == 0


def main(html_path: str, workspace: str):
    scripts_dir = os.path.join(workspace, ".vscode", "scripts")

    print("=" * 50)
    print("  son-cbt 자동화 체크 시작")
    print("=" * 50)
    print()

    all_ok = True

    print("[1/3] HTML 포맷 정리...")
    if not run_script(os.path.join(scripts_dir, "format_html.py"), html_path):
        all_ok = False
    print()

    print("[2/3] HTML 기본 검증...")
    if not run_script(os.path.join(scripts_dir, "validate_html.py"), html_path):
        all_ok = False
    print()

    print("[3/3] Git 변경사항 확인...")
    result = subprocess.run(
        ["git", "diff", "--stat"],
        cwd=workspace,
    )
    print()

    print("=" * 50)
    if all_ok:
        print("  [OK] 모든 체크 통과!")
    else:
        print("  [WARN] 일부 이슈 발견. 위 내용을 확인하세요.")
    print("=" * 50)

    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("사용법: python auto_check.py <HTML파일경로> <워크스페이스경로>")
        sys.exit(1)

    main(sys.argv[1], sys.argv[2])
