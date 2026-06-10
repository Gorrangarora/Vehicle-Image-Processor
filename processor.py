"""
Vehicle Image Processor — Zero Quality Loss Pipeline
=====================================================
- NO resizing (output = exact same dimensions as input)
- PNG output (lossless, no compression artifacts)
- Full report: input vs output dimensions + file sizes
"""

import os
import csv
import io
from pathlib import Path
from datetime import datetime

try:
    from PIL import Image
except ImportError:
    raise SystemExit("Run: pip install Pillow")

try:
    import fitz
    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False
    print("  [warn] pymupdf not found — PDF support disabled")

try:
    from pillow_heif import register_heif_opener
    register_heif_opener()
    HAS_HEIF = True
except ImportError:
    HAS_HEIF = False

try:
    import rawpy
    HAS_RAWPY = True
except ImportError:
    HAS_RAWPY = False

try:
    import cairosvg
    HAS_CAIRO = True
except ImportError:
    HAS_CAIRO = False

# ─── Config ───────────────────────────────────────────────────────────────────
INPUT_DIR     = Path("input")
OUTPUT_DIR    = Path("output")
LOG_DIR       = Path("logs")
OUTPUT_FORMAT = "JPEG"        # PNG = lossless | change to "JPEG" if you want
JPEG_QUALITY  = 95           # only used if OUTPUT_FORMAT = "JPEG"
MAX_DIMENSION = None         # None = NO resizing at all (full original size)

PILLOW_FORMATS = {".jpg", ".jpeg", ".png", ".gif", ".bmp",
                  ".tiff", ".tif", ".webp", ".ico"}
HEIC_FORMATS   = {".heic", ".heif"}
RAW_FORMATS    = {".raw", ".cr2", ".nef", ".arw", ".dng",
                  ".orf", ".rw2", ".pef", ".srw"}
SVG_FORMATS    = {".svg"}
PDF_FORMATS    = {".pdf"}
ALL_SUPPORTED  = (PILLOW_FORMATS | HEIC_FORMATS | RAW_FORMATS |
                  SVG_FORMATS | PDF_FORMATS)
# ──────────────────────────────────────────────────────────────────────────────

def setup_dirs():
    INPUT_DIR.mkdir(exist_ok=True)
    OUTPUT_DIR.mkdir(exist_ok=True)
    LOG_DIR.mkdir(exist_ok=True)


def file_size_str(path: Path) -> str:
    """Return human-readable file size: KB or MB."""
    b = path.stat().st_size
    if b >= 1_048_576:
        return f"{b/1_048_576:.2f} MB"
    return f"{b/1024:.1f} KB"


def to_rgb(img: Image.Image) -> Image.Image:
    """Convert to RGB (for JPEG) or keep RGBA (for PNG transparency)."""
    if OUTPUT_FORMAT == "PNG":
        if img.mode in ("P", "PA"):
            return img.convert("RGBA")
        return img  # PNG supports RGBA, RGB, L etc. natively
    # JPEG path
    if img.mode in ("RGBA", "LA", "PA"):
        bg = Image.new("RGB", img.size, (255, 255, 255))
        if img.mode == "PA":
            img = img.convert("RGBA")
        bg.paste(img.convert("RGB"), mask=img.split()[-1])
        return bg
    return img.convert("RGB")


def resize_if_needed(img: Image.Image) -> Image.Image:
    if MAX_DIMENSION is None:
        return img   # NO resize
    w, h = img.size
    if w > MAX_DIMENSION or h > MAX_DIMENSION:
        img.thumbnail((MAX_DIMENSION, MAX_DIMENSION), Image.LANCZOS)
    return img


def out_ext() -> str:
    return ".png" if OUTPUT_FORMAT == "PNG" else ".jpg"


def save_output(img: Image.Image, dest: Path) -> tuple[int, int]:
    img = to_rgb(img)
    img = resize_if_needed(img)
    if OUTPUT_FORMAT == "PNG":
        img.save(dest, "PNG", optimize=False, compress_level=0)  # 0 = fastest, no extra compression
    else:
        img.save(dest, "JPEG", quality=JPEG_QUALITY, optimize=True)
    return img.size


def _row(src, dest, in_w, in_h, out_w, out_h, in_size, pages, page, status="ok"):
    out_size = file_size_str(dest) if Path(dest).exists() else "—"
    return {
        "source":       src.name,
        "input_size":   in_size,
        "input_dim":    f"{in_w}×{in_h}",
        "output":       Path(dest).name,
        "output_size":  out_size,
        "output_dim":   f"{out_w}×{out_h}",
        "resized":      "No" if (in_w == out_w and in_h == out_h) else "Yes",
        "format_in":    src.suffix.upper().lstrip("."),
        "format_out":   OUTPUT_FORMAT,
        "pages":        pages,
        "page":         page,
        "status":       status,
    }


# ─── Converters ───────────────────────────────────────────────────────────────

def convert_pillow(src: Path, dest: Path) -> list[dict]:
    in_size = file_size_str(src)
    with Image.open(src) as img:
        in_w, in_h = img.size
        frames = getattr(img, "n_frames", 1)
        rows = []
        if frames > 1:
            for i in range(frames):
                img.seek(i)
                fd = dest.parent / f"{dest.stem}_frame{i+1:02d}{out_ext()}"
                out_w, out_h = save_output(img.copy(), fd)
                rows.append(_row(src, fd, in_w, in_h, out_w, out_h, in_size, frames, i+1))
        else:
            out_w, out_h = save_output(img, dest)
            rows.append(_row(src, dest, in_w, in_h, out_w, out_h, in_size, 1, 1))
    return rows


def convert_raw(src: Path, dest: Path) -> list[dict]:
    in_size = file_size_str(src)
    with rawpy.imread(str(src)) as raw:
        rgb = raw.postprocess(use_camera_wb=True, output_bps=16 if OUTPUT_FORMAT == "PNG" else 8)
    img = Image.fromarray(rgb)
    in_w, in_h = img.size
    out_w, out_h = save_output(img, dest)
    return [_row(src, dest, in_w, in_h, out_w, out_h, in_size, 1, 1)]


def convert_svg(src: Path, dest: Path) -> list[dict]:
    in_size = file_size_str(src)
    # SVG has no fixed pixel size — render at full resolution
    png_bytes = cairosvg.svg2png(url=str(src))
    img = Image.open(io.BytesIO(png_bytes))
    in_w, in_h = img.size
    out_w, out_h = save_output(img, dest)
    return [_row(src, dest, in_w, in_h, out_w, out_h, in_size, 1, 1)]


def convert_pdf(src: Path, base_name: str) -> list[dict]:
    in_size = file_size_str(src)
    rows = []
    doc = fitz.open(str(src))
    total = len(doc)
    for page_num, page in enumerate(doc, start=1):
        mat = fitz.Matrix(3.0, 3.0)          # 3× = ~216 DPI — high quality
        pix = page.get_pixmap(matrix=mat)
        fd = OUTPUT_DIR / f"{base_name}_page{page_num:02d}{out_ext()}"
        if OUTPUT_FORMAT == "PNG":
            pix.save(str(fd))
        else:
            fd.write_bytes(pix.tobytes("jpeg"))
        rows.append(_row(src, fd, pix.width, pix.height,
                         pix.width, pix.height, in_size, total, page_num))
    doc.close()
    return rows


# ─── Main pipeline ────────────────────────────────────────────────────────────

def process_all() -> list[dict]:
    setup_dirs()
    log_rows = []

    files = sorted(INPUT_DIR.iterdir())
    image_files = [f for f in files
                   if f.suffix.lower() in ALL_SUPPORTED and f.is_file()]

    if not image_files:
        print(f"  No supported files in {INPUT_DIR}/")
        return []

    resize_note = f"Max {MAX_DIMENSION}px" if MAX_DIMENSION else "NONE (full original size)"
    print(f"\n  Output format : {OUTPUT_FORMAT}")
    print(f"  Resizing      : {resize_note}")
    print(f"  Files found   : {len(image_files)}\n")
    print(f"  {'Source':<28} {'In dim':<14} {'In size':<10} {'Out dim':<14} {'Out size':<10} {'Resized?'}")
    print(f"  {'─'*90}")

    for src in image_files:
        ext  = src.suffix.lower()
        stem = src.stem
        dest = OUTPUT_DIR / f"{stem}{out_ext()}"
        if dest.exists():
            ts = datetime.now().strftime("%H%M%S")
            dest = OUTPUT_DIR / f"{stem}_{ts}{out_ext()}"

        try:
            if ext in PDF_FORMATS:
                if not HAS_PYMUPDF: raise RuntimeError("pymupdf not installed")
                rows = convert_pdf(src, stem)
            elif ext in RAW_FORMATS:
                if not HAS_RAWPY: raise RuntimeError("rawpy not installed")
                rows = convert_raw(src, dest)
            elif ext in SVG_FORMATS:
                if not HAS_CAIRO: raise RuntimeError("cairosvg not installed")
                rows = convert_svg(src, dest)
            else:
                rows = convert_pillow(src, dest)

            for r in rows:
                log_rows.append(r)
                print(f"  {r['source']:<28} {r['input_dim']:<14} {r['input_size']:<10} "
                      f"{r['output_dim']:<14} {r['output_size']:<10} {r['resized']}")

        except Exception as e:
            print(f"  {src.name:<28} ✗ ERROR: {e}")
            log_rows.append({
                "source": src.name, "input_size": "", "input_dim": "",
                "output": "", "output_size": "", "output_dim": "",
                "resized": "", "format_in": ext.upper().lstrip("."),
                "format_out": OUTPUT_FORMAT, "pages": "", "page": "",
                "status": f"error: {e}",
            })

    # CSV log
    log_path = LOG_DIR / f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    fields = ["source","input_dim","input_size","output","output_dim",
              "output_size","resized","format_in","format_out","pages","page","status"]
    with open(log_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(log_rows)

    ok  = sum(1 for r in log_rows if r["status"] == "ok")
    err = len(log_rows) - ok
    print(f"\n  {'─'*90}")
    print(f"  ✅ {ok} file(s) done  |  ❌ {err} error(s)  |  Log → {log_path}\n")
    return log_rows


if __name__ == "__main__":
    print("\n" + "=" * 55)
    print("  Vehicle Image Processor — Zero Quality Loss")
    print("=" * 55)
    process_all()
