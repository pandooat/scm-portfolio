# SCM Portfolio Starter Kit | Untuk Google Data Analytics Certificate Holder (Pemula)

> **SELURUH DATA ADALAH SINTETIS / SIMULASI.** Perusahaan, supplier, customer, order, stock, biaya, dan semua angka di paket ini fiktif. Tujuannya untuk portofolio belajar dan persiapan interview, bukan analisis operasional perusahaan nyata.

## Mulai dari sini: 3 langkah

1. **Buka `06_Career/HARI_PERTAMA_90_MENIT.md`**. Tutorial ini bisa dilakukan dengan DB Browser for SQLite; Python belum wajib.
2. **Buka `02_Database/scm_portfolio.sqlite`** menggunakan DB Browser for SQLite: https://sqlitebrowser.org/
3. **Lanjutkan ke modul baru** `03_SQL/MODUL_2_SQL_SCM_MINGGU_1_2.md` (latihan 7 hari), dan periksa jawaban dalam `03_SQL/PRAKTIK_MINGGU_1_2_JAWABAN.sql`. Setelah itu pelajari `03_SQL/solutions_16_queries.sql` dan `03_SQL/LATIHAN_SQL_PEMULA.md`.

Untuk progres belajar, buka workbook `SCM_12_Week_Learning_Tracker.xlsx` di folder utama, lalu pilih kegiatan mingguan dan isi status.

## Isi folder

```text
SCM_Portfolio_Starter/
├── README_MULAI_DI_SINI.md
├── 00_PROJECT_BRIEF.md
├── SCM_12_Week_Learning_Tracker.xlsx
├── 01_Data/              9 CSV + DATA_DICTIONARY.md
├── 02_Database/          scm_portfolio.sqlite + schema.sql
├── 03_SQL/               modul lanjutan 7 hari + 10 query tervalidasi + 16 solved SQL + daftar latihan
├── 04_Python/            generate_data.py, analyze_scm.py, replenishment_scenarios.py, 2 files pengujian
├── 05_PowerBI/           DAX measures + data model + tutorial step-by-step
├── 06_Career/            road map, interview, CV/GitHub, hari pertama
└── 07_Reports/           contoh KPI, forecast backtest, dan skenario reorder point untuk dataset simulasi
```

## Apa yang sudah ada, dan apa yang harus Anda buat sendiri?

**Sudah siap:** CSV, database SQLite, script Python, SQL examples, KPI report simulasi, dekomposisi OTIF, baseline forecast, skenario reorder point, 12 tes kualitas/perhitungan, roadmap, petunjuk Power BI.

**Anda buat sendiri untuk skill assessment:** file `.pbix` melalui Power BI Desktop, dashboard screenshot, penjelasan analisis pribadi, hipotesis, business memo final, dan presentasi interview. Mengikuti tutorial saja bukan bukti penguasaan; latih mengulang tanpa panduan.

## Cara jalankan Python (opsional setelah belajar SQL)

Pada Windows, buka folder proyek di terminal/PowerShell:

```powershell
py 04_Python\test_project.py
py 04_Python\analyze_scm.py
py 04_Python\test_forecast.py
py 04_Python\replenishment_scenarios.py
```

`generate_data.py` akan **membuat ulang dan menimpa** CSV/database yang sudah disediakan. Jalankan hanya jika ingin meregenerasi seluruh data dengan parameter simulasi yang sama:

```powershell
py 04_Python\generate_data.py
py 04_Python\test_project.py
py 04_Python\analyze_scm.py
py 04_Python\replenishment_scenarios.py
```

Tanpa pihak ketiga: script menggunakan Python Standard Library (`csv`, `random`, `sqlite3`).

## Validasi angka awal

| KPI | Dataset simulasi |
|---|---:|
| SKU | 48 |
| Warehouse | 3 |
| Supplier | 8 |
| Sales order | 4.925 |
| Sales order line | 8.534 |
| Inventory snapshots | 26.352 |
| Fill Rate (unit) | 74,15% |
| OTIF (order) | 42,90% |
| Revenue fulfilled | Rp3.324.652.500 |

Angka lain terdapat di `07_Reports/executive_summary.md`, dihitung ulang melalui `analyze_scm.py`.

## Perhatian mengenai akurasi dan privasi

- Dataset ini bukan benchmark perusahaan di industri FMCG dan tidak cocok menjadi sumber klaim penelitian empiris.
- Beberapa tingkat service sengaja rendah agar terdapat masalah nyata untuk diinvestigasi secara analitik.
- `Unserved Order Value` bukan confirmed lost sales.
- Forecast WAPE pada dataset buatan dapat tinggi karena banyak hari tanpa order per SKU-gudang; ini fenomena yang harus dianalisis, bukan disembunyikan.
- Skenario ROP memakai asumsi independensi demand dan lead time; biaya simpan mengasumsikan 20% per tahun dan tidak membuktikan penghematan aktual.
- Penghitungan stok bersifat simulasi dan tidak memakai metode costing perusahaan nyata.
- Setelah portofolio matang, buat screenshot Power BI dan unggah repository ke GitHub dengan disclaimer di atas.

## Target hasil akhir untuk rekruter

1. Link GitHub yang menampilkan alur SQL → analisis → dashboard.
2. `.pbix` yang dapat dibuka saat interview.
3. Business memo 1–2 halaman yang menghubungkan temuan KPI dan prioritas perbaikan.
4. Kemampuan menjelaskan minimal 12 query, empat dashboard, serta batasan data.

**Rujukan teknis resmi:**
- Power BI Desktop: https://learn.microsoft.com/en-us/power-bi/fundamentals/desktop-get-the-desktop
- Star-schema guidance: https://learn.microsoft.com/en-us/power-bi/guidance/star-schema
- SQLite: https://www.sqlite.org/lang_select.html

## Tambahan Modul 2 (Minggu 1–2)

- `03_SQL/MODUL_2_SQL_SCM_MINGGU_1_2.md`: tutorial 7 hari dengan perumusan masalah, cek hasil dan rubrik mandiri.
- `03_SQL/PRAKTIK_MINGGU_1_2_JAWABAN.sql`: 10 query siap jalankan, terdiri dari analisis OTIF, gudang, carrier, supplier, stok dan data quality.
- `03_SQL/test_module_2.py`: 10 tes otomatis; jalankan dengan `py 03_SQL\test_module_2.py`. Pengujian terbukti lulus pada dataset bawaan.
