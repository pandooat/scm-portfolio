# Executive Summary: FMCG Supply Chain (DATA SIMULASI)

**Status sumber:** Seluruh data dan nama perusahaan dalam proyek ini **sintetis/fiktif**.
**Periode transaksi:** 1 April–30 September 2026. **Tanggal data simulasi diekstrak:** 15 Oktober 2026.
**Batas inferensi:** Angka hanya mendeskripsikan dataset buatan dan tidak membuktikan kinerja atau penghematan bisnis nyata.

## KPI dasar

| KPI | Hasil dataset simulasi | Definisi |
|---|---:|---|
| Jumlah sales order | 4,925 order | `COUNT(*)` faktur/order di fact_shipments |
| Jumlah baris order | 8,534 baris | `COUNT(*)` fact_sales_order_lines |
| Fulfillment rate (unit) | 74.15% | SUM(fulfilled_qty)/SUM(ordered_qty) |
| OTIF order | 42.90% | Order yang lengkap **dan** tiba <= tanggal janji dibagi seluruh order |
| Revenue terpenuhi | Rp3.324.652.500 | SUM(fulfilled_qty * unit_price) |
| COGS terpenuhi | Rp2.216.806.500 | SUM(fulfilled_qty * unit_cost) |
| Freight cost | Rp159.946.000 | Total freight biaya order yang dikirim |
| Order value yang belum terpenuhi (indikatif) | Rp1.013.750.500 | SUM((ordered_qty - fulfilled_qty)*unit_price). **Bukan** realized lost revenue |
| Share SKU-gudang-hari dengan stok akhir 0 | 14.31% | SUM(stockout_flag)/COUNT(*) snapshot |
| Supplier PO OTD | 35.95% | PO diterima <= expected_date, hanya PO sudah diterima |
| Risiko stok tinggi, snapshot September | 70 kombinasi SKU-gudang | Berdasarkan ambang latihan >=5 hari stockout atau days cover <7 |

## Pertanyaan analitis untuk interview

1. Mengapa fill rate dan OTIF lebih rendah dibandingkan tingkat layanan yang diinginkan?
2. Warehouse dan SKU mana yang berkontribusi paling besar terhadap unfulfilled units?
3. Apakah pemasok dengan OTD rendah terkonsentrasi di produk fast-moving?
4. Bagaimana trade-off menaikkan safety stock versus biaya modal persediaan?
5. KPI mana yang perlu dinormalisasi per order, per unit, atau per hari agar tidak salah kesimpulan?

## Rekomendasi berbasis hipotesis, bukan klaim penghematan

- Telusuri SKU-gudang berisiko tinggi dalam `sku_inventory_risk_last_30d.csv`, lalu periksa kecepatan permintaan dan PO terbuka.
- Prioritaskan evaluasi SLA supplier berdasarkan metrik OTD yang sudah dihitung pada `supplier_performance.csv`.
- Uji skenario reorder point pada kombinasi fast-moving + lead time tidak stabil; hitung dampak stok dan service level **secara simulatif** sebelum merekomendasikan implementasi.
- Audit nilai `unserved order value`: potensi opportunity yang belum terpenuhi, bukan pendapatan yang pasti hilang.

## Artefak pendukung

- `warehouse_monthly.csv`: hasil agregasi bulanan 3 warehouse.
- `supplier_performance.csv`: performa delapan supplier fiktif.
- `sku_inventory_risk_last_30d.csv`: indikator risiko berbasis snapshot September.
- Semua laporan dihasilkan kembali menggunakan `python 04_Python/analyze_scm.py`.
