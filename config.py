# config.py - DIPERBARUI: Font Serif Ber-outline, Posisi, dan Warna yang Presisi

# =========================================================================
# 1. SUMBER DATA
# =========================================================================
CSV_URL = (
    "https://docs.google.com/spreadsheets/d/e/2PACX-1vQrQrjE62V_Eaq9g-00-hsrf-RxcGKQy9fEU1yJwa6-cG5lRGrRChsXb8sjV4NvcHU6l_zxrt_2ER-c/pub?gid=872183623&single=true&output=csv"
  
)

SHEET_HEADER_ROW = 5
MONTH_COLUMN = "OUTLOOK BULAN"

# =========================================================================
# 2. PEMETAAN KOLOM CSV
# =========================================================================
COLUMN_MAP = {
    "penjualan_2025":       "PENJUALAN 2025",
    "penjualan_target":     "PENJUALAN 2026 309 LANGSUNG",
    "penjualan_realisasi":  "PENJUALAN 2026",

    "saidi_2025":           "SAIDI 2025",
    "saidi_target":         "SAIDI 2026",
    "saidi_realisasi":      "SAIDI 2026.1",

    "saifi_2025":           "SAIFI 2025",
    "saifi_target":         "SAIFI 2026",
    "saifi_realisasi":      "SAIFI 2026.1",

    "ens_2025":             "ENS 2025",
    "ens_target":           "ENS 2026",
    "ens_realisasi":        "ENS 2026.1",

    "susut_2025":           "SUSUT 2025",
    "susut_target":         "SUSUT 2026",
    "susut_realisasi":      "SUSUT 2026.1",

    "p2tl_2025":            "P2TL 2025 (MWH)",
    "p2tl_target":          "P2TL 2026 (MWH)",
    "p2tl_realisasi":       "P2TL 2026 (MWH).1",

    "jtm_2025":             "JTM",
    "jtm_2026":             "JTM.1",
    "jtr_2025":             "JTR",
    "jtr_2026":             "JTR.1",
    "gardu_2025":           "GARDU / TRAFO",
    "gardu_2026":           "GARDU / TRAFO.1",
    "penyulang_2025":       "PENYULANG",
    "penyulang_2026":       "PENYULANG.1",
    "pelanggan_2025":       "PELANGGAN (309)",
    "pelanggan_2026":       "PELANGGAN (309).1",
    "daya_2025":            "DAYA TERSAMBUNG (MVA) (309)",
    "daya_2026":            "DAYA TERSAMBUNG (MVA) (309).1",
}

# =========================================================================
# 3. FORMAT ANGKA
# =========================================================================
DECIMAL_METRICS = {
    "penjualan": True,
    "saidi":     True,
    "saifi":     True,
    "ens":       True,
    "susut":     True,
    "p2tl":      True,
    "jtm":       True,
    "jtr":       True,
    "gardu":     False,
    "penyulang": False,
    "pelanggan": False,
    "daya":      True,
}

# =========================================================================
# 4. WARNA
# =========================================================================
YELLOW = "#E8A317"    # kuning-oranye, match "Target | Realisasi" di template
DARK   = "#333333"    # abu gelap default

# --- PERBAIKAN WARNA NAMA BULAN ---
# Warna disampling langsung dari tulisan "2026" di image_0.png
MONTH_FILL    = "#f6e9d8"   # Warna "isi" (fill) huruf - Coklat muda/bata medium
MONTH_OUTLINE = "#652d21"   # Warna "garis luar" (outline) - Coklat tua gelap

# =========================================================================
# 5. TERJEMAHAN NAMA BULAN
# =========================================================================
# Untuk mengubah "Jan" (dari dropdown "Jan 2026") jadi "Januari"
# (Indonesia full name yg muncul di template di sebelah kiri "2026").
MONTH_DISPLAY_ID = {
    # English abbreviations (kalau CSV pakai Aug/Oct/Dec)
    "Jan": "Januari",  "Feb": "Februari",  "Mar": "Maret",
    "Apr": "April",    "May": "Mei",       "Jun": "Juni",
    "Jul": "Juli",     "Aug": "Agustus",   "Sep": "September",
    "Oct": "Oktober",  "Nov": "November",  "Dec": "Desember",
    # Indonesian abbreviations (kalau CSV pakai Agu/Okt/Des)
    "Agu": "Agustus",  "Ags": "Agustus",
    "Okt": "Oktober",  "Des": "Desember",
}

# =========================================================================
# 6. FONT
# =========================================================================
FONT_PATH        = "assets/fonts/DejaVuSans-Bold.ttf"     # default (angka)

# --- PERBAIKAN FONT NAMA BULAN ---
# Diperbarui: Gunakan font Serif tebal dengan outline,
# untuk mencocokkan "2026" di template. (Bukan Pacifico lagi).
# Pastikan Anda memiliki font serif yang sesuai di folder assets/fonts/.
# Contoh di bawah menggunakan font serif fiktif; ganti dengan jalur sebenarnya.
SCRIPT_FONT_PATH = "assets/fonts/Carattere-Regular.ttf"  # Contoh font Serif Bold

# =========================================================================
# 7. KOORDINAT TEKS DI TEMPLATE (X, Y) — px
# =========================================================================
# Format tuple standar (5):  (x, y, anchor, font_size, color)
# Format tuple extended (8): (x, y, anchor, font_size, fill_color, font_path,
#                             stroke_width, stroke_color)
#
# Format extended dipakai kalau butuh outline (misal bulan serif ber-outline).

COORDINATES = {
    # ---- PERBAIKAN NAMA BULAN (8-tuple: pakai serif font + outline + warna sampling) ----
    # Kalibrasi manual:
    # Posisi: x diturunkan menjadi 785 (lebih dekat ke '2026'), y dinaikkan menjadi 222 (agar sejajar secara visual).
    # Anchor: Tetap 'rm' (rata kanan) agar jarak ke '2026' konsisten.
    # Ukuran: Tetap 50.
    # Outline: Ketebalan tetap 2, tetapi warna disampling ulang.
    "month_display": (825, 198, "rm", 65, MONTH_FILL, SCRIPT_FONT_PATH, 5, MONTH_OUTLINE),

    # ---- Kolom kinerja atas (Tidak Berubah) ----
    "penjualan_2025":       (650, 810, "rm", 22, DARK),
    "penjualan_target":     (970, 810, "rm", 22, YELLOW),
    "penjualan_realisasi":  (985, 810, "lm", 22, DARK),

    "saidi_2025":           (650, 885, "rm", 22, DARK),
    "saidi_target":         (970, 885, "rm", 22, YELLOW),
    "saidi_realisasi":      (985, 885, "lm", 22, DARK),

    "saifi_2025":           (650, 956, "rm", 22, DARK),
    "saifi_target":         (970, 956, "rm", 22, YELLOW),
    "saifi_realisasi":      (985, 956, "lm", 22, DARK),

    "ens_2025":             (650, 1027, "rm", 22, DARK),
    "ens_target":           (970, 1027, "rm", 22, YELLOW),
    "ens_realisasi":        (985, 1027, "lm", 22, DARK),

    "susut_2025":           (650, 1097, "rm", 22, DARK),
    "susut_target":         (970, 1097, "rm", 22, YELLOW),
    "susut_realisasi":      (985, 1097, "lm", 22, DARK),

    "p2tl_2025":            (650, 1170, "rm", 22, DARK),
    "p2tl_target":          (970, 1170, "rm", 22, YELLOW),
    "p2tl_realisasi":       (985, 1170, "lm", 22, DARK),

    # ---- Baris aset bawah (Tidak Berubah) ----
    "jtm_2025":             (238, 1457, "mm", 20, YELLOW),
    "jtm_2026":             (238, 1511, "mm", 20, DARK),
    "jtr_2025":             (388, 1457, "mm", 20, YELLOW),
    "jtr_2026":             (388, 1511, "mm", 20, DARK),
    "gardu_2025":           (534, 1457, "mm", 20, YELLOW),
    "gardu_2026":           (534, 1511, "mm", 20, DARK),
    "penyulang_2025":       (684, 1457, "mm", 20, YELLOW),
    "penyulang_2026":       (684, 1511, "mm", 20, DARK),
    "pelanggan_2025":       (834, 1457, "mm", 20, YELLOW),
    "pelanggan_2026":       (834, 1511, "mm", 20, DARK),
    "daya_2025":            (985, 1457, "mm", 20, YELLOW),
    "daya_2026":            (985, 1511, "mm", 20, DARK),
}

# =========================================================================
# 8. TEMPLATE
# =========================================================================
TEMPLATE_PATH = "assets/template.png"
