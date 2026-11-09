# Mock Interview: Junior SCM Data Analyst

Latihan ini dirancang untuk kandidat dengan sertifikasi Google Data Analytics dan pengalaman praktik awal. Jawablah dengan rumus, contoh query, satuan, risiko data, dan keputusan bisnis. Semua angka dataset bersumber dari SIMULASI.

## 1. Perkenalkan diri dalam 60 detik

**Kerangka jawaban (sesuaikan kebenaran diri):**

> Saya memiliki sertifikasi Google Data Analytics dan sedang membangun kompetensi analisis operasional melalui proyek supply chain end-to-end. Dalam proyek simulasi FMCG, saya memproses data order, stok, pembelian, dan pengiriman menggunakan SQL dan Python, kemudian membuat KPI Power BI. Saya berlatih mengevaluasi fill rate, OTIF, stockout, dan supplier lead time serta menerjemahkan temuan menjadi rekomendasi operasional. Saya tertarik dengan posisi ini karena dapat menggabungkan ketelitian analisis data dengan peningkatan kinerja distribusi.

**Peringatan:** katakan 'membangun' jika proyek masih dalam proses; 'telah membangun' hanya setelah selesai. Jangan mengaku pernah bekerja di perusahaan fiktif ini.

## 2. Jelaskan perbedaan Fill Rate dan OTIF

- Fill Rate = unit yang terpenuhi / unit diminta. Bisa tinggi walau pengiriman terlambat.
- OTIF = proporsi order yang sekaligus lengkap dan delivered <= promised date. Menggunakan grain order, bukan item.
- Jelaskan juga apakah periode berdasarkan order date atau delivery date dan konsekuensinya.

## 3. Apa yang Anda lakukan ketika Fill Rate menurun?

Langkah: (1) validasi definisi KPI, (2) cek unit/dimensi waktu, (3) segmen produk-gudang-supplier, (4) identifikasi kontributor unfulfilled units, (5) periksa replenishment, (6) susun hipotesis dan eksperimen perbaikan, (7) pantau service level dan biaya stok.

## 4. Bagaimana menghitung On-Time Delivery supplier?

- Pilih PO yang **sudah diterima** dalam populasi untuk metric berdasarkan tanggal PO.
- Tandai PO on time jika actual_receipt_date <= expected_date.
- Denominator = jumlah PO yang sudah diterima; PO masih open dipantau lewat **open/overdue PO** terpisah.
- Bandingkan supplier hanya jika cakupan jenis produk/lead time cukup sebanding.

## 5. Mengapa SQL JOIN sering mengacaukan KPI?

`fact_sales_order_lines` bisa memiliki beberapa baris untuk satu order, tetapi `fact_shipments` satu baris per order. JOIN langsung menyebabkan data order-level seperti `freight_cost` diduplikasi untuk setiap SKU. Solusi: agregasi lebih dahulu atau pisahkan fact tables di semantic model.

## 6. Bagaimana memilih safety stock?

Mulai dengan variabilitas permintaan dan lead time, service-level target, dan biaya simpan. Jangan memakai safety stock tunggal untuk semua SKU. Jika asumsi lead time konstan dan permintaan harian independen, salah satu pendekatan dasar adalah `Z × sigma_demand × sqrt(lead_time)`. Jika lead time juga bervariasi, gunakan model yang mengakomodasi kedua sumber ketidakpastian. Uji skenario serta batasannya, jangan klaim causal effect dari simulasi.

## 7. Apa kelemahan rata-rata demand per hari?

Rata-rata dapat menutupi musim, tren, promo, stockout-censored demand, maupun intermittent demand. Bandingkan baseline sederhana memakai evaluasi walk-forward atau holdout berdasarkan waktu. Hindari random split untuk data deret waktu.

## 8. Apakah mengoptimalkan biaya logistik selalu meningkatkan service level?

Tidak. Pengiriman lebih murah dapat memperpanjang transit, yang berdampak pada OTIF. Bandingkan trade-off biaya per order versus ketepatan waktu dan margin produk. Bila perlu, segmen layanan per jenis customer.

## 9. Dalam Power BI, mengapa inventory value tidak boleh dijumlahkan sepanjang hari?

Saldo persediaan adalah *semi-additive measure*: dapat dijumlah lintas SKU/gudang pada satu tanggal, tetapi tidak lintas waktu sebagai saldo saat ini. Gunakan nilai tanggal akhir untuk ending inventory, atau rata-rata nilai inventory per hari untuk denominator turnover.

## 10. Tugas SQL live: tampilkan 5 SKU dengan unfulfilled units tertinggi

```sql
SELECT p.sku,p.product_name,
       SUM(s.ordered_qty-s.fulfilled_qty) AS unfulfilled_units
FROM fact_sales_order_lines s
JOIN dim_products p ON p.product_id=s.product_id
GROUP BY p.product_id
ORDER BY unfulfilled_units DESC LIMIT 5;
```

## 11. Apa yang harus dilakukan jika SQL dan Power BI menghasilkan KPI berbeda?

Periksa date filter, inactive relationship, grain, tipe data, blanks, duplicate keys, perbedaan denominator, serta transaksi yang belum diterima/terkirim. Buat query rekonsiliasi dan cek sampel order sampai tingkat baris.

## 12. Apakah hasil proyek ini dapat diterapkan langsung pada perusahaan sungguhan?

Belum tentu. Dataset bersifat sintetis dan kebijakannya disederhanakan. Dalam operasi nyata, validasi definisi bisnis, integrasi ERP/WMS/TMS, granularitas waktu, SLA, retur, backorder, dan costing perlu dilakukan sebelum menjalankan rekomendasi.

## Skrip presentasi 5 menit

- **Menit 0–1:** konteks bisnis, dataset simulasi, dan definisi masalah.
- **Menit 1–2:** arsitektur data dan validasi.
- **Menit 2–3:** empat KPI utama, segmentasi gudang/SKU.
- **Menit 3–4:** dugaan akar masalah dan bukti yang tersedia, sebutkan hal yang belum terbukti.
- **Menit 4–5:** rekomendasi prioritas, trade-off biaya dan risiko, langkah monitoring.

## Pertanyaan balik untuk interviewer

1. Tools dan sistem sumber data yang digunakan perusahaan saat ini, mis. ERP/WMS/TMS?
2. Tiga KPI supply chain yang paling mendesak untuk ditingkatkan dalam enam bulan ke depan?
3. Tantangan data quality atau reporting yang paling sering dialami tim operasional?
