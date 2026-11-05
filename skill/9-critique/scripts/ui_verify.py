#!/usr/bin/env python3
"""
웹 서비스 및 UI 검증 스크립트 (scripts/ui_verify.py)
사용법:
    python3 scripts/ui_verify.py [http://127.0.0.1:8000] [path/to/index.html]
"""
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent


def resolve_work_dir() -> Path:
    cwd = Path(".").resolve()
    for p in [cwd] + list(cwd.parents) + list(THIS_DIR.parents):
        if (p / "sk" / "work").exists():
            return p / "sk" / "work"
        if (p / "sk").is_dir():
            return p / "sk" / "work"
    return cwd / "sk" / "work"


def check_url(url: str):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "SK-Kit-Verifier/2.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            return resp.status, body
    except Exception as e:
        return 0, str(e)


def audit_html(html_text: str):
    issues = []
    if re.search(r'<input[^>]+type=["\']?file["\']?', html_text, re.I):
        issues.append("[금지 위반] <input type='file'> 태그가 발견되었습니다. 전체화면 이탈 방지를 위해 제거하세요.")
    for fn in ("alert(", "confirm(", "prompt("):
        if fn in html_text:
            issues.append(f"[주의] 브라우저 기본 모달 {fn}) 호출이 있습니다. 인앱 토스트/모달로 대체를 권장합니다.")
    return issues


def capture_screenshot(url: str, out_png: Path):
    for binary in ("chromium", "chromium-browser", "google-chrome"):
        try:
            cmd = [
                binary,
                "--headless",
                "--no-sandbox",
                "--disable-gpu",
                "--window-size=1440,900",
                f"--screenshot={out_png.as_posix()}",
                url,
            ]
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=12)
            if res.returncode == 0 and out_png.exists():
                return True, f"스크린샷 캡처 성공 ({out_png})"
        except Exception:
            continue
    return False, "Chromium 바이너리를 찾을 수 없어 스크린샷 캡처를 건너뛰었습니다."


def main():
    base_url = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else "http://127.0.0.1:8000"
    html_path = Path(sys.argv[2]) if len(sys.argv) > 2 else None
    work_dir = resolve_work_dir()
    work_dir.mkdir(parents=True, exist_ok=True)

    print(f"=== WEB SERVICE & UI VERIFICATION ({base_url}) ===")
    for ep in ("/", "/api/health", "/api/state"):
        status, body = check_url(base_url + ep)
        print(f"  - GET {ep:15s} -> status={status} (len={len(body)})")
        if ep == "/" and status == 200:
            for iss in audit_html(body):
                print("   ", iss)

    if html_path and html_path.exists():
        for iss in audit_html(html_path.read_text(encoding="utf-8", errors="replace")):
            print("   ", iss)

    out_png = work_dir / "ui_screenshot.png"
    ok, msg = capture_screenshot(base_url + "/", out_png)
    print(f"  - Headless Visual Check: {msg}")


if __name__ == "__main__":
    main()
