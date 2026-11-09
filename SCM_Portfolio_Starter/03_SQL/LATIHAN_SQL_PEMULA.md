# Praktik SQL SCM dari Nol

**Sumber:** `02_Database/scm_portfolio.sqlite`, seluruh data sintetis. Gunakan **DB Browser for SQLite** → **Open Database** → **Execute SQL**. Salin satu query dari `solutions_16_queries.sql` dan tekan tombol **Execute** untuk melihat hasil.

## Rute progresif (16 latihan)

| No. | Level | Kompetensi | Tantangan |
|---:|---|---|---|
| 1 | Dasar | GROUP BY | Hitung jumlah SKU per kategori. |
| 2 | Dasar | WHERE, ORDER BY | Filter produk Food dengan harga >= Rp30.000. |
| 3 | Dasar | SUM | Hitung unit dipesan, dipenuhi, tidak dipenuhi. |
| 4 | Dasar | GROUP BY | Hitung banyaknya order line fulfilled, partial, unfulfilled. |
| 5 | Dasar | JOIN, NULLIF | Hitung fill rate per warehouse. |
| 6 | Dasar | JOIN, LIMIT | Temukan 10 SKU dengan revenue terbesar. |
| 7 | Menengah | GROUP BY tanggal | Buat revenue, COGS, gross margin per bulan. |
| 8 | Menengah | KPI grain | Hitung OTIF pada tingkat order, bukan baris order. |
| 9 | Menengah | CASE WHEN | Bandingkan ketepatan, kelengkapan dan ongkir per carrier. |
| 10 | Menengah | JOIN, julianday | Supplier OTD dan lead time, hanya PO yang sudah diterima. |
| 11 | Menengah | Aggregation | Identifikasi kombinasi SKU-gudang paling sering stok akhir nol. |
| 12 | Menengah | Opportunity metric | Hitung nilai order yang belum terpenuhi, tanpa mengklaim lost sales. |
| 13 | Lanjutan | CTE, window functions | Buat klasifikasi ABC dari kontribusi revenue. |
| 14 | Menengah | Variance | Hitung variance harga PO terhadap benchmark biaya produk. |
| 15 | Lanjutan | CTE, metric definition | Hitung monthly inventory turnover dengan average inventory yang benar. |
| 16 | Menengah | Data validation | Temukan ketidakseimbangan inventori (harus 0). |

## Cara belajar efektif

1. Jalankan query dalam file solusi, lalu **tutup solusi**.
2. Tulis ulang dengan struktur Anda sendiri; simpan menjadi file `.sql` baru.
3. Jelaskan kepada orang lain arti **numerator, denominator, grain, dan periode** setiap KPI.
4. Untuk query JOIN, jelaskan kemungkinan risiko **double counting** ketika tabel fakta digabung tanpa agregasi lebih dulu.
5. Bandingkan hasil Anda dengan `07_Reports/executive_summary.md`.

## Mini tes interview

- Jelaskan mengapa `COUNT(*)` pada `fact_sales_order_lines` tidak boleh dijadikan denominator untuk OTIF order-level.
- Mengapa menghitung `AVG(inventory_value)` seluruh baris snapshot belum tentu menjadi average inventory value harian total perusahaan?
- Apa perbedaan PO yang belum diterima dan PO yang diterima terlambat dalam perhitungan Supplier OTD?

**Kriteria lulus pribadi:** sanggup menulis ulang minimal 12 dari 16 query tanpa melihat jawaban, memverifikasi metrik, dan menjelaskan keterbatasannya.
