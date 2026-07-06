"""
app.py — Streamlit dashboard: Automated Performance Outlook — PLN UP3 Cilacap.
Full glow-up + 4 viz + per-chart PNG + A4 PDF + preferensi tampilan PDF.
"""

from __future__ import annotations

import io
from typing import Any

import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
import pandas as pd
import streamlit as st
from PIL import Image

from config import COLUMN_MAP, COORDINATES, MONTH_COLUMN, MONTH_DISPLAY_ID
from utils import (
    extract_values,
    fetch_sheet,
    format_all,
    get_available_months,
    get_row_for_month,
    image_to_pdf_bytes,
    image_to_png_bytes,
    render_image,
)

# =========================================================================
# PAGE CONFIG
# =========================================================================
st.set_page_config(
    page_title="Outlook Kinerja — PLN UP3 Cilacap",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================================================================
# CUSTOM CSS
# =========================================================================
st.markdown(
    """
<style>
    .stApp { background: linear-gradient(180deg, #FBF5E8 0%, #F5E9D3 100%); }
    .block-container { padding-top: 1.5rem; padding-bottom: 3rem; max-width: 1400px; }
    .hero {
        background: linear-gradient(135deg, #5F2C17 0%, #9B4526 60%, #B84F28 100%);
        padding: 1.75rem 2.25rem; border-radius: 18px; color: #FBF5E8;
        margin-bottom: 1.5rem; box-shadow: 0 6px 24px rgba(95, 44, 23, 0.25);
    }
    .hero-title { font-size: 1.9rem; font-weight: 800; margin: 0; letter-spacing: -0.02em; color: #FBF5E8; }
    .hero-sub { margin: 0.35rem 0 0; color: #F1DFC0; font-size: 0.95rem; }
    .hero-badge {
        display: inline-block; background: rgba(232, 163, 23, 0.9); color: #4A2812;
        padding: 0.2rem 0.7rem; border-radius: 999px; font-size: 0.75rem;
        font-weight: 700; margin-left: 0.5rem; vertical-align: middle;
    }
    .sec-title { color: #5F2C17; font-weight: 800; font-size: 1.05rem; margin: 0 0 0.75rem 0; display: flex; align-items: center; gap: 0.4rem; }
    .sec-sub { color: #8B6F5C; font-size: 0.8rem; margin-top: -0.3rem; margin-bottom: 0.9rem; }
    .kpi-mini { border-left: 3px solid #E8A317; padding: 0.45rem 0 0.45rem 0.85rem; margin-bottom: 0.75rem; }
    .kpi-label { color: #8B6F5C; font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 700; }
    .kpi-val { color: #5F2C17; font-size: 1.4rem; font-weight: 800; line-height: 1.1; }
    .kpi-tgt { color: #A6836E; font-size: 0.8rem; }
    .metric-row { margin-bottom: 0.9rem; }
    .metric-row-head { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 0.35rem; }
    .metric-name { color: #4A2812; font-weight: 700; font-size: 0.95rem; }
    .metric-pct { font-weight: 800; font-size: 0.95rem; }
    .bar-outer { height: 10px; background: #EFE1CB; border-radius: 6px; overflow: hidden; box-shadow: inset 0 1px 2px rgba(95,44,23,0.08); }
    .bar-inner { height: 100%; border-radius: 6px; transition: width 0.4s ease; }
    .metric-nums { margin-top: 0.3rem; color: #6B4E3A; font-size: 0.8rem; display: flex; justify-content: space-between; }
    .stDownloadButton button { background: linear-gradient(135deg, #5F2C17, #9B4526) !important; color: #FBF5E8 !important; border: none !important; font-weight: 700 !important; }
    .stDownloadButton button:hover { background: linear-gradient(135deg, #4A2812, #7A2500) !important; }
    
    /* Style Tambahan untuk Selectbox "Pilih metric" */
    .stSelectbox > div > div {
        background-color: #FFFFFF !important;
        border: 1px solid #E8DFD0 !important;
        border-radius: 8px !important;
        color: #4A2812 !important;
    }
    /* =========================================================================
   CUSTOM SIDEBAR STYLING (FIX TAMPILAN GELAP & KONTRAS TEKS)
   ========================================================================= */
/* 1. Mengubah background utama sidebar menjadi abu-abu gelap kebiruan */
section[data-testid="stSidebar"] { 
    background: #242731 !important; 
}

/* 2. Memaksa semua elemen teks bawaan, markdown, label, dan caption agar berwarna putih terang */
section[data-testid="stSidebar"] .stMarkdown, 
section[data-testid="stSidebar"] label, 
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] { 
    color: #FFFFFF !important; 
}

/* 3. FIX: Mengubah background tombol menjadi putih dan teksnya menjadi hitam */
section[data-testid="stSidebar"] button {
    background-color: #FFFFFF !important; /* Mengubah background tombol jadi putih */
    border: 1px solid #E8DFD0 !important; /* Memberikan border halus seperti dropdown */
    border-radius: 8px !important;       /* Membuat sudut melengkung sama seperti dropdown */
}

section[data-testid="stSidebar"] button p,
section[data-testid="stSidebar"] button span {
    color: #111111 !important;           /* Mengubah warna teks menjadi hitam/gelap */
    font-weight: 700 !important;
}
}
/* 4. FIX GARIS TEPI & SCROLLBAR COKELAT */
/* Menghilangkan atau menyamarkan garis batas vertikal di kanan sidebar */
section[data-testid="stSidebar"] + div, 
[data-testid="stSidebarCollapseByDragTarget"] {
    background-color: rgba(0, 0, 0, 0.1) !important; /* Mengubah garis cokelat vertikal menjadi abu-abu transparan halus */
    border-right: none !important;
}

/* Mengubah warna atau menyembunyikan scrollbar cokelat di sidebar */
section[data-testid="stSidebar"] .st-emotion-cache-16ids93, /* Selektor kontainer internal Streamlit */
section[data-testid="stSidebar"] > div:first-child {
    scrollbar-width: thin; /* Membuat scrollbar lebih tipis (Firefox) */
    scrollbar-color: rgba(0, 0, 0, 0.2) transparent; /* Mengubah batang scroll jadi abu-abu transparan (Firefox) */
}

/* Khusus browser Chrome, Edge, dan Safari (Webkit) */
section[data-testid="stSidebar"] ::-webkit-scrollbar {
    width: 6px !important;
    height: 6px !important;
}
section[data-testid="stSidebar"] ::-webkit-scrollbar-thumb {
    background: rgba(0, 0, 0, 0.2) !important; /* Mengubah warna kotak scrollbar cokelat menjadi abu-abu tipis */
    border-radius: 10px !important;
}
section[data-testid="stSidebar"] ::-webkit-scrollbar-track {
    background: transparent !important; /* Menghilangkan background track scrollbar */
}

/* Garis pembatas horizontal (st.divider) di dalam menu dibuat tipis */
section[data-testid="stSidebar"] hr {
    border-color: rgba(255, 255, 255, 0.1) !important;
}
    #MainMenu, footer { visibility: hidden; }
</style>
""",
    unsafe_allow_html=True
)
# =========================================================================
# HERO
# =========================================================================
st.markdown(
    """
<div class="hero">
    <div class="hero-title">⚡ Automated Performance Outlook <span class="hero-badge">2026</span></div>
    <p class="hero-sub">PLN UP3 Cilacap — Generator Infografis Kinerja Bulanan · Real-time from Google Sheets</p>
</div>
""",
    unsafe_allow_html=True,
)

# =========================================================================
# DATA LOAD
# =========================================================================
@st.cache_data(ttl=60, show_spinner="Mengambil data dari Google Sheets...")
def load_data():
    return fetch_sheet(cache_bust=True)


try:
    df = load_data()
except Exception as e:
    st.error(f"Gagal ambil data dari Google Sheets: {e}")
    st.stop()

try:
    available_months = get_available_months(df)
except KeyError as e:
    st.error(str(e))
    st.stop()

if not available_months:
    st.error("Tidak ada bulan yg terdeteksi. Cek isi sheet.")
    st.stop()

# =========================================================================
# SIDEBAR
# =========================================================================
with st.sidebar:
    st.markdown("### 🎛️ Kontrol")
    selected_month = st.selectbox("Pilih Bulan Laporan", available_months, index=0)
    st.divider()
    if st.button("🔄 Refresh data dari Google Sheets", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.divider()
    st.markdown("### 🎨 Preferensi PDF")
    infografis_full_page = st.toggle(
        "Infografis full-page (tanpa margin cream)",
        value=True,
        help="Halaman 1 PDF: template edge-to-edge tanpa background cream. kalau mau infografis mandiri.",
    )
    chart_bg_white = st.toggle(
        "Chart background putih",
        value=True,
        help="ON = chart pakai bg putih (kontras, standard laporan). OFF = chart pakai bg cream senada palette.",
    )

    st.divider()
    st.markdown("**Sumber data**")
    st.caption("Google Sheets · cache 60 detik")

# Warna background chart tergantung preferensi
CHART_BG = "#FFFFFF" if chart_bg_white else "#FBF5E8"

# =========================================================================
# GET ROW & FORMAT
# =========================================================================
row = get_row_for_month(df, selected_month)
if row is None:
    st.warning(f"Baris untuk **{selected_month}** tidak ketemu. Menampilkan template kosong.")
    values: dict[str, Any] = {k: None for k in COLUMN_MAP.keys()}
else:
    values = extract_values(row)

# ---- Parser & formatter Indonesia yg strict (dipakai override formatted) ----
import math as _math

def _parse_num_id(x):
    """
    Parse angka dari CSV Google Sheets. Auto-detect format US vs Indonesia:
      "4.691,3"    -> 4691.3   (Indonesia: titik ribuan, koma desimal)
      "4,691.3"    -> 4691.3   (US: koma ribuan, titik desimal)
      "1.192.772"  -> 1192772  (Indonesia thousand)
      "1,192,772"  -> 1192772  (US thousand)
      "4691.3"     -> 4691.3   (raw US decimal)
      "4691,3"     -> 4691.3   (raw Indonesia decimal)
    """
    if x is None:
        return None
    if isinstance(x, (int, float)):
        try:
            if _math.isnan(float(x)):
                return None
        except (TypeError, ValueError):
            return None
        return float(x)
    s = str(x).strip()
    if not s or s.lower() in {"nan", "none", "-"}:
        return None

    has_c = "," in s
    has_d = "." in s

    if has_c and has_d:
        # Separator paling kanan = desimal
        if s.rfind(",") > s.rfind("."):
            s = s.replace(".", "").replace(",", ".")   # Indonesia
        else:
            s = s.replace(",", "")                      # US
    elif has_c:
        parts = s.split(",")
        # Multi-koma atau 1 koma dgn 3 digit setelahnya -> thousand separator
        if len(parts) > 2 or (len(parts) == 2 and len(parts[1]) == 3 and parts[1].isdigit()):
            s = s.replace(",", "")
        else:
            s = s.replace(",", ".")                     # Indonesia decimal
    elif has_d:
        parts = s.split(".")
        # Multi-titik atau 1 titik dgn 3 digit setelahnya -> Indonesia thousand
        if len(parts) > 2 or (len(parts) == 2 and len(parts[1]) == 3 and parts[1].isdigit()):
            s = s.replace(".", "")

    try:
        return float(s)
    except (ValueError, TypeError):
        return None


def _fmt_id_strict(v, decimals):
    """
    Format ke konvensi Indonesia: titik ribuan, koma desimal, digit desimal fixed.
    Contoh: 4691.3 dgn decimals=1 -> "4.691,3"
            1192772 dgn decimals=0 -> "1.192.772"
    """
    parsed = _parse_num_id(v)
    if parsed is None or _math.isnan(parsed):
        return "-"
    s = f"{parsed:,.{decimals}f}"
    # US "1,234,567.89" -> Indonesia "1.234.567,89"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


# ---- Jumlah desimal per field: target & realisasi WAJIB sama, 2025 & 2026 sama ----
DECIMAL_SPEC = {
    # Metric utama — semua 2 desimal (Penjualan/SAIDI/SAIFI/ENS/Susut/P2TL)
    "penjualan_target": 2, "penjualan_realisasi": 2, "penjualan_2025": 2,
    "saidi_target":     2, "saidi_realisasi":     2, "saidi_2025":     2,
    "saifi_target":     2, "saifi_realisasi":     2, "saifi_2025":     2,
    "ens_target":       2, "ens_realisasi":       2, "ens_2025":       2,
    "susut_target":     2, "susut_realisasi":     2, "susut_2025":     2,
    "p2tl_target":      2, "p2tl_realisasi":      2, "p2tl_2025":      2,
    # Aset — mengikuti template Mei: JTM/JTR 1 desimal, sisanya integer
    "jtm_2025":       1, "jtm_2026":       1,
    "jtr_2025":       1, "jtr_2026":       1,
    "gardu_2025":     0, "gardu_2026":     0,
    "penyulang_2025": 0, "penyulang_2026": 0,
    "pelanggan_2025": 0, "pelanggan_2026": 0,
    "daya_2025":      0, "daya_2026":      0,
}


def apply_strict_format(formatted_dict, raw_values):
    """Override formatted dgn Indonesia format konsisten. Ambil raw dari values, format ulang."""
    out = dict(formatted_dict)
    for key, decimals in DECIMAL_SPEC.items():
        raw = raw_values.get(key)
        if raw is None:
            continue
        s = str(raw).strip()
        if not s or s.lower() in {"nan", "none", "-"}:
            continue
        result = _fmt_id_strict(raw, decimals)
        if result != "-":
            out[key] = result
    return out


formatted = format_all(values)
formatted = apply_strict_format(formatted, values)   # <- override supaya konsisten
month_short = selected_month.split()[0]
formatted["month_display"] = MONTH_DISPLAY_ID.get(month_short, month_short)
img_template = render_image(formatted)

# =========================================================================
# METRIC DEFINITIONS
# =========================================================================
METRICS_TOP = [
    ("penjualan", "PENJUALAN",  "GWh",       False),
    ("saidi",     "SAIDI",      "mnt/plg",   True),
    ("saifi",     "SAIFI",      "kali/plg",  True),
    ("ens",       "ENS",        "MWh",       True),
    ("susut",     "SUSUT",      "%",         True),
    ("p2tl",      "P2TL",       "MWh",       False),
]

ASETS = [
    ("jtm",       "JTM",       "kms"),
    ("jtr",       "JTR",       "kms"),
    ("gardu",     "GARDU",     "unit"),
    ("penyulang", "PENYULANG", "unit"),
    ("pelanggan", "PELANGGAN", "plg"),
    ("daya",      "DAYA TERSAMBUNG", "MVA"),
]

MONTH_ORDER = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

def _num(x: Any) -> float | None:
    if x is None:
        return None
    try:
        s = str(x).strip()
        if not s or s.lower() in {"nan", "none", "-"}:
            return None
        if "," in s and "." in s:
            s = s.replace(".", "").replace(",", ".")
        elif "," in s:
            s = s.replace(",", ".")
        return float(s)
    except (ValueError, TypeError):
        return None


def _score(target, real, lower_better):
    if target is None or real is None or target == 0 or real == 0:
        return None
    return (target / real * 100) if lower_better else (real / target * 100)


def _achievement(target, real, lower_better):
    score = _score(target, real, lower_better)
    if score is None:
        return None, "#A6836E", 0.0
    color = "#4A9D5B" if score >= 100 else "#B84F28"
    return score, color, min(100.0, max(0.0, score / 1.5))


def _fmt_num_id(v: float, decimals: int = 2) -> str:
    if v is None or np.isnan(v):
        return "-"
    s = f"{v:,.{decimals}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


# =========================================================================
# KONVENSI POLARITAS PLN (sumber: sheet KINERJA UP3, NKO 2026)
# Polaritas: 3 = Positif (naik = baik), 1 = Negatif (turun = baik),
#            2 = Range (real dlm rentang target = baik)
# Bobot: level UP3 (beda dgn ULP: SAIDI/SAIFI di ULP = 6, di UP3 = 5)
# =========================================================================
METRICS_PLN = {
    # key        : (polaritas, bobot UP3)
    "penjualan": (3, 14),
    "saidi":     (1, 5),
    "saifi":     (1, 5),
    "ens":       (1, 2),
    "susut":     (1, 12),
    "p2tl":      (3, 3),
}

PLN_CAP = 110.0  # hard cap pencapaian sesuai konvensi NKO


def _parse_range(target_str) -> tuple[float, float] | None:
    """Parse target range string spt '95-100' -> (95.0, 100.0)."""
    try:
        parts = str(target_str).replace(",", ".").split("-")
        if len(parts) == 2:
            lo, hi = float(parts[0]), float(parts[1])
            return (lo, hi) if lo <= hi else (hi, lo)
    except (ValueError, TypeError):
        pass
    return None


def _score_pln(target, real, polaritas):
    """
    Pencapaian sesuai konvensi NKO PLN (verified dari sheet KINERJA UP3):
      Pol 3 (Positif): min(real/target x 100, 110)
      Pol 1 (Negatif): min((2 - real/target) x 100, 110)
      Pol 2 (Range):   real dlm rentang -> 110 (berdasar 1 sampel NKO;
                       di luar rentang pakai jarak ke batas terdekat)
    Return None kalau data tidak lengkap.
    """
    if real is None:
        return None

    if polaritas == 2:
        rng = _parse_range(target)
        if rng is None:
            return None
        lo, hi = rng
        if lo <= real <= hi:
            return PLN_CAP
        # Di luar rentang: proporsional thd batas terdekat (asumsi, belum
        # terverifikasi NKO -- baru 1 sampel polaritas 2 di file sumber)
        edge = lo if real < lo else hi
        if edge == 0:
            return None
        return max(0.0, min((1 - abs(real - edge) / edge) * 100, PLN_CAP))

    t = _num(target) if not isinstance(target, (int, float)) else float(target)
    if t is None or t == 0:
        return None

    if polaritas == 3:
        raw = (real / t) * 100
    elif polaritas == 1:
        raw = (2 - real / t) * 100
    else:
        return None
    return max(0.0, min(raw, PLN_CAP))


def _nilai_pln(pencapaian, bobot):
    """NILAI = min(Pencapaian, 100) x Bobot / 100. GAP = sisa ke bobot penuh."""
    if pencapaian is None or bobot is None:
        return None, None
    nilai = min(pencapaian, 100.0) * bobot / 100.0
    gap = max(0.0, 100.0 - pencapaian) * bobot / 100.0
    return nilai, gap


def build_pencapaian_pln_chart(rows: list[dict], month_label: str,
                               bg: str = "#FFFFFF") -> plt.Figure:
    """
    Horizontal bar pencapaian per metric versi konvensi NKO PLN.
    rows: list of dict {label, pencapaian, nilai, bobot, polaritas}
    Garis referensi di 100% (target) dan 110% (cap NKO).
    """
    valid = [r for r in rows if r["pencapaian"] is not None]

    fig, ax = plt.subplots(figsize=(12, 5.5), dpi=100)
    fig.patch.set_facecolor(bg)
    ax.set_facecolor(bg)

    if not valid:
        ax.text(0.5, 0.5, "Belum ada data pencapaian", ha="center", va="center",
                transform=ax.transAxes, color="#8B6F5C", fontsize=14)
        ax.axis("off")
        return fig

    valid.sort(key=lambda r: r["pencapaian"])
    labels = [r["label"] for r in valid]
    pcts = [r["pencapaian"] for r in valid]
    colors = ["#4A9D5B" if p >= 100 else "#E8A317" if p >= 90 else "#B84F28"
              for p in pcts]

    bars = ax.barh(labels, pcts, color=colors, edgecolor="#5F2C17",
                   linewidth=0.6, height=0.62)

    for bar, r in zip(bars, valid):
        p = r["pencapaian"]
        nilai_txt = (f"  {p:.2f}%  ·  Nilai {r['nilai']:.1f}/{r['bobot']}"
                     if r["nilai"] is not None else f"  {p:.2f}%")
        ax.text(bar.get_width() + 1.2, bar.get_y() + bar.get_height() / 2,
                nilai_txt, va="center", fontweight="bold", fontsize=9.5,
                color="#4A2812")

    ax.axvline(100, color="#5F2C17", linestyle="--", linewidth=1.4, alpha=0.7)
    ax.axvline(PLN_CAP, color="#B84F28", linestyle=":", linewidth=1.6, alpha=0.9)
    ax.text(100, len(valid) - 0.28, " Target 100%", color="#5F2C17",
            fontsize=8.5, fontweight="bold", va="bottom", ha="left", rotation=90)
    ax.text(PLN_CAP, len(valid) - 0.28, f" Cap NKO {PLN_CAP:.0f}%", color="#B84F28",
            fontsize=8.5, fontweight="bold", va="bottom", ha="left", rotation=90)

    ax.set_title(f"Pencapaian KPI (Konvensi NKO PLN) — {month_label}",
                 fontsize=14, fontweight="bold", color="#5F2C17", pad=14)
    ax.set_xlabel("Pencapaian (%) — capped 110%", color="#4A2812", fontsize=11)
    ax.tick_params(colors="#4A2812")
    ax.set_xlim(0, 132)
    ax.grid(True, axis="x", alpha=0.3, linestyle="--")
    ax.set_axisbelow(True)
    for sp in ax.spines.values():
        sp.set_edgecolor("#E8DFD0")

    plt.tight_layout()
    return fig


# =========================================================================
# A4 CANVAS UTILITY
# =========================================================================
A4_W_PX = 1654   # 200 DPI × 8.27 inch
A4_H_PX = 2339   # 200 DPI × 11.69 inch
A4_MARGIN_BG = "#FBF5E8"  # cream margin around content


def fit_to_a4(source: Image.Image, margin_px: int = 100, fill: bool = False) -> Image.Image:
    """
    Fit source ke A4 portrait.
    fill=True: scale exact ke A4 (edge-to-edge, no margin).
    fill=False (default): center dgn cream margin.
    """
    if fill:
        # Aspect ratio template = A4 (0.707), jadi scaling ini lossless
        return source.resize((A4_W_PX, A4_H_PX), Image.LANCZOS)

    canvas = Image.new("RGB", (A4_W_PX, A4_H_PX), A4_MARGIN_BG)
    max_w = A4_W_PX - 2 * margin_px
    max_h = A4_H_PX - 2 * margin_px
    src_w, src_h = source.size
    scale = min(max_w / src_w, max_h / src_h)
    new_w = int(src_w * scale)
    new_h = int(src_h * scale)
    resized = source.resize((new_w, new_h), Image.LANCZOS)
    x = (A4_W_PX - new_w) // 2
    y = (A4_H_PX - new_h) // 2
    canvas.paste(resized, (x, y))
    return canvas


def figure_to_png_bytes(fig: plt.Figure) -> bytes:
    buf = io.BytesIO()
    fig.savefig(buf, format="PNG", dpi=200, bbox_inches="tight", facecolor=fig.get_facecolor())
    return buf.getvalue()


def bytes_to_pil(b: bytes) -> Image.Image:
    return Image.open(io.BytesIO(b)).convert("RGB")


# =========================================================================
# VIZ 1 — HEATMAP ACHIEVEMENT
# =========================================================================
def build_heatmap(_df: pd.DataFrame, current_month: str, bg: str = "#FFFFFF") -> plt.Figure:
    month_rows: dict[str, pd.Series] = {}
    for _, r in _df.iterrows():
        mv = str(r.get(MONTH_COLUMN, "")).strip()
        if not mv or " " not in mv:
            continue
        parts = mv.split()
        if len(parts) != 2 or not parts[1].isdigit():
            continue
        month_rows[parts[0]] = r

    metric_labels = [lbl for _, lbl, _, _ in METRICS_TOP]
    bulan_labels = [m for m in MONTH_ORDER if m in month_rows]
    matrix = np.full((len(metric_labels), len(bulan_labels)), np.nan)

    for i, (mk, _, _, lower) in enumerate(METRICS_TOP):
        for j, bulan in enumerate(bulan_labels):
            r = month_rows[bulan]
            t = _num(r.get(COLUMN_MAP.get(f"{mk}_target")))
            v = _num(r.get(COLUMN_MAP.get(f"{mk}_realisasi")))
            sc = _score(t, v, lower)
            if sc is not None:
                matrix[i, j] = sc

    fig, ax = plt.subplots(figsize=(12, 5), dpi=100)
    fig.patch.set_facecolor(bg)
    ax.set_facecolor(bg)

    cmap = mcolors.LinearSegmentedColormap.from_list("danantara_rg",
                                                     ["#B84F28", "#E8A317", "#4A9D5B"])
    norm = mcolors.Normalize(vmin=50, vmax=150)
    im = ax.imshow(matrix, cmap=cmap, norm=norm, aspect="auto")

    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            val = matrix[i, j]
            if np.isnan(val):
                ax.text(j, i, "—", ha="center", va="center", color="#8B6F5C", fontsize=10)
            else:
                tc = "white" if val < 75 or val > 130 else "#4A2812"
                ax.text(j, i, f"{val:.0f}%", ha="center", va="center",
                        color=tc, fontsize=10, fontweight="bold")

    ax.set_xticks(range(len(bulan_labels)))
    ax.set_xticklabels(bulan_labels, fontsize=11, color="#4A2812")
    ax.set_yticks(range(len(metric_labels)))
    ax.set_yticklabels(metric_labels, fontsize=11, color="#4A2812", fontweight="bold")

    hm = current_month.split()[0]
    if hm in bulan_labels:
        idx = bulan_labels.index(hm)
        ax.axvspan(idx - 0.5, idx + 0.5, fill=False, edgecolor="#5F2C17", linewidth=2.5, zorder=3)

    ax.set_title("Achievement Kinerja — Realisasi vs Target 2026",
                 fontsize=14, fontweight="bold", color="#5F2C17", pad=14)
    ax.tick_params(axis="both", which="both", length=0)
    for sp in ax.spines.values():
        sp.set_edgecolor("#E8DFD0")

    cbar = fig.colorbar(im, ax=ax, pad=0.02, aspect=25)
    cbar.set_label("Achievement %", color="#5F2C17", fontweight="bold")
    cbar.ax.tick_params(colors="#4A2812")
    cbar.outline.set_edgecolor("#E8DFD0")

    plt.tight_layout()
    return fig


# =========================================================================
# VIZ 2 — RANKING BULAN
# =========================================================================
def build_ranking_bar(_df: pd.DataFrame, metric_key: str, metric_label: str, unit: str,
                     bg: str = "#FFFFFF") -> plt.Figure:
    col_real = COLUMN_MAP.get(f"{metric_key}_realisasi")
    data = []
    for _, r in _df.iterrows():
        mv = str(r.get(MONTH_COLUMN, "")).strip()
        if not mv or " " not in mv:
            continue
        parts = mv.split()
        if len(parts) != 2 or not parts[1].isdigit():
            continue
        val = _num(r.get(col_real))
        if val is not None:
            data.append((parts[0], val))

    if not data:
        fig, ax = plt.subplots(figsize=(12, 5), dpi=100)
        fig.patch.set_facecolor(bg)
        ax.text(0.5, 0.5, "Belum ada data realisasi", ha="center", va="center",
                transform=ax.transAxes, color="#8B6F5C", fontsize=14)
        ax.axis("off")
        return fig

    data.sort(key=lambda x: x[1], reverse=True)
    labels = [d[0] for d in data]
    values = [d[1] for d in data]

    fig, ax = plt.subplots(figsize=(12, 5.5), dpi=100)
    fig.patch.set_facecolor(bg)
    ax.set_facecolor(bg)

    n = len(labels)
    colors = plt.cm.Greens(np.linspace(0.35, 0.85, n))
    bars = ax.bar(labels, values, color=colors, edgecolor="#3A5F3A", linewidth=0.5)

    ymax = max(values)
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + ymax * 0.015,
                _fmt_num_id(val, 2), ha="center", va="bottom",
                fontweight="bold", fontsize=9, color="#2A4A2A")

    ax.set_title(f"Ranking Bulan — Realisasi {metric_label} ({unit}) 2026",
                 fontsize=14, fontweight="bold", color="#5F2C17", pad=14)
    ax.set_xlabel("Bulan", color="#4A2812", fontsize=11)
    ax.set_ylabel(f"Realisasi ({unit})", color="#4A2812", fontsize=11)
    ax.tick_params(colors="#4A2812")
    ax.grid(True, axis="y", alpha=0.3, linestyle="--")
    ax.set_axisbelow(True)
    for sp in ax.spines.values():
        sp.set_edgecolor("#E8DFD0")
    ax.set_ylim(0, ymax * 1.15)

    plt.tight_layout()
    return fig


# =========================================================================
# VIZ 3 — ASET HORIZONTAL
# =========================================================================
def build_aset_horizontal(_df: pd.DataFrame, bg: str = "#FFFFFF") -> plt.Figure:
    data = []
    for key, label, unit in ASETS:
        col_25 = COLUMN_MAP.get(f"{key}_2025")
        col_26 = COLUMN_MAP.get(f"{key}_2026")
        v25 = None
        v26 = None
        for _, r in _df.iterrows():
            if v25 is None:
                x = _num(r.get(col_25))
                if x is not None:
                    v25 = x
            if v26 is None:
                x = _num(r.get(col_26))
                if x is not None:
                    v26 = x
            if v25 is not None and v26 is not None:
                break
        if v25 and v26 and v25 > 0:
            growth = ((v26 - v25) / v25) * 100
            data.append((f"{label} ({unit})", v25, v26, growth))

    if not data:
        fig, ax = plt.subplots(figsize=(12, 5), dpi=100)
        fig.patch.set_facecolor(bg)
        ax.text(0.5, 0.5, "Belum ada data aset", ha="center", va="center",
                transform=ax.transAxes, color="#8B6F5C", fontsize=14)
        ax.axis("off")
        return fig

    data.sort(key=lambda x: x[3], reverse=True)
    labels = [d[0] for d in data]
    growths = [d[3] for d in data]
    v25s = [d[1] for d in data]
    v26s = [d[2] for d in data]

    fig, ax = plt.subplots(figsize=(12, 5.5), dpi=100)
    fig.patch.set_facecolor(bg)
    ax.set_facecolor(bg)

    n = len(labels)
    colors = plt.cm.Oranges(np.linspace(0.5, 0.85, n))
    bars = ax.barh(labels, growths, color=colors, edgecolor="#7A2500", linewidth=0.5)

    xmax = max(growths) if growths else 1
    for bar, g, v25, v26 in zip(bars, growths, v25s, v26s):
        sign = "+" if g >= 0 else ""
        ax.text(bar.get_width() + xmax * 0.02, bar.get_y() + bar.get_height() / 2,
                f"{sign}{g:.2f}%  ({_fmt_num_id(v25, 0)} → {_fmt_num_id(v26, 0)})",
                va="center", fontweight="bold", fontsize=9, color="#4A2812")

    ax.set_title("Pertumbuhan Aset Infrastruktur — 2025 → 2026",
                 fontsize=14, fontweight="bold", color="#5F2C17", pad=14)
    ax.set_xlabel("Growth (%)", color="#4A2812", fontsize=11)
    ax.tick_params(colors="#4A2812")
    ax.invert_yaxis()
    ax.grid(True, axis="x", alpha=0.3, linestyle="--")
    ax.set_axisbelow(True)
    for sp in ax.spines.values():
        sp.set_edgecolor("#E8DFD0")
    ax.set_xlim(0, xmax * 1.35)

    plt.tight_layout()
    return fig


# =========================================================================
# VIZ 4 — TREND AREA + PEAK
# =========================================================================
def build_area_trend(_df: pd.DataFrame, metric_key: str, metric_label: str, unit: str,
                     bg: str = "#FFFFFF") -> plt.Figure:
    col_real = COLUMN_MAP.get(f"{metric_key}_realisasi")
    col_tgt  = COLUMN_MAP.get(f"{metric_key}_target")
    col_25   = COLUMN_MAP.get(f"{metric_key}_2025")

    data = []
    for _, r in _df.iterrows():
        mv = str(r.get(MONTH_COLUMN, "")).strip()
        if not mv or " " not in mv:
            continue
        parts = mv.split()
        if len(parts) != 2 or not parts[1].isdigit():
            continue
        data.append((parts[0], _num(r.get(col_real)), _num(r.get(col_tgt)), _num(r.get(col_25))))

    if not data:
        fig, ax = plt.subplots(figsize=(14, 5), dpi=100)
        fig.patch.set_facecolor(bg)
        ax.text(0.5, 0.5, "Belum ada data untuk metric ini", ha="center", va="center",
                transform=ax.transAxes, color="#8B6F5C", fontsize=14)
        ax.axis("off")
        return fig

    x = list(range(len(data)))
    real_vals = [d[1] for d in data]
    tgt_vals  = [d[2] for d in data]
    r25_vals  = [d[3] for d in data]
    labels = [d[0] for d in data]

    fig, ax = plt.subplots(figsize=(14, 5.5), dpi=100)
    fig.patch.set_facecolor(bg)
    ax.set_facecolor(bg)

    real_np = np.array(real_vals, dtype=float)
    if np.any(~np.isnan(real_np)):
        ax.fill_between(x, real_np, alpha=0.35, color="#B84F28", label="Realisasi 2026")
        ax.plot(x, real_np, marker="o", linewidth=2.5, color="#7A2500",
                markerfacecolor="#FBF5E8", markeredgecolor="#5F2C17", markersize=7, zorder=3)

    tgt_np = np.array(tgt_vals, dtype=float)
    if np.any(~np.isnan(tgt_np)):
        ax.plot(x, tgt_np, "--", color="#E8A317", linewidth=1.8, alpha=0.85, label="Target 2026")

    r25_np = np.array(r25_vals, dtype=float)
    if np.any(~np.isnan(r25_np)):
        ax.plot(x, r25_np, ":", color="#8B6F5C", linewidth=1.5, alpha=0.75, label="Realisasi 2025")

    valid = [(i, v) for i, v in enumerate(real_vals) if v is not None]
    if valid:
        peak_i, peak_v = max(valid, key=lambda t: t[1])
        peak_month = labels[peak_i]
        text_offset = -2 if peak_i > len(x) * 0.7 else 1.5
        ax.annotate(
            f"Puncak: {peak_month}\n{_fmt_num_id(peak_v, 2)} {unit}",
            xy=(peak_i, peak_v),
            xytext=(peak_i + text_offset, peak_v),
            arrowprops=dict(arrowstyle="->", color="#B84F28", lw=1.5),
            color="#7A2500", fontweight="bold", fontsize=10,
            ha="left" if text_offset > 0 else "right",
        )

    ax.set_xticks(x)
    ax.set_xticklabels(labels, color="#4A2812")
    ax.set_title(f"Trend Realisasi {metric_label} ({unit}) — 2026",
                 fontsize=14, fontweight="bold", color="#5F2C17", pad=14)
    ax.set_xlabel("Bulan", color="#4A2812", fontsize=11)
    ax.set_ylabel(f"Nilai ({unit})", color="#4A2812", fontsize=11)
    ax.tick_params(colors="#4A2812")
    ax.grid(True, alpha=0.3, linestyle="--")
    ax.set_axisbelow(True)
    for sp in ax.spines.values():
        sp.set_edgecolor("#E8DFD0")
    ax.legend(loc="upper left", frameon=True, facecolor=bg, edgecolor="#E8DFD0")

    plt.tight_layout()
    return fig


# =========================================================================
# UI STATE
# =========================================================================
if "ranking_metric" not in st.session_state:
    st.session_state.ranking_metric = "PENJUALAN (GWh)"
if "trend_metric" not in st.session_state:
    st.session_state.trend_metric = "PENJUALAN (GWh)"

def _resolve_metric(label: str) -> tuple[str, str, str]:
    for mk, mlabel, munit, _ in METRICS_TOP:
        if f"{mlabel} ({munit})" == label:
            return mk, mlabel, munit
    return METRICS_TOP[0][0], METRICS_TOP[0][1], METRICS_TOP[0][2]


# =========================================================================
# PRA-HITUNG: CHART PNG & PDF LENGKAP (dipakai lintas tab)
# =========================================================================
safe_name = selected_month.replace(" ", "_").replace("/", "-").lower()

png_template = image_to_png_bytes(img_template)
pdf_template_only = image_to_pdf_bytes(img_template)

ranking_mk, ranking_lbl, ranking_unit = _resolve_metric(st.session_state.ranking_metric)
trend_mk, trend_lbl, trend_unit = _resolve_metric(st.session_state.trend_metric)

fig_h = build_heatmap(df, selected_month, bg=CHART_BG)
heat_png = figure_to_png_bytes(fig_h)
plt.close(fig_h)

fig_r = build_ranking_bar(df, ranking_mk, ranking_lbl, ranking_unit, bg=CHART_BG)
rank_png = figure_to_png_bytes(fig_r)
plt.close(fig_r)

fig_a = build_aset_horizontal(df, bg=CHART_BG)
aset_png = figure_to_png_bytes(fig_a)
plt.close(fig_a)

fig_t = build_area_trend(df, trend_mk, trend_lbl, trend_unit, bg=CHART_BG)
trend_png = figure_to_png_bytes(fig_t)
plt.close(fig_t)

# Page 1 pakai preferensi fill; page 2-5 selalu pakai margin cream
pages_a4 = [
    fit_to_a4(img_template, fill=infografis_full_page),
    fit_to_a4(bytes_to_pil(heat_png)),
    fit_to_a4(bytes_to_pil(rank_png)),
    fit_to_a4(bytes_to_pil(aset_png)),
    fit_to_a4(bytes_to_pil(trend_png)),
]
pdf_buf = io.BytesIO()
pages_a4[0].save(pdf_buf, format="PDF", save_all=True,
                 append_images=pages_a4[1:], resolution=200.0)
pdf_lengkap_bytes = pdf_buf.getvalue()


# =========================================================================
# PANEL UNDUH (dirender di setiap tab, key unik per tab via key_suffix)
# =========================================================================
def render_download_panel(key_suffix: str) -> None:
    with st.container(border=True):
        st.markdown('<div class="sec-title">⬇️ Unduh Utama</div>', unsafe_allow_html=True)

        st.download_button(
            "Export PNG Infografis 🖼️",
            data=png_template,
            file_name=f"outlook_infografis_{safe_name}.png",
            mime="image/png",
            use_container_width=True,
            key=f"dl_png_tpl_{key_suffix}",
        )

        st.download_button(
            "📄 PDF Infografis (1 halaman)",
            data=pdf_template_only,
            file_name=f"outlook_infografis_{safe_name}.pdf",
            mime="application/pdf",
            use_container_width=True,
            help="Hanya infografis dlm 1 halaman PDF, ukuran native template (300 DPI, quality maksimal).",
            key=f"dl_pdf_tpl_{key_suffix}",
        )

        st.download_button(
            "📄 Lengkap (5 halaman A4) PDF",
            data=pdf_lengkap_bytes,
            file_name=f"outlook_lengkap_{safe_name}.pdf",
            mime="application/pdf",
            use_container_width=True,
            help=f"Page 1: infografis ({'full-page' if infografis_full_page else 'dgn margin cream'}). "
                 f"Page 2-5: 4 visualisasi dgn margin cream. Chart bg: {'putih' if chart_bg_white else 'cream'}.",
            key=f"dl_pdf_full_{key_suffix}",
        )


# =========================================================================
# TABS
# =========================================================================
tab_preview, tab_target, tab_trend, tab_debug = st.tabs(
    ["🖼️ Preview & Unduh", "🎯 Target vs Realisasi", "📈 Analisis Trend & Visualisasi", "🐞 Debug"]
)

# -------------------------------------------------------------------------
# TAB 1 — Preview & Unduh
# -------------------------------------------------------------------------
with tab_preview:
    col_left, col_right = st.columns([2, 1], gap="large")

    with col_left:
        with st.container(border=True):
            st.markdown(f'<div class="sec-title">🖼️ Preview Infografis — {selected_month}</div>', unsafe_allow_html=True)
            st.image(img_template, use_container_width=True)

    with col_right:
        with st.container(border=True):
            st.markdown('<div class="sec-title">📊 KPI Utama Bulan Ini</div>', unsafe_allow_html=True)
            for mk, mlabel, munit, _ in METRICS_TOP[:3]:
                real = formatted.get(f"{mk}_realisasi", "-")
                tgt  = formatted.get(f"{mk}_target", "-")
                st.markdown(
                    f"""
<div class="kpi-mini">
    <div class="kpi-label">{mlabel} <span style="text-transform:none;color:#A6836E;">({munit})</span></div>
    <div class="kpi-val">{real}</div>
    <div class="kpi-tgt">Target: <strong>{tgt}</strong></div>
</div>
""", unsafe_allow_html=True)

        render_download_panel("preview")

# -------------------------------------------------------------------------
# TAB 2 — Target vs Realisasi
# -------------------------------------------------------------------------
with tab_target:
    col_left, col_right = st.columns([3, 1], gap="large")

    with col_left:
        # ---- hitung pencapaian PLN utk semua metric (dipakai bar + chart) ----
        pln_rows = []
        for mk, mlabel, munit, _lower in METRICS_TOP:
            pol, bobot = METRICS_PLN[mk]
            tn = _num(values.get(f"{mk}_target"))
            rn = _num(values.get(f"{mk}_realisasi"))
            raw_target = values.get(f"{mk}_target")  # utk polaritas 2 (range string)
            pct = _score_pln(raw_target if pol == 2 else tn, rn, pol)
            nilai, gap = _nilai_pln(pct, bobot)
            pln_rows.append({
                "key": mk, "label": mlabel, "unit": munit,
                "polaritas": pol, "bobot": bobot,
                "target": tn, "real": rn,
                "pencapaian": pct, "nilai": nilai, "gap": gap,
            })

        with st.container(border=True):
            st.markdown('<div class="sec-title">🎯 Target vs Realisasi — Konvensi NKO PLN</div>', unsafe_allow_html=True)
            st.markdown(
                '<div class="sec-sub">Pencapaian dihitung sesuai polaritas NKO: '
                'Pol 3 Positif = real/target · Pol 1 Negatif = (2 − real/target) · '
                'semua di-cap 110%. Hijau ≥ 100% · Kuning 90–99% · Oranye &lt; 90%.</div>',
                unsafe_allow_html=True,
            )
            for r in pln_rows:
                pct = r["pencapaian"]
                if pct is None:
                    color, pct_str, bar_w = "#A6836E", "—", 0.0
                elif pct >= 100:
                    color, pct_str, bar_w = "#4A9D5B", f"{pct:.2f}%", min(100.0, pct / 1.1)
                elif pct >= 90:
                    color, pct_str, bar_w = "#E8A317", f"{pct:.2f}%", pct / 1.1
                else:
                    color, pct_str, bar_w = "#B84F28", f"{pct:.2f}%", pct / 1.1

                pol_badge = {3: "↑ Positif", 1: "↓ Negatif", 2: "⇅ Range"}[r["polaritas"]]
                nilai_str = (f"Nilai: <strong>{r['nilai']:.2f}</strong> / {r['bobot']}"
                             if r["nilai"] is not None else f"Bobot: {r['bobot']}")
                capped_note = " · capped" if pct is not None and pct >= PLN_CAP else ""

                st.markdown(
                    f"""
<div class="metric-row">
    <div class="metric-row-head">
        <div class="metric-name">{r['label']} <span style="color:#A6836E;font-weight:400;font-size:0.8rem;">· {r['unit']} · Pol {r['polaritas']} {pol_badge} · Bobot {r['bobot']}</span></div>
        <div class="metric-pct" style="color:{color};">{pct_str}<span style="font-size:0.7rem;color:#A6836E;">{capped_note}</span></div>
    </div>
    <div class="bar-outer"><div class="bar-inner" style="width:{bar_w}%; background:{color};"></div></div>
    <div class="metric-nums">
        <span>Target: <strong style="color:#4A2812;">{formatted.get(f"{r['key']}_target", "-")}</strong></span>
        <span>{nilai_str}</span>
        <span>Realisasi: <strong style="color:{color};">{formatted.get(f"{r['key']}_realisasi", "-")}</strong></span>
    </div>
</div>
""", unsafe_allow_html=True)

            # ---- ringkasan total nilai (6 KPI dashboard, bukan total NKO) ----
            got = [r for r in pln_rows if r["nilai"] is not None]
            if got:
                tot_nilai = sum(r["nilai"] for r in got)
                tot_bobot = sum(r["bobot"] for r in got)
                st.markdown(
                    f"""
<div style="margin-top:0.5rem;padding:0.7rem 1rem;background:#F5E9D3;border-radius:10px;
            border-left:4px solid #5F2C17;color:#4A2812;font-size:0.9rem;">
    Total Nilai <strong>{tot_nilai:.2f}</strong> dari bobot <strong>{tot_bobot}</strong>
    ({len(got)} KPI infografis — bukan total NKO penuh, NKO punya {100} bobot dgn KPI lain di luar dashboard ini)
</div>
""", unsafe_allow_html=True)

        # ---- visualisasi pencapaian PLN ----
        with st.container(border=True):
            st.markdown('<div class="sec-title">📊 Visualisasi Pencapaian — NKO PLN</div>', unsafe_allow_html=True)
            st.markdown(
                '<div class="sec-sub">Garis putus2 coklat = target 100% · garis titik2 merah = cap NKO 110%. '
                'Label kanan: pencapaian & nilai/bobot.</div>',
                unsafe_allow_html=True,
            )
            fig_pln = build_pencapaian_pln_chart(pln_rows, selected_month, bg=CHART_BG)
            pln_png = figure_to_png_bytes(fig_pln)
            plt.close(fig_pln)
            st.image(pln_png, use_container_width=True)
            st.download_button(
                "Export PNG chart ini (Pencapaian NKO)⬇️",
                data=pln_png,
                file_name=f"pencapaian_nko_{selected_month.replace(' ', '_').lower()}.png",
                mime="image/png",
                key="dl_pencapaian_pln",
            )

    with col_right:
        render_download_panel("target")

# -------------------------------------------------------------------------
# TAB 3 — Analisis Trend (Heatmap, Ranking, Aset, Trend Area)
# -------------------------------------------------------------------------
with tab_trend:
    col_left, col_right = st.columns([3, 1], gap="large")

    with col_left:
        with st.container(border=True):
            st.markdown('<div class="sec-title">🔥 Heatmap Achievement — 12 Bulan × 6 Metric</div>', unsafe_allow_html=True)
            st.markdown('<div class="sec-sub">Border coklat menyorot bulan aktif. Cell "—" berarti data belum ada.</div>',
                        unsafe_allow_html=True)
            st.image(heat_png, use_container_width=True)
            st.download_button(
                "Export PNG chart ini (Heatmap)⬇️ ",
                data=heat_png,
                file_name=f"heatmap_achievement_{selected_month.split()[1]}.png",
                mime="image/png",
                key="dl_heatmap",
            )

        with st.container(border=True):
            st.markdown('<div class="sec-title">📊 Ranking Bulan — Realisasi</div>', unsafe_allow_html=True)
            st.markdown('<div class="sec-sub">Urutan bulan dari realisasi tertinggi ke terendah untuk metric yg dipilih.</div>',
                        unsafe_allow_html=True)
            st.selectbox(
                "Pilih metric",
                [f"{lbl} ({unit})" for _, lbl, unit, _ in METRICS_TOP],
                key="ranking_metric",
            )
            st.image(rank_png, use_container_width=True)
            st.download_button(
                " Export PNG chart ini (Ranking)⬇️ ",
                data=rank_png,
                file_name=f"ranking_bulan_{ranking_mk}.png",
                mime="image/png",
                key="dl_ranking",
            )

        with st.container(border=True):
            st.markdown('<div class="sec-title">🏗️ Pertumbuhan Aset Infrastruktur</div>', unsafe_allow_html=True)
            st.markdown('<div class="sec-sub">Growth % dari 2025 ke 2026 untuk 6 kategori aset.</div>',
                        unsafe_allow_html=True)
            st.image(aset_png, use_container_width=True)
            st.download_button(
                "Export PNG chart ini(Aset)⬇️ ",
                data=aset_png,
                file_name="pertumbuhan_aset_2025_2026.png",
                mime="image/png",
                key="dl_aset",
            )

        with st.container(border=True):
            st.markdown('<div class="sec-title">📈 Trend Realisasi Bulanan — Puncak Highlighted</div>', unsafe_allow_html=True)
            st.markdown('<div class="sec-sub">Area = realisasi 2026 · Kuning putus2 = target · Abu titik2 = realisasi 2025.</div>',
                        unsafe_allow_html=True)
            st.selectbox(
                "Pilih metric",
                [f"{lbl} ({unit})" for _, lbl, unit, _ in METRICS_TOP],
                key="trend_metric",
            )
            st.image(trend_png, use_container_width=True)
            st.download_button(
                "Export PNG chart ini(Trend)⬇️",
                data=trend_png,
                file_name=f"trend_area_{trend_mk}.png",
                mime="image/png",
                key="dl_trend",
            )

    with col_right:
        render_download_panel("trend")

# -------------------------------------------------------------------------
# TAB 4 — Debug
# -------------------------------------------------------------------------
with tab_debug:
    col_left, col_right = st.columns([3, 1], gap="large")

    with col_left:
        with st.expander("📋 Semua Nilai Terbaca (raw dari sheet)"):
            show_df = pd.DataFrame({
                "Metric": list(formatted.keys()),
                "Nilai (formatted)": list(formatted.values()),
            })
            st.dataframe(show_df, hide_index=True, use_container_width=True, height=420)

        with st.expander("ℹ️ Debug — kolom & bulan yg terbaca dari CSV"):
            st.write(f"**Bulan terdeteksi ({len(available_months)}):**")
            st.write(available_months)
            st.write("**Kolom di CSV:**")
            st.write(list(df.columns))
            st.dataframe(df.head(15), use_container_width=True)

    with col_right:
        render_download_panel("debug")

# =========================================================================
# FOOTER
# =========================================================================
st.markdown(
    """
<div style="margin-top:2rem;padding:1rem;text-align:center;color:#8B6F5C;font-size:0.8rem;">
    🌸 PLN UP3 Cilacap · Powered by Streamlit + Pillow + Matplotlib
</div>
""",
    unsafe_allow_html=True,
)
