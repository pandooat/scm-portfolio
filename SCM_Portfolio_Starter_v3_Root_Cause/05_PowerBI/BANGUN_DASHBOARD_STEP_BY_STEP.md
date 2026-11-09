# Tutorial Power BI Desktop untuk Pemula (SCM Portfolio)

**Tujuan:** buat `.pbix` Anda sendiri dari 9 CSV sintetis. File `.pbix` **tidak** disertakan; bagian ini menuntun Anda membuatnya secara mandiri untuk ditampilkan saat interview.

## Persiapan

1. Unduh Power BI Desktop dari Microsoft Store atau https://learn.microsoft.com/en-us/power-bi/fundamentals/desktop-get-the-desktop
2. Ekstrak seluruh folder proyek dan jangan pindahkan CSV satu-satu.
3. Buka Power BI Desktop, pilih **Blank report**.
4. Pilih **Home → Get data → Text/CSV** → file `01_Data/dim_products.csv` → pilih **Transform Data** (bukan Load) agar dapat memeriksa tipe data.
5. Di Power Query pilih **New Source → Text/CSV**, tambahkan SEMUA 9 CSV dalam folder `01_Data/`.
6. Pada setiap query, centang **Use First Row as Headers** bila judul belum terbaca; ubah tipe kolom sesuai `MODEL_DATA.md`.
7. Untuk tanggal dari CSV, pastikan Date bukan Text. Untuk kolom kosong pada `actual_receipt_date`, nilai kosong harus `null`, bukan string teks.
8. Klik **Close & Apply**.

## Relasi

9. Buka **Model View** (ikon skema di sidebar kiri).
10. Buat **14 hubungan dimensi→fakta** sesuai diagram di `MODEL_DATA.md`: 3 produk, 4 gudang, 1 supplier, 2 pelanggan, dan 4 tanggal.
11. Semua arah filter **Single**, cardinality **One to many (1:*)**. Periksa tidak ada relationship fakta langsung ke fakta.
12. Buka **Table View**, cek 48 SKU, 3 warehouse, 4.925 shipments/order dan 26.352 snapshot inventory.

## Measures DAX

13. Klik **Modeling → New Measure**; masukkan rumus pertama dari `DAX_Measures.txt`, misalnya:

```dax
Total Orders = COUNTROWS(fact_shipments)
```

14. Lakukan satu demi satu untuk `Units Requested`, `Units Fulfilled`, `Fill Rate %`, `OTIF %`, `Revenue IDR`, `COGS IDR`, `Supplier OTD %`, `Stockout Snapshot %` dan seterusnya.
15. **Measure tools → Format → Percentage** untuk KPI persen. Jumlah rupiah gunakan format number dengan separator ribuan/currency.
16. Buat Card untuk memverifikasi:

- Total Orders: **4.925**
- Fill Rate %: **74,15%**
- OTIF %: **42,90%**
- Revenue IDR: **Rp3.324.652.500**

Jika berbeda, periksa format pengenalan kolom, relationship atau apakah ada slicer aktif.

## Desain dashboard: 4 halaman

### Page 1: Executive Overview

- Card: Revenue, Fill Rate %, OTIF %, Supplier OTD %, Freight Cost
- Clustered bar: Revenue per warehouse (axis `dim_warehouses[warehouse_name]`)
- Line chart: `Revenue IDR` by `dim_calendar[year_month]`
- Table: warehouse, fill rate, OTIF, freight cost
- Slicer: calendar month dan warehouse
- Insight box: kesimpulan dan rekomendasi dalam bahasa bisnis

### Page 2: Inventory & Stockout

- Card: Stockout Snapshot %, End Period Inventory Value
- Clustered bar: stockout SKU-warehouse-days by warehouse
- Matrix: produk/category, stockout count, end period inventory value
- Top-10 SKU stockout untuk bulan September; bandingkan dengan `07_Reports/sku_inventory_risk_last_30d.csv`
- Hindari menampilkan SUM seluruh saldo stok harian sebagai nilai stok terkini.

### Page 3: Procurement & Supplier

- Card: Supplier OTD %, Avg Supplier Lead Days
- Bar: Supplier OTD % by supplier
- Table: supplier, POs received, POs on time, average lead
- Investigasi supplier dengan delay tertinggi, laporkan jumlah PO pembandingnya.

### Page 4: Logistics & Customer Service

- Card: OTIF %, On-Time %, In-Full %, Avg Freight per Shipped Order
- Bar: OTIF % by carrier
- Bar: OTIF % by warehouse
- Chart: freight cost by `dim_calendar[year_month]`
- Insight: bedakan keterlambatan pengiriman dan tidak terpenuhi stok.

## Quality Assurance sebelum dipublikasikan

- [ ] Semua filter bekerja konsisten tanpa hubungan ambigu.
- [ ] Revenue tidak berubah hanya karena menambahkan tabel dimensi supplier pada halaman unrelated.
- [ ] OTIF selalu berdasarkan jumlah order, bukan jumlah item.
- [ ] Persentase ditampilkan sebagai 74,15%, bukan 0,7415% atau 7.415%.
- [ ] Saldo akhir inventory memakai tanggal terakhir periode terpilih.
- [ ] Setiap chart memiliki judul dan unit (Rp, unit, hari, %).
- [ ] Beri label 'Synthetic Data | Portfolio Case Study' di semua halaman.
- [ ] Simpan `.pbix` sebagai `SCM_FMCG_Analytics_Portfolio.pbix` pada komputer Anda.
- [ ] Ambil screenshot empat dashboard untuk GitHub; **jangan** mengklaim hasil buatan ini sebagai proyek profesional di perusahaan.

## Jika bingung

Mulai dari **satu** halaman `Executive Overview` saja. Tampilkan empat angka utama dan satu grafik revenue per warehouse. Baru lanjutkan ke halaman lain. 

Sumber resmi:
- https://learn.microsoft.com/en-us/power-bi/fundamentals/desktop-get-the-desktop
- https://learn.microsoft.com/en-us/power-bi/guidance/star-schema
