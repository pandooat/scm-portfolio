# Modul 3 — SQL Quick Reference & Kuis Mandiri

**Data:** sintetis. Lakukan latihan tanpa melihat jawaban terlebih dahulu.

## Ringkasan SQL praktis

| Ekspresi | Untuk apa? | Perhatian |
|---|---|---|
| `SELECT` | Pilih kolom | Gunakan nama alias yang bermakna |
| `FROM` | Tetapkan tabel sumber | Pahami grain sumber |
| `WHERE` | Filter baris | Diterapkan sebelum agregasi |
| `JOIN ... ON` | Gabungkan tabel | JOIN antarfact dapat menggandakan KPI |
| `SUM`, `COUNT` | Agregasi | Pastikan unit dan denominator sesuai |
| `GROUP BY` | Agregasi per kategori | Tambahkan kunci dimensi yang konsisten |
| `CASE WHEN` | Klasifikasi bersyarat | Kategori harus jelas dan eksklusif |
| `WITH x AS (...)` | CTE untuk query bertahap | Berguna untuk agregasi sebelum JOIN |
| `NULLIF(x,0)` | Hindari pembagian nol | Persentase dapat menjadi `NULL` jika penyebut nol |
| `substr(date,1,7)` | Bulan dalam format `YYYY-MM` | Hanya cocok untuk string tanggal ISO |

## Kuis (jawab tanpa membuka `MODUL_3_ROOT_CAUSE_QUERIES.sql`)

1. Apa perbedaan 4.925 order dan 8.534 order line?
2. Sebutkan rumus unit fill rate dan denominasi yang dipakai.
3. Mengapa nilai fill rate tidak tepat dihitung dengan rata-rata persentase seluruh order line tanpa bobot?
4. Pada bulan apa terjadi fill rate paling rendah?
5. Pada Agustus, gudang mana mencatat fill rate terendah?
6. Apa kombinasi gudang-SKU dengan nilai order tidak terpenuhi terbesar?
7. Apakah `nilai unit order tidak terpenuhi × harga jual` bisa langsung disebut *lost revenue*? Jelaskan.
8. Bagaimana menghindari duplikasi ongkir ketika menggabungkan shipment dan sales order line?
9. Apakah 10% OTD pada supplier SKU0039–Surabaya otomatis membuktikan keterlambatan supplier menyebabkan semua kegagalan layanan?
10. Jika stok akhir 0, apakah stok pasti kosong sepanjang hari? Jelaskan.

## Panduan mengecek pemahaman

Setelah menjawab, bandingkan dengan `MODUL_3_ROOT_CAUSE_ANALYSIS.md`, cek query, lalu tulis jawaban 2–4 kalimat per nomor. Jika ada jawaban yang belum bisa dijelaskan, ulangi sesi yang berkaitan.

## Contoh format presentasi tiga menit

- **0:00–0:30**: nyatakan masalah dan definisi KPI (OTIF vs fill rate).
- **0:30–1:15**: tampilkan pola tren bulanan dan konsentrasi gudang-SKU.
- **1:15–2:00**: tampilkan rangkaian stok dan penerimaan PO sebagai bukti hipotesis.
- **2:00–2:40**: sampaikan rekomendasi, KPI pilot, biaya/risiko implementasi.
- **2:40–3:00**: jelaskan keterbatasan data sintetis dan validasi berikutnya.
