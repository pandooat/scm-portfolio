# Roadmap 12 Minggu: Google Data Analytics Certificate → Junior SCM Data Analyst

**Asumsi:** pemula; belajar 10–12 jam/minggu di Windows; proyek sepenuhnya data sintetis. Jangan memaksa semua target selesai bila Anda belum mampu menjelaskan hasil mandiri.

| Minggu | Fokus | Durasi target | Tugas praktik | Bukti selesai |
|---:|---|---:|---|---|
| 1 | SCM Fundamentals + Excel | 10 jam | Pahami order → picking → pengiriman; buka CSV penjualan dan buat PivotTable | KPI unit dipesan vs dipenuhi |
| 2 | Excel Quality + Procurement | 10 jam | XLOOKUP, SUMIFS, Pivot, validasi duplikasi, analisis lead time | Ringkasan 3 gudang + keterlambatan PO |
| 3 | SQL Basic | 12 jam | DB Browser, SELECT, WHERE, GROUP BY, 1–6 latihan | 6 query disimpan dan dipahami |
| 4 | SQL Intermediate | 12 jam | JOIN, CASE, CTE, window functions, 7–16 latihan | 12+ query selesai tanpa mengandalkan copy-paste |
| 5 | Power BI Data Prep | 12 jam | Import 9 CSV, types, Power Query, cek grain | Data model bebas relasi ambigu |
| 6 | DAX Core + Executive | 12 jam | Measures, slicer, KPI cards, trend chart | Page 1 Executive selesai dan KPI cocok SQL |
| 7 | 3 Operational Pages | 12 jam | Inventory, Supplier, Logistics + cross-filter | 4 halaman dashboard selesai |
| 8 | Python for SCM | 10 jam | Dasar Python, csv, sqlite3, fungsi, skrip analisis | Bisa jalankan `analyze_scm.py` dan menjelaskan kode |
| 9 | Root Cause Analysis | 12 jam | ABC, SKU risks, supplier & warehouse comparison | 1 memo diagnosis memakai temuan data |
| 10 | Forecast & Optimization | 12 jam | Seasonal-naive/mean baseline, validation by time; reorder point scenario | Perbandingan forecast baseline dan skenario (asumsi jelas) |
| 11 | Portfolio Publication | 10 jam | README, screenshot `.pbix`, clean scripts, GitHub | Repository rapi dan file dapat direproduksi |
| 12 | Interview Simulation | 12 jam | SQL timed test, 5-min presentation, case questions, CV | Demo dan pertanyaan dasar selesai mandiri |

## Rutinitas mingguan yang realistis

- **2 sesi × 90 menit:** materi dan eksplorasi tool.
- **3 sesi × 2 jam:** praktik langsung pada proyek.
- **1 sesi × 1 jam:** menulis insight dan mereview error.
- **2 jam fleksibel:** menyelesaikan tugas tertinggal atau latihan interview.

Total kira-kira 12 jam seminggu. Kurangi ritme bila belum memahami istilah baru.

## Milestone dan gerbang kelulusan

- **Akhir minggu 2:** dapat menerangkan apa itu order, order line, SKU, PO, supplier, gudang, lead time, stockout.
- **Akhir minggu 4:** dapat membuat 12 query SQL tanpa meniru baris demi baris; tidak salah menghitung denominator OTIF.
- **Akhir minggu 7:** dapat membangun ulang satu halaman Power BI tanpa membuka video tutorial.
- **Akhir minggu 10:** dapat menjelaskan manfaat dan keterbatasan rekomendasi inventory, termasuk biaya stok tambahan.
- **Akhir minggu 12:** dapat menunjukkan project SQL + Power BI + Python, membuat analisis saat interviewer mengubah pertanyaan, dan mengakui asumsi data sintetis.

## Prioritas jika waktu terbatas

1. SQL (JOIN, agregasi, CTE, KPI query).
2. Power BI (data types, star schema, DAX, filter).
3. SC operation KPI (inventory, procurement, delivery, service).
4. Communication + business reasoning.
5. Python otomatisasi dan forecast sebagai nilai tambah setelah fondasi stabil.

**Larangan portofolio:** jangan mencantumkan 'berhasil menghemat RpX perusahaan' dari hasil simulasi; tulis 'mengestimasi skenario penghematan menggunakan data sintetis'.
