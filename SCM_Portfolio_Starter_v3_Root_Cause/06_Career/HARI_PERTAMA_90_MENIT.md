# Hari Pertama: Tugas Praktik 90 Menit

**Tujuan:** membuktikan Anda bisa menjalankan SQL pertama dengan database yang sudah tersedia, lalu memahami hasilnya. Tidak perlu menginstal Python untuk tahap ini.

## Menit 0–15: kenali data

Buka `01_Data/dim_products.csv` dan `fact_sales_order_lines.csv` menggunakan Microsoft Excel. Temukan `product_id`, `order_id`, `ordered_qty`, dan `fulfilled_qty`.

**Pertanyaan:** mengapa satu `order_id` bisa muncul lebih dari satu baris? Jawaban: satu order dapat berisi beberapa produk.

## Menit 15–30: buka database

1. Instal aplikasi **DB Browser for SQLite** dari https://sqlitebrowser.org/
2. Klik `Open Database` lalu pilih file `02_Database/scm_portfolio.sqlite`.
3. Pilih tab `Browse Data`, lalu cek daftar tabel dan jumlah barisnya.

## Menit 30–50: query pertama

Buka tab `Execute SQL`, tempel:

```sql
SELECT
    SUM(ordered_qty) AS units_requested,
    SUM(fulfilled_qty) AS units_fulfilled
FROM fact_sales_order_lines;
```

Klik `Run` (tombol ▶). Catat kedua nilai.

## Menit 50–65: hitung Fill Rate

```sql
SELECT
    ROUND(100.0 * SUM(fulfilled_qty) / SUM(ordered_qty), 2) AS fill_rate_pct
FROM fact_sales_order_lines;
```

**Checkpoint:** Anda seharusnya melihat `74.15`. Ini berarti 74,15% unit order dalam dataset simulasi terpenuhi.

## Menit 65–80: bandingkan dengan OTIF

```sql
SELECT
    ROUND(100.0 * SUM(otif_flag) / COUNT(*), 2) AS otif_pct
FROM fact_shipments;
```

**Checkpoint:** hasilnya `42.9`. Mengapa OTIF lebih kecil? Karena order harus **lengkap dan tepat waktu** sekaligus.

## Menit 80–90: tulis dua kalimat insight

Tulis analisis singkat dari hasil Anda sendiri, contoh:

> Dataset simulasi mencatat fill rate 74,15% dan OTIF 42,90%. Selisih ini menunjukkan masalah pelayanan tidak dapat dinilai hanya dari jumlah unit yang dipenuhi, karena ketepatan tanggal pengiriman juga menjadi bagian definisi OTIF.

**Jangan langsung menyimpulkan** bahwa penyebab utama adalah supplier sebelum melihat data procurement dan logistics. 

## Selesai jika

Anda dapat menjalankan tiga query tanpa error dan menerangkan beda denominator dua KPI tersebut. Jika terjadi error, simpan screenshot tab `Execute SQL`, teks query, dan pesan error untuk dianalisis.
