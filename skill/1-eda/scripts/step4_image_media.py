#!/usr/bin/env python3
"""
[Step 4] 이미지 · 비정형 미디어 데이터셋 분석기
"""
from __future__ import annotations
import struct
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


def parse_image_header(path: Path) -> Tuple[Optional[int], Optional[int], str]:
    suf = path.suffix.lower()
    try:
        data = path.read_bytes()[:32768]
        if len(data) == 0:
            return None, None, "EMPTY_0_BYTES"
        if data.startswith(b"\x89PNG\r\n\x1a\n") and len(data) >= 24:
            w, h = struct.unpack(">II", data[16:24])
            return w, h, "PNG"
        if data[:6] in (b"GIF87a", b"GIF89a") and len(data) >= 10:
            w, h = struct.unpack("<HH", data[6:10])
            return w, h, "GIF"
        if data.startswith(b"\xff\xd8"):
            idx = 2
            while idx < len(data) - 9:
                if data[idx] != 0xFF:
                    idx += 1
                    continue
                marker = data[idx + 1]
                if marker in (0xC0, 0xC1, 0xC2):
                    h, w = struct.unpack(">HH", data[idx + 5 : idx + 9])
                    return w, h, "JPEG"
                seg_len = struct.unpack(">H", data[idx + 2 : idx + 4])[0]
                idx += 2 + seg_len
            return None, None, "JPEG"
        if suf == ".svg":
            return None, None, "SVG"
    except Exception:
        return None, None, "CORRUPTED"
    return None, None, suf.lstrip(".").upper()


def analyze_images(image_paths: List[Path], root: Path, out_grid_png: Path) -> Dict[str, Any]:
    if not image_paths:
        return {"count": 0, "summary": [], "class_dist": {}}

    by_folder = Counter(str(p.parent.relative_to(root)) for p in image_paths)
    resolutions = Counter()
    formats = Counter()
    corrupted = []

    for p in image_paths[:5000]:
        w, h, fmt = parse_image_header(p)
        formats[fmt] += 1
        if fmt in ("EMPTY_0_BYTES", "CORRUPTED"):
            corrupted.append(str(p.relative_to(root)))
        elif w and h:
            resolutions[f"{w}x{h}"] += 1

    summary = [
        f"**[이미지 데이터 감지]** 총 **{len(image_paths):,}개** 이미지 파일 확인 (포맷: {', '.join(f'{k}={v}' for k, v in formats.most_common())})",
        f"**[폴더/클래스별 분포]** {', '.join(f'`{k}`({v}장)' for k, v in by_folder.most_common(8))}",
    ]
    if resolutions:
        summary.append(f"**[주요 해상도(Width*Height)]** {', '.join(f'{k}({v}장)' for k, v in resolutions.most_common(5))}")
    if corrupted:
        summary.append(f"**[손상/빈 이미지 경고]** 손상되었거나 0바이트인 파일 **{len(corrupted)}개** 발견: `{', '.join(corrupted[:5])}`")

    try:
        import warnings
        warnings.filterwarnings('ignore')
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        plt.rcParams['axes.unicode_minus'] = False
        from PIL import Image

        raster_imgs = [p for p in image_paths if p.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp", ".bmp"}][:9]
        if raster_imgs:
            n = len(raster_imgs)
            cols = min(3, n)
            rows = (n + cols - 1) // cols
            fig, axes = plt.subplots(rows, cols, figsize=(4 * cols, 3.5 * rows))
            if rows == 1 and cols == 1:
                axes = [[axes]]
            elif rows == 1:
                axes = [axes]
            elif cols == 1:
                axes = [[ax] for ax in axes]
            for idx, p in enumerate(raster_imgs):
                r, c = divmod(idx, cols)
                im = Image.open(p)
                axes[r][c].imshow(im)
                axes[r][c].set_title(f"{p.parent.name}/{p.name} ({im.size[0]}x{im.size[1]})", fontsize=8)
                axes[r][c].axis("off")
            for idx in range(len(raster_imgs), rows * cols):
                r, c = divmod(idx, cols)
                axes[r][c].axis("off")
            plt.tight_layout()
            fig.savefig(out_grid_png, dpi=120)
            plt.close(fig)
            summary.append(f"**[이미지 샘플 그리드 생성]** `{out_grid_png.as_posix()}`")
    except Exception:
        pass

    return {
        "count": len(image_paths),
        "summary": summary,
        "class_dist": dict(by_folder),
    }
