# Vehicle Image Processor

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

---

## Project structure

```
vehicle_image_processor/
├── processor.py      ← Core pipeline (Phase 2)
├── app.py            ← Streamlit dashboard (Phase 5)
├── requirements.txt
├── input/            ← Drop files here
├── output/           ← Processed JPEGs appear here
└── logs/             ← CSV run logs
```

---

## What it handles

| Input | Output |
|-------|--------|
| `.jpg` / `.jpeg` | Standardized JPEG (resized, mode-fixed) |
| `.png` (including transparent) | JPEG with white background |
| `.pdf` | One JPEG per page at 2× resolution |

---

## Phase roadmap

| Phase | Status | Description |
|-------|--------|-------------|
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
