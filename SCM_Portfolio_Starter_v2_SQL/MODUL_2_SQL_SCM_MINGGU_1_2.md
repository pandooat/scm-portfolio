# Modul 2 | Investigasi Masalah SCM dengan SQL (Minggu 1–2)

**Level:** Pemula, dengan Google Data Analytics Certificate  
**Lingkungan:** DB Browser for SQLite  
**Database:** `../02_Database/scm_portfolio.sqlite`  
**Data:** seluruhnya **SIMULASI / SINTETIS**, bukan data operasional nyata.

## Sasaran belajar

Pada akhir modul Anda mampu (1) membedakan **order** dari **order line**, (2) membuat SQL `SELECT`, `COUNT`, `SUM`, `GROUP BY`, `JOIN` dan `CASE WHEN`, (3) memahami empat hasil OTIF, (4) memilih masalah prioritas berdasarkan data, dan (5) menyajikan rekomendasi yang tidak berlebihan.

## Cara memakai modul

1. Buka database SQLite di `02_Database/scm_portfolio.sqlite` dengan DB Browser for SQLite.
2. Pilih tab **Execute SQL**.
3. Jalankan satu query. Periksa hasilnya sebelum melihat jawaban di `PRAKTIK_MINGGU_1_2_JAWABAN.sql`.
4. Simpan query yang Anda tulis sendiri sebagai file `latihan_saya.sql`.
5. Tulis 2–3 kalimat interpretasi data untuk setiap latihan. Jangan menyalin kesimpulan tanpa memahami perhitungannya.

## Peta tabel

- `dim_products`: daftar 48 SKU, kategori, supplier, harga dan biaya standar.
- `dim_warehouses`: tiga gudang (Jakarta, Bandung, Surabaya).
- `dim_suppliers`: delapan supplier.
- `fact_sales_order_lines`: satu baris untuk satu jenis produk dalam pesanan. Terdapat 8.534 baris untuk 4.925 order.
- `fact_shipments`: satu baris untuk satu **order**. Terdapat 4.925 order.
- `fact_purchase_order_lines`: catatan PO kepada supplier.
- `fact_inventory_daily`: stok akhir per **tanggal × gudang × SKU**.

> **Grain** berarti satu baris mewakili entitas apa. Ini harus ditentukan sebelum melakukan `COUNT` ataupun `JOIN`. Jika langsung menggabungkan dua tabel fakta di tingkat detail tanpa memahami grain, angka dapat berlipat dan keliru.

## Jadwal latihan 7 hari (60–90 menit/hari)

### Hari 1: Baca tabel dan pahami grain (Q1, Q2)

**Pertanyaan bisnis:** Berapa total order dan bagaimana persentase order yang memenuhi janji lengkap dan tepat waktu?

```sql
SELECT COUNT(*) AS total_orders,
       SUM(otif_flag) AS otif_orders,
       ROUND(100.0 * SUM(otif_flag) / COUNT(*),2) AS otif_pct
FROM fact_shipments;
```

**Ekspektasi:** 4.925 order, 2.113 OTIF, 42,90%.

Bandingkan dengan:

```sql
SELECT COUNT(*) AS order_lines,
       COUNT(DISTINCT order_id) AS unique_orders
FROM fact_sales_order_lines;
```

**Ekspektasi:** 8.534 order line tetapi hanya 4.925 order unik. Mengapa? Satu order dapat mengandung lebih dari satu SKU. **Jangan menghitung OTIF order dari `COUNT(*)` pada order line.**

**Tugas refleksi:** tulis perbedaan order-level dan line-level, termasuk contoh risiko double counting.

### Hari 2: Fill rate per gudang (Q3)

**Pertanyaan:** gudang mana yang paling rendah persentase unit pemenuhannya?

Gunakan `SUM(fulfilled_qty) / SUM(ordered_qty)` pada `fact_sales_order_lines`, gabungkan dengan `dim_warehouses` menggunakan `warehouse_id`, lalu `GROUP BY` gudang.

**Ekspektasi:** Surabaya 72,80%; Jakarta 73,94%; Bandung 75,76%.

**Interpretasi tepat:** Surabaya menjadi prioritas pemeriksaan unit pemenuhan. **Belum dapat disimpulkan** bahwa karyawan/gudangnya berkinerja buruk sebelum memeriksa komposisi SKU, pola demand, dan pasokan.

### Hari 3: Bongkar OTIF menjadi empat kategori (Q4)

Gunakan `CASE WHEN` pada `on_time_flag` dan `in_full_flag` di tabel `fact_shipments`.

| Kategori (hanya satu per order) | Order |
|---|---:|
| Lengkap & tepat waktu | 2.113 |
| Tidak lengkap, tepat waktu | 1.022 |
| Lengkap, terlambat | 848 |
| Tidak lengkap & terlambat | 942 |
| **Total** | **4.925** |

**Latihan berpikir:** apa kesalahan menghitung 1.964 order tidak lengkap + 1.790 order terlambat = 3.754 sebagai jumlah order gagal OTIF? Jawaban: terdapat 942 order yang masuk ke kedua kelompok, sehingga harus dikurangi untuk menghindari double counting. Total gagal OTIF = 2.812.

### Hari 4: OTIF per gudang dan carrier (Q5, Q6)

Gunakan `fact_shipments` untuk menghitung OTIF per gudang, lalu per `carrier_name`.

**Ekspektasi OTIF gudang:** Surabaya 42,32%; Jakarta 42,57%; Bandung 43,82%.

**Ekspektasi OTIF carrier terendah:** Mitra Trucking (Simulasi) = 34,67%. Periksa `on_time_pct` dan `in_full_pct` sebelum menyusun hipotesis.

**Tugas refleksi:** karena OTIF mencakup ketepatan dan kelengkapan, apakah OTIF yang rendah pada satu carrier otomatis membuktikan bahwa carrier tersebut penyebab utamanya? **Tidak.** Ketersediaan barang, rute, dan karakteristik order perlu dikontrol.

### Hari 5: Supplier OTD dan keterlambatan procurement (Q7)

Hitung PO tepat waktu yang sudah diterima: `actual_receipt_date <= expected_date`.

**Ekspektasi supplier terendah:** PT Niaga Mitra (Simulasi), OTD 2,83% pada 106 PO diterima. Berikutnya PT Karya Maju Industri 3,88%; PT Surya Ritelindo 5,45%.

**Perhatian metodologis:** filter `actual_receipt_date IS NOT NULL` diperlukan untuk metrik OTD **PO diterima**. PO terbuka tidak boleh hilang dari pemantauan; buat metrik *open/overdue PO* terpisah agar tidak tercipta survivorship bias.

### Hari 6: Temukan SKU berisiko dan nilai opportunity (Q8, Q9)

1. Kelompokkan September 2026 berdasarkan gudang dan SKU, lalu jumlahkan `stockout_flag` untuk hari ketika stok akhir = 0.
2. Hitung nilai order belum terpenuhi `SUM((ordered_qty - fulfilled_qty) * unit_price)` berdasarkan SKU.
3. Cocokkan temuan kedua analisis: apakah SKU dengan banyak hari stok kosong juga memiliki nilai order tidak terpenuhi besar?

**Penting:** `unserved_order_value_rp` bersifat indikatif, **bukan bukti lost sales**. Data sintetis tidak memuat apakah pelanggan akhirnya membatalkan order, menunggu backorder, atau membeli produk pengganti.

### Hari 7: Data quality, memo dan latihan interview (Q10)

Cek bahwa `opening_qty + received_qty - shipped_qty = closing_qty` pada setiap snapshot stok.

**Ekspektasi:** 0 snapshot yang tidak seimbang.

Kemudian tulis memo maksimal 250 kata, dengan struktur:

1. **Masalah:** KPI apa, periode apa, denominasi apa, besarnya berapa.
2. **Temuan:** pecahan OTIF, area yang paling berisiko.
3. **Hipotesis:** kemungkinan penyebab, dengan bahasa belum terverifikasi.
4. **Tindakan:** data tambahan untuk memvalidasi penyebab dan pilot perbaikan yang bisa dicoba.
5. **Keterbatasan:** ini data buatan; temuan bukan dampak operasional nyata.

## 5 pertanyaan mini interview

1. Mengapa `COUNT(*)` pada `fact_sales_order_lines` bukan jumlah order?
2. Apa bedanya unit fill rate dan OTIF? Apakah denominatornya sama?
3. Apa peran `JOIN dim_warehouses` pada query fill rate?
4. Mengapa OTD supplier yang rendah belum otomatis membuktikan stockout?
5. Sebelum merekomendasikan safety stock, data tambahan apa yang diperlukan?

## Rubrik kemajuan mandiri

| Aspek | Poin maksimal |
|---|---:|
| Menulis SQL tanpa menyalin | 30 |
| Menafsirkan numerator, denominator, grain, periode | 25 |
| Melakukan validasi dan menghindari double counting | 20 |
| Menyusun rekomendasi dan batasan yang logis | 15 |
| Menjelaskan hasil dengan ringkas | 10 |
| **Total** | **100** |

**Target sebelum melanjutkan ke DAX:** minimal 80/100 pada rubrik pribadi, serta dapat menulis Q1–Q5 tanpa melihat jawabannya. Target tersebut merupakan standar latihan, bukan kriteria resmi recruiter.

## Next step

Setelah Q1–Q10, lanjutkan `LATIHAN_SQL_PEMULA.md` dan `solutions_16_queries.sql` untuk CTE, inventory turnover, supplier variance, dan ABC revenue classification. Lalu mulai langkah pemodelan di `05_PowerBI/BANGUN_DASHBOARD_STEP_BY_STEP.md`.
