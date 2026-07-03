"""
utils.py
--------
Fungsi utility: fetch data dari Google Sheets, format angka Indonesia,
render teks ke atas template pakai Pillow.
"""

from __future__ import annotations

import io
import time
from datetime import datetime
from typing import Any

import pandas as pd
import requests
from PIL import Image, ImageDraw, ImageFont

from config import (
    COLUMN_MAP,
    COORDINATES,
    CSV_URL,
    DECIMAL_METRICS,
    FONT_PATH,
    MONTH_COLUMN,
    SHEET_HEADER_ROW,
    TEMPLATE_PATH,
)

# =========================================================================
# KONFIGURASI FILTER BULAN
# =========================================================================
TARGET_YEAR = 2026

_VALID_MONTH_PREFIXES = {
    "jan", "feb", "mar", "apr", "may", "jun", "jul",
    "aug", "sep", "sept", "oct", "nov", "dec",
    "january", "february", "march", "april", "june", "july",
    "august", "september", "october", "november", "december",
    "mei", "agu", "ags", "okt", "des",
    "januari", "februari", "maret", "juni", "juli",
    "agustus", "oktober", "desember",
}

# =========================================================================
# AUTO-SHRINK FONT UNTUK ANGKA PANJANG
# =========================================================================
# Threshold panjang STRING (setelah format, termasuk pemisah titik/koma):
# - ≤ 8 char: font default
# - 9 char: -2
# - 10 char: -4
# - 11+ char: -6
# Aturan berlaku HANYA untuk metric yg key-nya diakhiri "_target".
# Kolom 2025 & realisasi tidak disentuh.
_SHRINK_SUFFIX = "_target"
_SHRINK_TABLE = [
    (5, 0),    # panjang ≤ 5 → -0   (Hasil: 22)
    (6, 1),    # panjang == 6 → -1  (Hasil: 21)
    (7, 0),    # panjang == 7 → -0  (Hasil: 22)
    (8, 2),    # panjang == 8 → -2  (Hasil: 20)  <-- Disesuaikan landai
    (9, 5),    # panjang == 9 → -2  (Hasil: 20)  <-- Diubah ke -2 (Ini untuk format "X.XXX.XXX")
    # 10+ → -10 (ditangani di fallback fungsi bawaanmu, Hasil: 12)
]


def _adjust_font_size(text: str, base_size: int, key: str) -> int:
    """Kembalikan font size disesuaikan panjang teks (khusus metric target)."""
    if not key.endswith(_SHRINK_SUFFIX):
        return base_size
    n = len(text)
    for max_len, reduction in _SHRINK_TABLE:
        if n <= max_len:
            return max(base_size - reduction, 10)
    # Fallback: 11+ karakter
    return max(base_size - 6, 10)


# =========================================================================
# MONTH NORMALIZATION
# =========================================================================
_DATE_FORMATS = [
    "%m/%d/%Y",
    "%d/%m/%Y",
    "%Y-%m-%d",
    "%m-%d-%Y",
    "%d-%m-%Y",
]


def normalize_month(val: Any) -> str:
    if val is None:
        return ""
    s = str(val).strip()
    if not s or s.lower() in {"nan", "none"}:
        return ""
    for fmt in _DATE_FORMATS:
        try:
            dt = datetime.strptime(s, fmt)
            return dt.strftime("%b %Y")
        except ValueError:
            continue
    return s


def _is_valid_month_entry(s: str) -> bool:
    parts = s.strip().split()
    if len(parts) != 2:
        return False
    month_part, year_part = parts
    if not year_part.isdigit() or int(year_part) != TARGET_YEAR:
        return False
    return month_part.lower() in _VALID_MONTH_PREFIXES


# =========================================================================
# DATA
# =========================================================================
def fetch_sheet(cache_bust: bool = True) -> pd.DataFrame:
    url = CSV_URL
    if cache_bust:
        url = f"{url}&_={int(time.time())}"

    resp = requests.get(url, timeout=30)
    resp.raise_for_status()

    df = pd.read_csv(
        io.StringIO(resp.text),
        header=SHEET_HEADER_ROW,
        skip_blank_lines=False,
    )
    df.columns = [str(c).strip() for c in df.columns]
    df = df.dropna(how="all")

    if MONTH_COLUMN in df.columns:
        df[MONTH_COLUMN] = df[MONTH_COLUMN].apply(normalize_month)

    return df


def get_available_months(df: pd.DataFrame) -> list[str]:
    if MONTH_COLUMN not in df.columns:
        raise KeyError(
            f"Kolom '{MONTH_COLUMN}' tidak ada di CSV. "
            f"Kolom yg tersedia: {list(df.columns)}"
        )
    raw = df[MONTH_COLUMN].astype(str).str.strip().tolist()
    seen: set[str] = set()
    ordered: list[str] = []
    for m in raw:
        if m and _is_valid_month_entry(m) and m not in seen:
            seen.add(m)
            ordered.append(m)
    return ordered


def get_row_for_month(df: pd.DataFrame, month: str) -> pd.Series | None:
    if MONTH_COLUMN not in df.columns:
        raise KeyError(
            f"Kolom '{MONTH_COLUMN}' tidak ada di CSV. "
            f"Kolom yg tersedia: {list(df.columns)}"
        )
    target = month.strip().lower()
    normalized = df[MONTH_COLUMN].astype(str).str.strip().str.lower()
    matches = df[normalized == target]
    if matches.empty:
        return None
    return matches.iloc[0]


def extract_values(row: pd.Series) -> dict[str, Any]:
    values: dict[str, Any] = {}
    for metric_key, csv_col in COLUMN_MAP.items():
        if csv_col in row.index:
            values[metric_key] = row[csv_col]
        else:
            values[metric_key] = None
    return values


# =========================================================================
# FORMATTING
# =========================================================================
def _metric_base(metric_key: str) -> str:
    return metric_key.rsplit("_", 1)[0]


def format_id(value: Any, is_decimal: bool) -> str:
    if value is None:
        return "-"
    try:
        s = str(value).strip()
        if s == "" or s.lower() in {"nan", "none", "-"}:
            return "-"
        s_norm = s.replace(".", "").replace(",", ".") if "," in s else s
        num = float(s_norm)
    except (ValueError, TypeError):
        return str(value)

    if is_decimal:
        formatted = f"{num:,.2f}"
        formatted = formatted.replace(",", "X").replace(".", ",").replace("X", ".")
        return formatted
    else:
        formatted = f"{int(round(num)):,}"
        return formatted.replace(",", ".")


def format_all(values: dict[str, Any]) -> dict[str, str]:
    out: dict[str, str] = {}
    for k, v in values.items():
        base = _metric_base(k)
        is_decimal = DECIMAL_METRICS.get(base, False)
        out[k] = format_id(v, is_decimal)
    return out


# =========================================================================
# RENDER
# =========================================================================
def _load_font(size: int, path: str = FONT_PATH) -> ImageFont.FreeTypeFont:
    """Load font dari path. Fallback ke FONT_PATH default, lalu default PIL."""
    try:
        return ImageFont.truetype(path, size=size)
    except OSError:
        try:
            return ImageFont.truetype(FONT_PATH, size=size)
        except OSError:
            return ImageFont.load_default()


def _unpack_coord_spec(spec: tuple) -> dict:
    """
    Support tuple 5 & 8 element:
      5: (x, y, anchor, size, color)
      8: (x, y, anchor, size, fill, font_path, stroke_width, stroke_color)
    Return dict dgn semua field terisi (defaults sesuai FONT_PATH utk 5-tuple).
    """
    d = {
        "x": spec[0],
        "y": spec[1],
        "anchor": spec[2],
        "size": spec[3],
        "color": spec[4],
        "font_path": FONT_PATH,
        "stroke_width": 0,
        "stroke_color": None,
    }
    if len(spec) >= 8:
        d["font_path"] = spec[5]
        d["stroke_width"] = spec[6]
        d["stroke_color"] = spec[7]
    return d


def render_image(
    formatted: dict[str, str],
    coord_override: dict[str, tuple] | None = None,
) -> Image.Image:
    img = Image.open(TEMPLATE_PATH).convert("RGB")
    draw = ImageDraw.Draw(img)

    for key, spec in COORDINATES.items():
        cfg = _unpack_coord_spec(spec)
        x, y = cfg["x"], cfg["y"]
        if coord_override and key in coord_override:
            x, y = coord_override[key]

        text = formatted.get(key, "-")
        adjusted_size = _adjust_font_size(text, cfg["size"], key)
        font = _load_font(adjusted_size, cfg["font_path"])

        draw_kwargs = {"font": font, "fill": cfg["color"]}
        if cfg["stroke_width"] > 0 and cfg["stroke_color"]:
            draw_kwargs["stroke_width"] = cfg["stroke_width"]
            draw_kwargs["stroke_fill"] = cfg["stroke_color"]

        try:
            draw.text((x, y), text, anchor=cfg["anchor"], **draw_kwargs)
        except ValueError:
            draw.text((x, y), text, **draw_kwargs)

    return img


# =========================================================================
# EXPORT
# =========================================================================
def image_to_png_bytes(img: Image.Image) -> bytes:
    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()


def image_to_pdf_bytes(img: Image.Image) -> bytes:
    buf = io.BytesIO()
    img.convert("RGB").save(buf, format="PDF", resolution=300.0)
    return buf.getvalue()