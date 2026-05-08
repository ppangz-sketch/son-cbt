"""
Git 커밋 & 푸시 대화형 스크립트
- 변경사항 확인 후 커밋 메시지 입력
- 자동 add → commit → push
보안: 로컬 git 명령어만 실행, 외부 통신은 git push 시에만 (GitHub)
"""
import subprocess
import sys
import os
import locale

SYS_ENC = locale.getpreferredencoding()


def run_git(cwd: str, *args) -> tuple[int, str, str]:
    """Git 명령어 실행"""
    result = subprocess.run(
        ["git"] + list(args),
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding=SYS_ENC,
        errors="replace",
    )
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def main(workspace: str):
    os.chdir(workspace)

    # 1. 상태 확인
    code, out, err = run_git(workspace, "status", "--short")
    if code != 0:
        print(f"ERROR: git status 실패\n{err}")
        sys.exit(1)

    if not out:
        print("변경사항이 없습니다. 커밋할 내용이 없어요.")
        sys.exit(0)

    print("=== 변경된 파일 ===")
    print(out)
    print()

    # 2. diff stat
    code, diff_out, _ = run_git(workspace, "diff", "--stat")
    if diff_out:
        print("=== 변경 통계 ===")
        print(diff_out)
        print()

    # 3. 커밋 메시지 입력
    try:
        msg = input("커밋 메시지를 입력하세요: ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\n취소되었습니다.")
        sys.exit(0)

    if not msg:
        print("커밋 메시지가 비어있어 취소합니다.")
        sys.exit(0)

    # 4. add
    code, _, err = run_git(workspace, "add", "-A")
    if code != 0:
        print(f"ERROR: git add 실패\n{err}")
        sys.exit(1)

    # 5. commit
    code, _, err = run_git(workspace, "commit", "-m", msg)
    if code != 0:
        print(f"ERROR: git commit 실패\n{err}")
        sys.exit(1)

    print(f"OK: 커밋 완료 - \"{msg}\"")

    # 6. push 여부 확인
    try:
        push = input("원격 저장소에 push 할까요? (y/n): ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print("\npush 건너뜁니다.")
        sys.exit(0)

    if push == "y":
        code, out, err = run_git(workspace, "push")
        if code != 0:
            print(f"ERROR: git push 실패\n{err}")
            sys.exit(1)
        print(f"OK: push 완료\n{out}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용법: python git_commit_push.py <워크스페이스경로>")
        sys.exit(1)

    main(sys.argv[1])
