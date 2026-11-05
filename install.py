#!/usr/bin/env python3
"""실무형 AI 과제 표준 스킬 키트 설치 스크립트 (`python3 sk/install.py`).

과제 루트 디렉터리에서 실행하면:
1. 과제 루트의 `AGENTS.md`에 하네스 지침(`sk/harness/AGENTS.md`)을 병합합니다.
2. `sk/skill/` 하위의 14개 표준 스킬을 `.agents/skills/`에 설치합니다.
(`sk/work/` 작업 디렉터리와 `INBOX.md`, `OUTBOX.md` 등의 파일은 키트에 사전 생성되어 있습니다.)
"""
from __future__ import annotations
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TASK_ROOT = ROOT.parent
HARNESS = ROOT / "harness" / "AGENTS.md"
SKILL_SOURCE = ROOT / "skill"
SKILL_DIRS = [".agents/skills"]
BEGIN = "<!-- SK-KIT:BEGIN (python3 sk/install.py가 관리하는 구역입니다.) -->"
END = "<!-- SK-KIT:END -->"


def install_kit():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    # 1. Update AGENTS.md in TASK_ROOT
    agents_path = TASK_ROOT / "AGENTS.md"
    harness_text = HARNESS.read_text(encoding="utf-8").strip() + "\n"
    if agents_path.exists():
        orig = agents_path.read_text(encoding="utf-8")
        if BEGIN in orig and END in orig:
            pre = orig.split(BEGIN)[0]
            post = orig.split(END)[1]
            agents_path.write_text(pre + harness_text + post.lstrip("\n"), encoding="utf-8")
        else:
            agents_path.write_text(orig.rstrip() + "\n\n" + harness_text, encoding="utf-8")
    else:
        agents_path.write_text(harness_text, encoding="utf-8")

    # 2. Copy 14 skills to .agents/skills
    skill_count = 0
    for sdir_rel in SKILL_DIRS:
        target_sdir = TASK_ROOT / sdir_rel
        if target_sdir.exists():
            shutil.rmtree(target_sdir)
        target_sdir.mkdir(parents=True, exist_ok=True)
        for item in sorted(SKILL_SOURCE.iterdir(), key=lambda p: int(p.name.split("-")[0]) if p.name.split("-")[0].isdigit() else 999):
            if item.is_dir() and (item / "SKILL.md").exists():
                dst = target_sdir / item.name
                shutil.copytree(item, dst)
                if sdir_rel == ".agents/skills":
                    skill_count += 1

    print(f"[설치 완료] 14개 표준 스킬이 .agents/skills에 설치되었습니다. (총 {skill_count}개)")
    print("  1) 사용자 실전 매뉴얼 (에디터에 열기):   sk/USER_GUIDE.md")
    print("  2) 사전 요청·답장·수동 검증 피드백 입력: sk/work/INBOX.md")
    print("  3) AI 질문·DM 초안·구현 명세 브리핑:     sk/work/OUTBOX.md")
    print("  4) 세션 인계(Handoff)·구현 로직 명세:    sk/work/BUILD_PROGRESS.md")


if __name__ == "__main__":
    install_kit()
