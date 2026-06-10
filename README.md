# Vehicle Image Processor

<<<<<<< HEAD
Converts JPG, PNG, and PDF files into standardized JPEG images.
Part of the AI-powered vehicle image pipeline project.

---

## Setup

```bash
pip install -r requirements.txt
```

---

## Usage

### Option A — Command line (Phase 2)

1. Drop files into the `input/` folder
2. Run the script:

```bash
python processor.py
```

3. Find results in `output/`
4. Check logs in `logs/`

### Option B — Streamlit dashboard (Phase 5)

```bash
streamlit run app.py
```

Opens at `http://localhost:8501` — upload files via browser, download a ZIP of results.
=======
A Python-based image processing pipeline that converts vehicle images from any format into standardized JPEG output. Built as part of an AI-powered vehicle data project at Shriram Automall India Limited (SAMIL).

---

## What it does

Takes image files in any format from an `input/` folder, converts them all to high-quality JPEG, and saves them to an `output/` folder. Every run generates a detailed CSV report showing input dimensions, output dimensions, file sizes, and conversion status.

---

## Supported input formats

| Format | Extension | Notes |
|--------|-----------|-------|
| JPEG | `.jpg` `.jpeg` | Re-encoded at quality 95 |
| PNG | `.png` | Transparency replaced with white background |
| BMP | `.bmp` | Direct convert |
| TIFF | `.tif` `.tiff` | Multi-page supported |
| WebP | `.webp` | Direct convert |
| GIF | `.gif` | Each frame saved as separate JPEG |
| ICO | `.ico` | Direct convert |
| HEIC | `.heic` `.heif` | iPhone camera photos |
| RAW | `.raw` `.cr2` `.nef` `.arw` `.dng` `.orf` | Camera RAW files |
| SVG | `.svg` | Vector rendered to raster (Windows needs Cairo) |
| PDF | `.pdf` | Each page saved as separate JPEG |

---

## Output

- Format: **JPEG**
- Quality: **95 / 95** (maximum)
- Dimensions: **Same as input** (no resizing)
- Naming: `filename.jpg` for single images, `filename_page01.jpg` for PDF pages, `filename_frame01.jpg` for GIF frames
>>>>>>> 0f0adb8e17004a1e0d0d330166a5cff89bf9df02

---

## Project structure

```
vehicle_image_processor/
<<<<<<< HEAD
├── processor.py      ← Core pipeline (Phase 2)
├── app.py            ← Streamlit dashboard (Phase 5)
├── requirements.txt
├── input/            ← Drop files here
├── output/           ← Processed JPEGs appear here
└── logs/             ← CSV run logs
=======
├── processor.py          Core pipeline — runs from terminal
├── app.py                Streamlit dashboard — runs in browser
├── requirements.txt      Python library dependencies
├── README.md             This file
├── input/                Drop your files here before running
├── output/               Converted JPEGs appear here
└── logs/                 CSV report saved after every run
>>>>>>> 0f0adb8e17004a1e0d0d330166a5cff89bf9df02
```

---

<<<<<<< HEAD
## What it handles

| Input | Output |
|-------|--------|
| `.jpg` / `.jpeg` | Standardized JPEG (resized, mode-fixed) |
| `.png` (including transparent) | JPEG with white background |
| `.pdf` | One JPEG per page at 2× resolution |
=======
## Setup

### Step 1 — Install Python libraries

```bash
pip install -r requirements.txt
```

### Step 2 — Drop files into input/

Copy any image files (JPG, PNG, PDF, BMP, TIFF, WebP, GIF, HEIC, RAW, SVG, ICO) into the `input/` folder.

---

## How to run

### Option A — Terminal (command line)

```bash
python processor.py
```

Results appear in `output/`. Log saved in `logs/`.

### Option B — Streamlit dashboard (browser UI)

```bash
python -m streamlit run app.py
```

Opens at `http://localhost:8501` in your browser. Upload files, click Process, view gallery, download ZIP.

---

## Output example

```
File                        In dim       In size    Out dim      Out size   Resized?
──────────────────────────────────────────────────────────────────────────────────
car_photo.jpg               4000×3000    184 KB     4000×3000    69 KB      No
logo.png                    1280×720     20 KB      1280×720     57 KB      No
inspection.pdf (page 1)     2480×3508    326 KB     2480×3508    312 KB     No
inspection.pdf (page 2)     2480×3508    326 KB     2480×3508    287 KB     No
car_anim.gif (frame 1)      640×360      43 KB      640×360      19 KB      No
```

---

## Notes on specific formats

**PDF** — A 5-page PDF produces 5 separate JPEG files, one per page. Pages are rendered at 3× zoom (216 DPI) for high clarity.

**GIF** — Animated GIFs produce one JPEG per frame. A 3-frame GIF produces 3 JPEGs.

**SVG** — Requires the Cairo system library. On Windows, install GTK from:
`https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases`
If Cairo is not installed, SVG files are skipped and all other formats still work.

**RAW** — Requires `rawpy` and `libraw`. On Ubuntu/Debian: `sudo apt install libraw-dev`. On Windows, rawpy usually installs libraw automatically via pip.

**HEIC** — iPhone photos. Requires `pillow-heif` which is included in requirements.txt.

---

## Quality and dimensions

| Setting | Value | Meaning |
|---------|-------|---------|
| Output format | JPEG | Standard, widely compatible |
| JPEG quality | 95 | Maximum quality, minimal compression |
| Resizing | Disabled | Output dimensions = input dimensions always |

There is no resizing. A 4000×3000 input always produces a 4000×3000 output.

JPEG re-encoding adds a very small second-generation quality loss (invisible at quality 95) when the input is already a JPEG. For RAW, PNG, BMP, TIFF inputs there is effectively zero visual quality loss.
>>>>>>> 0f0adb8e17004a1e0d0d330166a5cff89bf9df02

---

## Phase roadmap

| Phase | Status | Description |
|-------|--------|-------------|
<<<<<<< HEAD
| 1 | ✅ | Understand the data |
| 2 | ✅ | Core pipeline (`processor.py`) |
| 3 | 🔲 | Google Drive link support |
| 4 | 🔲 | Organize by vehicle ID |
| 5 | ✅ | Streamlit dashboard (`app.py`) |
| — | 🔲 | PostgreSQL metadata storage |
| — | 🔲 | AI classification |

---

## Next step (Phase 3)

Add Google Drive support by installing `google-api-python-client` and creating a service account.
Ask Claude: *"How do I add Google Drive download support to this processor.py?"*
=======
| 1 | Done | Understand the data and current process |
| 2 | Done | Core conversion pipeline (processor.py) |
| 3 | Planned | Google Drive link support |
| 4 | Planned | Organise output by vehicle ID |
| 5 | Done | Streamlit dashboard (app.py) |
| 6 | Planned | PostgreSQL metadata storage |
| 7 | Planned | OpenCV image analysis |
| 8 | Planned | AI-based vehicle classification |

---

## Requirements

```
Pillow>=10.0.0
pymupdf>=1.23.0
streamlit>=1.35.0
pandas>=2.0.0
pillow-heif>=0.16.0
rawpy>=0.21.0
imageio>=2.33.0
cairosvg>=2.7.0
```

---

## Built with

- Python 3.10+
- Pillow — image processing
- PyMuPDF (fitz) — PDF extraction
- rawpy — RAW camera format support
- cairosvg — SVG rasterization
- pillow-heif — HEIC/HEIF support
- Streamlit — browser dashboard
- Pandas — results table and reporting

---

## Project info

**Project:** Vehicle Image Processing Pipeline
**Organization:** Shriram Automall India Limited (SAMIL)
**Developer:** Gorrang Arora

