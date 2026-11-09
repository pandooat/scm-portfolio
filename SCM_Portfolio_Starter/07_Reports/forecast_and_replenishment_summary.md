# Demand Forecast Backtest & Replenishment Scenario (SINTETIS)

**Bukan hasil penerapan lapangan, bukan data industri nyata.** Seluruh metrik dihitung dari dataset buatan FMCG.

## Forecasting baseline: validasi satu langkah ke depan

- Validasi: **1–30 September 2026**, untuk 144 kombinasi SKU–gudang per hari.
- `MA14`: ramalan permintaan unit besok menggunakan rata-rata unit yang dipesan dalam 14 hari sebelumnya.
- `Seasonal naive (7-day)`: ramalan besok sama dengan permintaan pada hari yang sama minggu lalu.
- Evaluasi *rolling one-step ahead*: menggunakan permintaan yang tersedia **sebelum** tanggal ramalan, tanpa mengintip tanggal berikutnya.
- Metrik: WAPE = total absolute error / total actual ordered units, tidak memakai rata-rata error persen per SKU yang mempunyai nilai actual 0.

| Baseline | WAPE dataset sintetis |
|---|---:|
| Moving average 14-day | 136.80% |
| Seasonal naive (lag 7 hari) | 158.94% |

Interpretasi: model dengan WAPE lebih kecil lebih baik untuk baseline yang diuji. WAPE tinggi tidak boleh disembunyikan, terutama karena demand SKU-gudang bersifat intermittent. Gunakan error per kategori/SKU untuk memeriksa apakah pendekatan lebih cocok bagi Fast atau Slow moving.

## Reorder Point (ROP) scenario per SKU-gudang

Menggunakan unit permintaan yang dicatat (`ordered_qty`) dalam 90 hari terakhir hingga **30 September 2026**, serta rata-rata dan simpangan baku lead time aktual supplier yang sudah diterima pada/belum tanggal tersebut.

Formula pembelajaran (asumsi permintaan harian dan lead time saling independen):

- `Expected lead-time demand = demand_mean × lead_mean`
- `Safety stock = Z × sqrt(lead_mean × demand_sd² + demand_mean² × lead_sd²)`
- `Reorder point = ceil(expected lead-time demand + safety stock)`
- `Inventory position = closing stock + open PO qty` (model ini tidak memakai backorder).

Tiga tingkat layanan sasaran ilustratif: 90% (Z=1,282), 95% (Z=1,645), 98% (Z=2,054). **Angka tingkat layanan bukan hasil service level yang telah dicapai.**

- Jumlah kombinasi SKU-gudang: 144.
- Posisi inventory di bawah ROP skenario 95%: 68 kombinasi.
- Perkiraan biaya carrying safety stock/tahun memakai **asumsi 20% per tahun × unit cost standar**. Bukan tarif/biaya perusahaan nyata.

Perbandingan biaya 95% vs 90% merupakan ilustrasi tambahan biaya simpan safety stock; **bukan estimasi dampak bersih terhadap lost sales atau penghematan aktual**.

## Keterbatasan

- Simulasi tidak memodelkan retur, MOQ supplier, biaya stockout aktual, variasi harga, backorder, kapasitas gudang, dan distribusi non-normal.
- Parameter Z adalah pendekatan normal dan tidak menjamin fill rate atau cycle service level pada SKU yang intermittent.
- Hindari menerapkan semua ROP langsung; prioritaskan SKU Fast/high risk lalu uji permintaan dan lead time nyata.

## File untuk Power BI

- `forecast_predictions_sep2026.csv`: actual vs dua baseline forecast per SKU-gudang-tanggal.
- `forecast_backtest_by_warehouse.csv`: ringkasan WAPE tiap warehouse dan metode.
- `reorder_point_service_level_scenarios.csv`: skenario ROP 90/95/98% dan ilustrasi annual carrying cost.
