"""
Vehicle Image Processor — Streamlit Dashboard (Zero Quality Loss)
Run: streamlit run app.py
"""
import streamlit as st
import shutil, tempfile
from pathlib import Path
from datetime import datetime
import pandas as pd

import processor as proc
from processor import process_all, setup_dirs, INPUT_DIR, OUTPUT_DIR, ALL_SUPPORTED

st.set_page_config(page_title="Vehicle Image Processor", page_icon="🚗", layout="wide")
st.title("🚗 Vehicle Image Processor")
st.caption("Zero quality loss — original dimensions preserved")

# ── Sidebar ──
with st.sidebar:
    st.header("⚙️ Output Settings")

    fmt = st.radio("Output Format", ["PNG (Lossless ✅)", "JPEG (Smaller size)"], index=0)
    proc.OUTPUT_FORMAT = "PNG" if fmt.startswith("PNG") else "JPEG"

    if proc.OUTPUT_FORMAT == "JPEG":
        proc.JPEG_QUALITY = st.slider("JPEG Quality", 60, 95, 95)
        st.caption("95 = maximum JPEG quality")

    resize_on = st.toggle("Enable Resizing", value=False)
    if resize_on:
        proc.MAX_DIMENSION = st.slider("Max Dimension (px)", 800, 8000, 4000, step=100)
        st.caption(f"Images larger than {proc.MAX_DIMENSION}px will be scaled down proportionally")
    else:
        proc.MAX_DIMENSION = None
        st.success("✅ No resizing — full original dimensions")

    st.divider()
    st.markdown("**Supported input formats**")
    st.markdown("""
- 🖼️ JPG, PNG, BMP, GIF, TIFF, WebP, ICO
- 📱 HEIC / HEIF (iPhone)
- 📷 RAW: CR2, NEF, ARW, DNG...
- 🎨 SVG (vector)
- 📄 PDF (each page separately)
    """)

# ── Upload ──
st.subheader("📤 Upload Files")
ext_list = [e.lstrip(".") for e in sorted(ALL_SUPPORTED)]
uploaded = st.file_uploader("Upload", type=ext_list,
                             accept_multiple_files=True, label_visibility="collapsed")

c1, c2, c3 = st.columns([2,1,1])
with c1:
    go = st.button("⚡ Process Files", type="primary", disabled=not uploaded)
with c2:
    if st.button("🗑️ Clear Output"):
        shutil.rmtree(OUTPUT_DIR, ignore_errors=True)
        OUTPUT_DIR.mkdir(exist_ok=True)
        st.success("Cleared.")
with c3:
    out_ext = ".png" if proc.OUTPUT_FORMAT == "PNG" else ".jpg"
    n = len(list(OUTPUT_DIR.glob(f"*{out_ext}"))) if OUTPUT_DIR.exists() else 0
    st.metric("Files in output/", n)

# ── Process ──
if go and uploaded:
    setup_dirs()
    for uf in uploaded:
        (INPUT_DIR / uf.name).write_bytes(uf.getbuffer())

    with st.spinner("Converting — no quality loss..."):
        results = process_all()

    for f in INPUT_DIR.iterdir():
        if f.is_file(): f.unlink()

    ok  = [r for r in results if r["status"] == "ok"]
    err = [r for r in results if r["status"] != "ok"]

    if ok:  st.success(f"✅ {len(ok)} image(s) converted — zero quality loss!")
    if err:
        st.error(f"❌ {len(err)} error(s)")
        for r in err: st.code(f"{r['source']}: {r['status']}")

    if ok:
        st.subheader("📊 Dimension & Size Report")
        df = pd.DataFrame(ok)[[
            "source","format_in","input_dim","input_size",
            "format_out","output_dim","output_size","resized","pages"
        ]]
        df.columns = [
            "Source File","Input Format","Input Dimensions","Input Size",
            "Output Format","Output Dimensions","Output Size","Resized?","Pages"
        ]

        # Highlight if resized
        def highlight_resized(row):
            color = "#fff3cd" if row["Resized?"] == "Yes" else ""
            return [f"background-color: {color}"] * len(row)

        st.dataframe(df.style.apply(highlight_resized, axis=1), use_container_width=True)

        # Summary stats
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total files processed", len(ok))
        with col2:
            resized_count = sum(1 for r in ok if r["resized"] == "Yes")
            st.metric("Resized files", resized_count)
        with col3:
            st.metric("Output format", proc.OUTPUT_FORMAT)

# ── Gallery ──
out_ext = ".png" if proc.OUTPUT_FORMAT == "PNG" else ".jpg"
if OUTPUT_DIR.exists():
    out_files = sorted(OUTPUT_DIR.glob(f"*{out_ext}"))
    if out_files:
        st.subheader(f"🖼️ Output Gallery ({len(out_files)} images)")
        cols = st.columns(4)
        for i, p in enumerate(out_files):
            with cols[i % 4]:
                st.image(str(p), caption=p.name, use_container_width=True)

        st.divider()
        zp = Path(tempfile.mktemp(suffix=".zip"))
        shutil.make_archive(str(zp.with_suffix("")), "zip", OUTPUT_DIR)
        st.download_button(
            "⬇️ Download All as ZIP", zp.read_bytes(),
            file_name=f"processed_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
            mime="application/zip", type="primary",
        )
