"""
Git 커밋/동기화 스크립트
- 기본: 변경사항 확인 후 커밋 메시지 입력, push 여부 확인
- 빠른 모드: 커밋 메시지 인자 전달 시 자동 add -> commit -> sync
보안: 로컬 git 명령어만 실행, 외부 통신은 git pull/push 시에만 (GitHub)
"""
import argparse
from datetime import datetime
import locale
import os
import subprocess
import sys

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


def has_upstream(workspace: str) -> bool:
    code, _, _ = run_git(workspace, "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}")
    return code == 0


def has_remote_origin(workspace: str) -> bool:
    code, out, _ = run_git(workspace, "remote")
    if code != 0:
        return False
    return "origin" in out.splitlines()


def parse_changed_files(status_output: str) -> list[str]:
    files: list[str] = []
    for raw_line in status_output.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        path_part = line[3:] if len(line) > 3 else line
        if " -> " in path_part:
            path_part = path_part.split(" -> ", 1)[1]

        name = os.path.basename(path_part.strip())
        if name and name not in files:
            files.append(name)
    return files


def build_auto_message(changed_files: list[str]) -> str:
    date_str = datetime.now().strftime("%Y-%m-%d")
    if not changed_files:
        return f"auto sync {date_str}"

    if len(changed_files) <= 3:
        file_part = ", ".join(changed_files)
    else:
        file_part = f"{', '.join(changed_files[:3])} 외 {len(changed_files) - 3}건"

    return f"auto sync {date_str} {file_part}"


def sync_remote(workspace: str) -> None:
    """원격과 동기화 (upstream 있으면 pull --rebase 후 push, 없으면 origin에 upstream 설정)"""
    if has_upstream(workspace):
        code, out, err = run_git(workspace, "pull", "--rebase")
        if code != 0:
            print(f"ERROR: git pull --rebase 실패\n{err}")
            sys.exit(1)
        if out:
            print(f"OK: pull 완료\n{out}")
    else:
        if not has_remote_origin(workspace):
            print("ERROR: origin 원격 저장소가 없어 자동 동기화를 진행할 수 없습니다.")
            sys.exit(1)

    push_args = ("push",) if has_upstream(workspace) else ("push", "-u", "origin", "HEAD")
    code, out, err = run_git(workspace, *push_args)
    if code != 0:
        print(f"ERROR: git push 실패\n{err}")
        sys.exit(1)
    print(f"OK: push 완료\n{out}")


def commit_changes(workspace: str, msg: str) -> None:
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

    print(f'OK: 커밋 완료 - "{msg}"')


def main(workspace: str, message: str | None = None, auto_sync: bool = False, auto_message: bool = False):
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
    changed_files = parse_changed_files(out)

    # 2. diff stat
    code, diff_out, _ = run_git(workspace, "diff", "--stat")
    if diff_out:
        print("=== 변경 통계 ===")
        print(diff_out)
        print()

    # 3. 커밋 메시지 입력
    if auto_message:
        msg = build_auto_message(changed_files)
        print(f"자동 커밋 메시지: {msg}")
    elif message is not None:
        msg = message.strip()
        print(f"커밋 메시지: {msg}")
    else:
        try:
            msg = input("커밋 메시지를 입력하세요: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n취소되었습니다.")
            sys.exit(0)

    if not msg:
        print("커밋 메시지가 비어있어 취소합니다.")
        sys.exit(0)

    commit_changes(workspace, msg)

    if auto_sync:
        print("자동 동기화를 시작합니다...")
        sync_remote(workspace)
        return

    # 6. push 여부 확인
    try:
        push = input("원격 저장소에 push 할까요? (y/n): ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print("\npush 건너뜁니다.")
        sys.exit(0)

    if push == "y":
        sync_remote(workspace)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Git 커밋/동기화 스크립트")
    parser.add_argument("workspace", help="워크스페이스 경로")
    parser.add_argument("--message", help="커밋 메시지 (지정 시 입력 프롬프트 생략)")
    parser.add_argument("--auto-message", action="store_true", help="날짜+파일명 형식의 커밋 메시지 자동 생성")
    parser.add_argument("--auto-sync", action="store_true", help="커밋 후 pull --rebase + push 자동 실행")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    main(args.workspace, args.message, args.auto_sync, args.auto_message)
