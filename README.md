# Automated Performance Outlook — PLN UP3 Cilacap

Generator infografis kinerja bulanan (Penjualan, SAIDI, SAIFI, ENS, Susut, P2TL, aset) yang membaca data real-time dari Google Sheets dan overlay ke template Canva → export PNG/PDF.

## Struktur

```
dashboard-pln-cilacap/
├── app.py                       # Streamlit UI (main)
├── utils.py                     # Data fetch + PIL render (pure Python)
├── config.py                    # ⭐ SATU-SATUNYA file yg biasa diedit
├── requirements.txt
├── notebook.ipynb               # Colab + ngrok utk dev/demo
├── .streamlit/config.toml       # Tema
└── assets/
    ├── template.png             # Background dari Canva
    └── fonts/DejaVuSans-Bold.ttf
```

## Setup lokal

```bash
git clone https://github.com/surthe49-hub/dashboard-pln-cilacap.git
cd dashboard-pln-cilacap
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Buka http://localhost:8501.

## Deploy PERMANEN (Streamlit Community Cloud)

Ini yang menghasilkan URL tetap, bukan Colab+ngrok.

1. Push repo ke GitHub (sudah).
2. Login ke https://share.streamlit.io dengan akun GitHub.
3. **New app** → pilih repo `dashboard-pln-cilacap`, branch `main`, file `app.py`.
4. Deploy. URL final: `https://<nama-app>.streamlit.app`.

Redeploy otomatis tiap `git push` ke `main`.

## Development / demo cepat (Colab + Ngrok)

Buka `notebook.ipynb` di Google Colab, jalankan cell 1→9 berurutan. URL ngrok muncul di cell 9. **Tidak permanen** — mati saat sesi Colab berakhir.

## Kalibrasi koordinat

Angka default di `config.py` = estimasi. Pertama kali pakai:

1. Jalankan aplikasi.
2. Sidebar → toggle **🛠️ Developer Mode**.
3. Geser slider X/Y tiap metric, lihat preview.
4. Setelah semua pas, scroll ke bawah → **📋 Export Coordinates**.
5. Copy snippet, paste ke `config.py` ganti dict `COORDINATES`.
6. Commit & push. Selesai — tidak perlu kalibrasi lagi.

## Kalau data tidak muncul

Buka expander **ℹ️ Debug** di bawah app. Bandingkan nama kolom di CSV dengan `COLUMN_MAP` di `config.py`. Nama harus sama persis (spasi, kapitalisasi).

Kalau baris bulan tidak ketemu: cek `MONTH_COLUMN` dan pastikan nama bulan di sheet sama dengan yang di `MONTHS`.

## Refresh data

Aplikasi cache 60 detik. Klik tombol **🔄 Refresh** di sidebar untuk bypass cache. `cache_bust=True` di fetcher juga menambahkan timestamp ke URL sehingga Google tidak mengembalikan versi cache lama.
