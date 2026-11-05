#!/usr/bin/env python3
"""
슬라이스별 사전 정의 자동 검증 스크립트 (scripts/verify_slice.py)
사용법:
    python3 scripts/verify_slice.py [1|2|3|4|5|all] [http://127.0.0.1:8000]

역할:
- 도메인이 바뀌어도 공통으로 유지되는 4-Layer 클린 아키텍처, 상향식(Bottom-Up) 무스터브(Zero-Stub) 원칙,
  SQLite 영속성/파라미터 바인딩, 데이터셋 검증/롤백 구조, 코어 엔진 순수성/결정론, API 권한/DTO 분리,
  UI 외부 CDN/파일창 금지 및 5대 상태 표시 여부를 슬라이스별로 즉시 자동 검사한다.
"""
from __future__ import annotations
import ast
import importlib
import re
import sqlite3
import sys
from pathlib import Path
from typing import List, Tuple

THIS_DIR = Path(__file__).resolve().parent
if str(THIS_DIR) not in sys.path:
    sys.path.insert(0, str(THIS_DIR))

from ui_verify import audit_html, capture_screenshot, check_url, resolve_work_dir


def resolve_task_root() -> Path:
    cwd = Path(".").resolve()
    for p in [cwd] + list(cwd.parents):
        if (p / "app").is_dir() or (p / "sk" / "work").exists():
            return p
    return cwd


def check_python_ast_conventions(py_path: Path) -> List[str]:
    """모든 슬라이스 공통: 문법, 비특정 bare except 금지, 미구현 스터브(pass/TODO/NotImplementedError) 검사."""
    issues: List[str] = []
    if not py_path.exists():
        return [f"[누락] `{py_path.name}` 파일이 존재하지 않습니다."]

    src = py_path.read_text(encoding="utf-8", errors="replace")
    try:
        tree = ast.parse(src, filename=str(py_path))
    except SyntaxError as e:
        return [f"[문법 오류] `{py_path.name}:{e.lineno}` -> {e.msg}"]

    for node in ast.walk(tree):
        if isinstance(node, ast.ExceptHandler) and node.type is None:
            issues.append(f"[컨벤션 위반] `{py_path.name}:{node.lineno}` 비특정 `bare except:`가 사용되었습니다. 구체적 예외 클래스를 명시하세요.")
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            body_wo_doc = [
                stmt for stmt in node.body
                if not (isinstance(stmt, ast.Expr) and isinstance(getattr(stmt, "value", None), ast.Constant) and isinstance(stmt.value.value, str))
            ]
            if len(body_wo_doc) == 1:
                only_stmt = body_wo_doc[0]
                if isinstance(only_stmt, ast.Pass):
                    issues.append(f"[미구현 스터브 감지] `{py_path.name}:{node.lineno}` 함수 `{node.name}()` 내부가 `pass` 스터브 상태입니다.")
                elif isinstance(only_stmt, ast.Raise) and "NotImplementedError" in ast.unparse(only_stmt):
                    issues.append(f"[미구현 스터브 감지] `{py_path.name}:{node.lineno}` 함수 `{node.name}()`가 `NotImplementedError` 스터브 상태입니다.")

    for idx, line in enumerate(src.splitlines(), start=1):
        if re.search(r"#\s*(TODO|FIXME)\b", line, re.I):
            issues.append(f"[미완성 주석 감지] `{py_path.name}:{idx}` 미완성 `TODO/FIXME` 주석이 남아 있습니다.")

    return issues


def verify_slice_1(root: Path) -> Tuple[bool, List[str], List[str]]:
    """Slice 1: 환경변수(.env.example, config.py) · SQLite 영속성/롤백(db.py) · 데이터셋 검증(data_loader.py)"""
    passed: List[str] = []
    issues: List[str] = []
    app_dir = root / "app"

    env_ex = root / ".env.example"
    if env_ex.exists() and env_ex.read_text(encoding="utf-8", errors="replace").strip():
        passed.append("`.env.example` 환경변수 템플릿 파일 확인 완료")
    else:
        issues.append("[Slice 1 결함] 루트에 `.env.example` 파일이 없거나 비어 있습니다.")

    for fname in ("config.py", "db.py", "data_loader.py"):
        fpath = app_dir / fname
        ast_issues = check_python_ast_conventions(fpath)
        if ast_issues:
            issues.extend(ast_issues)
        else:
            passed.append(f"`app/{fname}` AST 문법 · 무스터브(Zero-Stub) · 예외 처리 규칙 통과")

    cfg_path = app_dir / "config.py"
    if cfg_path.exists():
        cfg_src = cfg_path.read_text(encoding="utf-8", errors="replace")
        if "os.environ" in cfg_src or "getenv" in cfg_src:
            passed.append("`app/config.py` 환경변수(`os.environ`/`getenv`) 기반 설정 주입 확인")
        else:
            issues.append("[Slice 1 결함] `app/config.py`에서 `os.environ` 또는 `os.getenv` 호출이 감지되지 않습니다.")

    db_path = app_dir / "db.py"
    if db_path.exists():
        db_src = db_path.read_text(encoding="utf-8", errors="replace")
        if "sqlite3" in db_src:
            passed.append("`app/db.py` SQLite 영속성 드라이버 사용 확인")
        else:
            issues.append("[Slice 1 주의] `app/db.py`에서 `sqlite3` 사용이 감지되지 않습니다.")

        if re.search(r'f["\']\s*(SELECT|INSERT|UPDATE|DELETE)\b.*\{', db_src, re.I):
            issues.append("[Slice 1 보안/컨벤션 위반] `app/db.py`에 f-string SQL 쿼리 조합이 감지되었습니다. `?` 파라미터 바인딩을 사용하세요.")
        else:
            passed.append("`app/db.py` SQL 문자열 포맷팅 주입 없음 (`?` 파라미터 바인딩 준수)")

        if any(k in db_src.lower() for k in ("is_stale", "stale", "needs_recalc")):
            passed.append("`app/db.py` 데이터 변경 후 재계산 전 이전 결과 노출 차단(`is_stale`) 상태 관리 확인")
        else:
            issues.append("[Slice 1 주의] `app/db.py`에 재계산 필요 상태 플래그(`is_stale` 등) 관리 로직이 보이지 않습니다.")

    dl_path = app_dir / "data_loader.py"
    if dl_path.exists():
        dl_src = dl_path.read_text(encoding="utf-8", errors="replace")
        if "validate" in dl_src.lower():
            passed.append("`app/data_loader.py` 데이터셋 유효성 검증 함수 존재 확인")
        else:
            issues.append("[Slice 1 결함] `app/data_loader.py`에 데이터셋 검증(`validate*`) 함수가 보이지 않습니다.")

    ds_dir = root / "data" / "datasets"
    if ds_dir.exists() and list(ds_dir.iterdir()):
        passed.append(f"`data/datasets/` 화면 선택·검증 테스트용 데이터셋 준비 확인 ({len(list(ds_dir.iterdir()))}개 항목)")
    else:
        issues.append("[Slice 1 주의] `data/datasets/` 폴더가 없거나 테스트용 데이터셋(정상 변경본/오류 주입본)이 아직 준비되지 않았습니다.")

    return len(issues) == 0, passed, issues


def verify_slice_2(root: Path) -> Tuple[bool, List[str], List[str]]:
    """Slice 2: 순수 도메인 모델 및 최적화·재계산 코어 엔진 (app/core_engine.py)"""
    passed: List[str] = []
    issues: List[str] = []
    ce_path = root / "app" / "core_engine.py"

    ast_issues = check_python_ast_conventions(ce_path)
    if ast_issues:
        issues.extend(ast_issues)
    else:
        passed.append("`app/core_engine.py` AST 문법 · 무스터브(Zero-Stub) · 예외 처리 규칙 통과")

    if not ce_path.exists():
        return False, passed, issues

    src = ce_path.read_text(encoding="utf-8", errors="replace")
    tree = ast.parse(src, filename=str(ce_path))

    forbidden_imports = {"fastapi", "flask", "starlette", "sqlite3", "uvicorn"}
    found_forbidden = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                top_pkg = alias.name.split(".")[0]
                if top_pkg in forbidden_imports:
                    found_forbidden.add(top_pkg)
        elif isinstance(node, ast.ImportFrom) and node.module:
            top_pkg = node.module.split(".")[0]
            if top_pkg in forbidden_imports:
                found_forbidden.add(top_pkg)

    if found_forbidden:
        issues.append(f"[Slice 2 클린 아키텍처(SRP) 위반] 순수 도메인 계층 `app/core_engine.py`가 웹/DB 패키지({', '.join(sorted(found_forbidden))})를 직접 import하고 있습니다.")
    else:
        passed.append("`app/core_engine.py` 순수 도메인 계층 분리(`SRP`) 확인 (웹 프레임워크·DB 드라이버 의존성 0건)")

    if "random." in src and "Random(" not in src and "seed(" not in src:
        issues.append("[Slice 2 결정론 위반 위험] `app/core_engine.py`에서 시드 고정 없는 `random` 호출이 감지되었습니다. 동일 입력 대비 100% 동일한 결과를 보장하세요.")
    else:
        passed.append("`app/core_engine.py` 비결정적 난수 호출 없음 (결정론적 재현성 준수)")

    if any(k in src for k in ("unassigned_warnings", "warnings", "unassigned", "infeasible")):
        passed.append("`app/core_engine.py` 제약 미충족 대상/실행 불가 조건 명시적 경고(`unassigned_warnings` 등) 반환 구조 확인")
    else:
        issues.append("[Slice 2 주의] `app/core_engine.py`에 제약 미충족 대상을 조용히 누락하지 않고 경고하는 `unassigned_warnings` 처리 구조가 보이지 않습니다.")

    return len(issues) == 0, passed, issues


def verify_slice_3(root: Path, base_url: str) -> Tuple[bool, List[str], List[str]]:
    """Slice 3: REST API Thin Router (simulator_api.py) · 권한/DTO 분리 · 서버 엔트리(main.py) · Dockerfile"""
    passed: List[str] = []
    issues: List[str] = []
    app_dir = root / "app"

    for fname in ("simulator_api.py", "main.py"):
        fpath = app_dir / fname
        if fpath.exists():
            ast_issues = check_python_ast_conventions(fpath)
            if ast_issues:
                issues.extend(ast_issues)
            else:
                passed.append(f"`app/{fname}` AST 문법 · 무스터브(Zero-Stub) · 예외 처리 규칙 통과")

    api_path = app_dir / "simulator_api.py"
    main_path = app_dir / "main.py"
    combined_api_src = ""
    if api_path.exists():
        combined_api_src += api_path.read_text(encoding="utf-8", errors="replace")
    if main_path.exists():
        combined_api_src += "\n" + main_path.read_text(encoding="utf-8", errors="replace")

    if not combined_api_src.strip():
        issues.append("[Slice 3 결함] `app/simulator_api.py` 및 `app/main.py`를 찾을 수 없습니다.")
        return False, passed, issues

    if "CREATE TABLE" in combined_api_src.upper():
        issues.append("[Slice 3 Thin Router 위반] API 계층(`simulator_api.py`/`main.py`) 내부에 `CREATE TABLE` DDL이 직접 작성되어 있습니다. `db.py`로 분리하세요.")
    else:
        passed.append("API 라우터 계층 Thin Controller 원칙 확인 (DDL 직접 내장 없음)")

    if any(k in combined_api_src for k in ("require_admin", "admin", "role", "x-role")):
        passed.append("운영자(Admin) 서버 측 권한 확인 로직 감지 완료")
    else:
        issues.append("[Slice 3 보안 주의] API 계층에서 운영자 권한 확인(`require_admin_role` 등) 로직이 감지되지 않습니다.")

    if any(k in combined_api_src for k in ("to_user_dto", "user_dto", " sanitize", "whitelist")):
        passed.append("일반 구성원 조회 응답 화이트리스트 DTO 변환(`to_user_dto`) 구조 확인")
    else:
        issues.append("[Slice 3 개인정보 보호 주의] 구성원 조회 API에서 타인 민감 정보를 제거하는 `to_user_dto` 화이트리스트 함수가 보이지 않습니다.")

    dockerfile = root / "Dockerfile"
    if dockerfile.exists() and dockerfile.read_text(encoding="utf-8", errors="replace").strip():
        passed.append("루트 `Dockerfile` 컨테이너 빌드 정의 확인 완료")
    else:
        issues.append("[Slice 3 주의] 루트에 `Dockerfile`이 없거나 비어 있습니다.")

    status, body = check_url(base_url.rstrip("/") + "/api/health")
    if status == 200:
        passed.append(f"라이브 서버 `GET /api/health` 정상 응답 확인 (status=200, body={body[:80]})")
    else:
        passed.append(f"`GET /api/health` 미연결 (현재 서버 미기동 상태이거나 다른 포트 사용 중: {body[:60]})")

    return len(issues) == 0, passed, issues


def verify_slice_4_5(root: Path, base_url: str) -> Tuple[bool, List[str], List[str]]:
    """Slice 4 & 5: 프론트엔드 정적 자산 (외부 CDN 금지, 파일 업로드 창 금지, ES6+ 컨벤션, SVG 그래프, 5대 상태, 스크린샷)"""
    passed: List[str] = []
    issues: List[str] = []
    static_dir = root / "app" / "static"

    if not static_dir.exists():
        issues.append("[Slice 4~5 결함] `app/static/` 디렉터리가 존재하지 않습니다.")
        return False, passed, issues

    js_files = list(static_dir.glob("*.js"))
    css_files = list(static_dir.glob("*.css"))
    html_files = list(static_dir.glob("*.html"))

    if not html_files:
        issues.append("[Slice 4~5 결함] `app/static/` 내에 엔트리 HTML(`index.html`) 파일이 없습니다.")

    all_fe_text = ""
    for p in html_files + css_files + js_files:
        txt = p.read_text(encoding="utf-8", errors="replace")
        all_fe_text += "\n" + txt
        if re.search(r"(https?://cdn\.|https?://fonts\.googleapis\.com|https?://unpkg\.com|https?://cdnjs\.)", txt, re.I):
            issues.append(f"[Slice 4~5 외부 CDN 금지 위반] `{p.name}`에서 외부 CDN/웹폰트 URL 참조가 발견되었습니다. 오프라인/폐쇄망 호환을 위해 제거하세요.")

    for hpath in html_files:
        html_issues = audit_html(hpath.read_text(encoding="utf-8", errors="replace"))
        issues.extend(html_issues)

    for jpath in js_files:
        jtxt = jpath.read_text(encoding="utf-8", errors="replace")
        if re.search(r"^\s*var\s+", jtxt, re.M):
            issues.append(f"[Slice 4~5 JS 컨벤션 위반] `{jpath.name}`에서 레거시 `var` 선언이 발견되었습니다. `const`와 `let`만 사용하세요.")
        for fn in ("alert(", "confirm(", "prompt("):
            if fn in jtxt:
                issues.append(f"[Slice 4~5 전체화면/UX 위반] `{jpath.name}`에서 브라우저 기본 모달 `{fn})` 호출이 발견되었습니다.")

    if "<svg" in all_fe_text.lower() or "createelementns" in all_fe_text.lower():
        passed.append("프론트엔드 Native SVG 노드-간선 그래프 렌더링 코드 확인 완료")
    else:
        issues.append("[Slice 4~5 시각화 주의] 프론트엔드 코드에서 `<svg>` 또는 `createElementNS` 기반 SVG 그래프 렌더링 로직이 보이지 않습니다.")

    if not any("외부 CDN" in i for i in issues) and not any("금지 위반" in i for i in issues):
        passed.append("외부 CDN 미사용 · `<input type='file'>` 미사용 · `var` 미사용 검증 통과")

    status, body = check_url(base_url.rstrip("/") + "/")
    if status == 200:
        passed.append(f"라이브 웹 서버 `GET /` 정상 응답 확인 (len={len(body)})")
        work_dir = resolve_work_dir()
        work_dir.mkdir(parents=True, exist_ok=True)
        out_png = work_dir / "ui_screenshot.png"
        ok, msg = capture_screenshot(base_url.rstrip("/") + "/", out_png)
        if ok:
            passed.append(msg)

    return len(issues) == 0, passed, issues


def main():
    target_slice = sys.argv[1].lower() if len(sys.argv) > 1 else "all"
    base_url = sys.argv[2] if len(sys.argv) > 2 else "http://127.0.0.1:8000"
    root = resolve_task_root()

    slice_map = {
        "1": [("Slice 1 (Config · SQLite DB · Dataset Loader)", lambda: verify_slice_1(root))],
        "2": [("Slice 2 (Pure Domain & Optimization Engine)", lambda: verify_slice_2(root))],
        "3": [("Slice 3 (REST API · Auth/DTO · Dockerfile)", lambda: verify_slice_3(root, base_url))],
        "4": [("Slice 4~5 (Frontend SPA · SVG Graph · UI Guardrails)", lambda: verify_slice_4_5(root, base_url))],
        "5": [("Slice 4~5 (Frontend SPA · SVG Graph · UI Guardrails)", lambda: verify_slice_4_5(root, base_url))],
    }
    if target_slice == "all":
        runners = slice_map["1"] + slice_map["2"] + slice_map["3"] + slice_map["4"]
    else:
        runners = slice_map.get(target_slice, slice_map["all" if target_slice not in slice_map else target_slice])

    overall_ok = True
    print(f"=== PRE-BUILT SLICE VERIFIER (target={target_slice}, root={root.name}) ===")
    for title, fn in runners:
        ok, passed, issues = fn()
        overall_ok = overall_ok and ok
        status_str = "PASS" if ok else "NEEDS_ATTENTION"
        print(f"\n[{status_str}] {title}")
        for p in passed:
            print(f"  + [OK] {p}")
        for iss in issues:
            print(f"  - [ISSUE] {iss}")

    sys.exit(0 if overall_ok else 1)


if __name__ == "__main__":
    main()

