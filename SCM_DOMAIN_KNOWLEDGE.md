# SCM FMCG Domain Knowledge
*Referensi tunggal untuk memahami Supply Chain Management di industri FMCG — konsep, metrik, formula, arsitektur data, dan logika bisnis yang digunakan dalam proyek ini.*

> **Status Data:** Seluruh angka dalam dokumen ini merujuk dataset sintetis proyek portofolio (Apr–Sep 2026, seed `2026`). Bukan data perusahaan nyata atau benchmark industri.

---

## Daftar Isi

1. [Apa Itu FMCG & Tantangan Supply Chain-nya](#1-apa-itu-fmcg--tantangan-supply-chain-nya)
2. [Arsitektur Jaringan Distribusi](#2-arsitektur-jaringan-distribusi)
3. [Alur Transaksi End-to-End](#3-alur-transaksi-end-to-end)
4. [KPI Inti & Cara Menghitungnya](#4-kpi-inti--cara-menghitungnya)
5. [Model Data — Star Schema](#5-model-data--star-schema)
6. [Manajemen Persediaan — Konsep & Formula](#6-manajemen-persediaan--konsep--formula)
7. [Pemasok & Purchase Order](#7-pemasok--purchase-order)
8. [Logistik & 3PL](#8-logistik--3pl)
9. [Klasifikasi ABC & Prioritas SKU](#9-klasifikasi-abc--prioritas-sku)
10. [Root Cause Analysis — Kerangka Diagnosis](#10-root-cause-analysis--kerangka-diagnosis)
11. [Business Impact Simulation — Cara Kerja Model Skenario](#11-business-impact-simulation--cara-kerja-model-skenario)
12. [Ground Truth Proyek Ini](#12-ground-truth-proyek-ini)
13. [Jebakan Analisis yang Harus Dihindari](#13-jebakan-analisis-yang-harus-dihindari)
14. [Glosarium Cepat](#14-glosarium-cepat)

---

## 1. Apa Itu FMCG & Tantangan Supply Chain-nya

### Definisi
**FMCG (Fast-Moving Consumer Goods)** adalah produk konsumen dengan perputaran tinggi, margin relatif tipis, dan siklus hidup pendek — meliputi makanan kemasan, minuman, perawatan pribadi, dan produk kebersihan rumah tangga. Contoh: sabun, mie instan, kopi sachet, detergen.

### Karakteristik yang Mempengaruhi Supply Chain

| Karakteristik | Implikasi Operasional |
| :--- | :--- |
| **Demand bervolume tinggi & berfluktuasi** | Reorder point statis mudah meleset; butuh perhitungan berbasis variansi |
| **Margin tipis** | Stockout langsung merusak profitabilitas; carrying cost harus dijaga minimum |
| **Produk perishable / ekspiry** | Kelebihan stok pun berisiko (kadaluarsa, write-off) |
| **Jaringan distribusi multi-tier** | Supplier → DC Regional → Retailer → End Consumer; tiap lapis menambah lead time dan variabilitas |
| **Ekspektasi service level tinggi** | Retailer besar menetapkan SLA ketat (OTIF ≥ 95% di industri); penalti kontraktual bila meleset |
| **Banyak SKU, pola demand berbeda** | SKU fast-moving butuh safety stock lebih besar; SKU slow tidak perlu stok besar |

### Tiga Risiko Paling Umum di FMCG
1. **Upstream**: Supplier terlambat → stok habis sebelum reorder terpenuhi
2. **Internal**: Kebijakan reorder point statis → tidak adaptif terhadap perubahan demand atau variasi lead time
3. **Downstream**: Carrier underperforming → produk tersedia di gudang tapi terlambat sampai ke pelanggan

---

## 2. Arsitektur Jaringan Distribusi

```
[ Supplier Tier-1 ]
        |
   Purchase Order (PO)
        |
        v
[ Distribution Center / Gudang Regional ]
   (Gudang A Jakarta | Gudang B Surabaya | Gudang C Bandung)
        |
   Sales Order → Shipment → 3PL Carrier
        |
        v
[ Pelanggan / Retailer ]
```

### Komponen Jaringan dalam Proyek Ini

| Entitas | Jumlah | Peran |
| :--- | :---: | :--- |
| **SKU (produk)** | 48 | Unit analisis terkecil untuk stok dan demand |
| **Gudang (DC)** | 3 | Jakarta, Surabaya, Bandung — titik penyimpanan & pengiriman |
| **Supplier** | 8 | Menyediakan stok via PO; masing-masing memiliki variabilitas lead time berbeda |
| **Pelanggan** | 36 | Pengirim sales order; B2B (retailer, modern trade) |
| **Carrier / 3PL** | 4 | Mitra Trucking, SiCepat GOKIL, J&T Cargo, lainnya |

### Perbedaan Gudang vs. Distribution Center
- **Gudang tradisional**: penyimpanan pasif
- **Distribution Center (DC)**: aktif mengatur aliran masuk (inbound PO) dan keluar (outbound shipment); ini yang digunakan dalam proyek

---

## 3. Alur Transaksi End-to-End

```
1. Pelanggan → Sales Order (fact_sales_order_lines)
       ↓ Stok tersedia? → Fulfilled / Partial / Unfulfilled
       ↓ Carrier dijadwalkan?
2. Gudang → Shipment (fact_shipments)
       ↓ Delivered ≤ promised_date?
3. OTIF dievaluasi (on_time_flag AND in_full_flag)

Paralel (replenishment loop):
4. Gudang → Purchase Order ke Supplier (fact_purchase_order_lines)
5. Supplier → Kirim barang → Diterima di gudang
6. Stok di-update (fact_inventory_daily: opening + received - shipped = closing)
```

### Aturan Penting dalam Simulasi Ini
- Tidak ada **backorder** — kekurangan unit langsung tidak terpenuhi, bukan ditunda
- Tidak ada **return** atau **shrinkage**
- `shipped_date` = `order_date` jika stok tersedia saat order masuk
- `closing_qty` tidak bisa negatif

---

## 4. KPI Inti & Cara Menghitungnya

### 4.1 Fill Rate (Unit)

**Definisi:** Proporsi unit yang berhasil dipenuhi dari total unit yang dipesan.

```
Fill Rate = SUM(fulfilled_qty) / SUM(ordered_qty)
           pada fact_sales_order_lines
```

> Grain: **line item** (satu SKU dalam satu order). Tidak memperhitungkan ketepatan waktu.
> Proyek ini: **74.15%** (72,721 unit terpenuhi dari 98,069 unit dipesan)

**Jebakan umum:** Fill rate yang tinggi tidak menjamin OTIF tinggi — produk bisa terpenuhi lengkap tapi terlambat dikirim.

---

### 4.2 OTIF (On-Time In-Full)

**Definisi:** Proporsi *sales order* yang terpenuhi 100% kuantitasnya DAN diterima pelanggan ≤ tanggal janji.

```
OTIF_Flag = 1  JIKA (shipped_qty = ordered_qty) AND (delivered_date ≤ promised_date)
           ELSE 0

OTIF Rate = SUM(otif_flag) / COUNT(DISTINCT order_id)
            pada fact_shipments
```

> Grain: **order** (bukan line item). Satu order gagal = seluruh order dihitung gagal.
> Proyek ini: **42.90%** (2,113 dari 4,925 order berhasil OTIF)

**Dekomposisi OTIF Failure:**

```
Total Order: 4,925
├── OTIF Berhasil          : 2,113  (42.90%) ← target
├── Lengkap, Terlambat     :   848  (17.22%) ← masalah carrier
├── Tepat Waktu, Tidak Full: 1,022  (20.75%) ← masalah stok
└── Gagal Keduanya         :   942  (19.13%) ← masalah gabungan
```

---

### 4.3 Supplier OTD (On-Time Delivery)

**Definisi:** Proporsi Purchase Order yang diterima gudang ≤ tanggal yang dijanjikan supplier.

```
Supplier OTD = COUNT(PO di mana actual_receipt_date ≤ expected_date)
               / COUNT(PO dengan status received)
               — PO dengan status "open" DIKECUALIKAN dari denominator
```

> Proyek ini: **35.95%** agregat — hanya 1 dari 3 PO tiba tepat waktu.
> Supplier terburuk: PT Niaga Mitra (2.65%), PT Karya Maju Industri (3.74%), PT Surya Ritelindo (5.04%)

**Mengapa PO "open" dikecualikan?** Karena PO yang belum selesai belum bisa dinilai keterlambatannya. Memasukkannya ke denominator akan secara artifisial menurunkan OTD.

---

### 4.4 Stockout Share (Daily)

**Definisi:** Proporsi snapshot SKU-gudang-hari dengan stok penutup = 0.

```
Stockout Share = COUNT(snapshot rows di mana closing_qty = 0)
                 / COUNT(total snapshot rows)
                 pada fact_inventory_daily
```

> Proyek ini: **14.31%** (3,772 dari 26,352 snapshot harian = nol stok)
> 68 dari 144 kombinasi SKU-gudang di bawah ambang ROP service level 95%

**Penting:** Ini bukan proporsi pesanan yang gagal — ini proporsi *hari* di mana stok = 0 untuk suatu SKU di suatu gudang. Angka ini bisa tinggi bahkan jika demand sedang rendah pada hari itu.

---

### 4.5 Unserved Order Value

**Definisi:** Estimasi nilai permintaan yang tidak terpenuhi — **indikator peluang**, bukan "lost sales yang sudah terbukti."

```
Unserved Order Value = SUM( (ordered_qty - fulfilled_qty) × unit_price )
```

> Proyek ini: ~Rp 1,013,750,500
> Interpretasi: Jika semua permintaan terpenuhi, revenue bisa lebih tinggi sebesar nilai ini. Namun ada asumsi bahwa demand tidak diganti ke kompetitor dan harga tidak berubah.

---

### 4.6 Carrier On-Time Rate

**Definisi:** Proporsi shipment yang dikirim oleh suatu carrier dan tiba ≤ promised_date, **per carrier**.

```
Carrier On-Time = COUNT(order di mana on_time_flag = 1 AND carrier = X)
                  / COUNT(order yang dikirim oleh carrier X)
```

> Mitra Trucking: **48.88%** — terendah
> SiCepat GOKIL: 69.79%
> J&T Cargo: 69.39%

---

### 4.7 Inventory Turnover

**Definisi:** Seberapa cepat persediaan berputar dalam periode tertentu.

```
Inventory Turnover = COGS Periode / Rata-rata Nilai Persediaan Periode

Rata-rata Nilai Persediaan = AVG(daily closing inventory value)
                             bukan (awal + akhir) / 2
```

> Turnover **tidak diannualisasi** dalam proyek ini karena periode hanya 6 bulan.

---

### 4.8 Gross Profit & Gross Margin

```
Gross Profit = Revenue Fulfilled − COGS Terkait
Gross Margin = Gross Profit / Revenue Fulfilled × 100%
```

> Proyek ini: Revenue Rp 3.32 B | COGS Rp 2.22 B | Gross Profit ≈ Rp 1.11 B
> **Belum** mengurangkan freight, overhead, atau SG&A.

---

## 5. Model Data — Star Schema

### Struktur Tabel

```
                    ┌─────────────────┐
                    │  dim_products   │
                    │  (48 SKU)       │
                    └────────┬────────┘
                             │ 1:N
         ┌───────────────────┼───────────────────┐
         │                   │                   │
         v                   v                   v
┌──────────────────┐ ┌────────────────┐ ┌─────────────────────────┐
│fact_sales_order_ │ │fact_shipments  │ │fact_purchase_order_lines│
│lines             │ │(grain: order)  │ │(grain: PO line)         │
│(grain: order×SKU)│ └───────┬────────┘ └───────────┬─────────────┘
└──────────────────┘         │                      │
         │                   │                      │
         └───────────────────┼──────────────────────┘
                             │ N:1
              ┌──────────────┼──────────────┐
              v              v              v
      ┌──────────┐  ┌──────────────┐  ┌────────────┐
      │dim_       │  │dim_warehouses│  │dim_suppliers│
      │customers  │  │(3 gudang)    │  │(8 supplier) │
      └──────────┘  └──────────────┘  └────────────┘
                             │
                    ┌────────┴────────┐
                    │fact_inventory_  │
                    │daily            │
                    │(grain: sku×wh×day)│
                    └─────────────────┘
```

### Aturan JOIN Kritis

| Aturan | Penjelasan |
| :--- | :--- |
| **Jangan JOIN fact-to-fact langsung** | `fact_sales_order_lines` ↔ `fact_shipments` harus melalui agregasi atau subquery |
| **Freight bisa terduplikasi** | Satu `order_id` muncul banyak kali di `fact_sales_order_lines`; jika JOIN ke `fact_shipments` tanpa agregasi, `freight_cost` terhitung ganda |
| **OTIF dihitung di grain order** | Jangan hitung OTIF dari `fact_sales_order_lines` — gunakan `fact_shipments` |
| **Stok harian tidak boleh di-SUM lintas hari** | `SUM(closing_qty)` lintas tanggal = double counting; gunakan `AVG` atau filter satu tanggal spesifik |

---

## 6. Manajemen Persediaan — Konsep & Formula

### 6.1 Konsep Dasar Stok

| Istilah | Definisi |
| :--- | :--- |
| **Safety Stock (SS)** | Buffer stok ekstra untuk menyerap ketidakpastian demand dan lead time |
| **Reorder Point (ROP)** | Titik stok di mana PO harus segera dibuat; jika stok = ROP, pesan sekarang |
| **Lead Time** | Waktu dari PO dikirim ke supplier sampai barang diterima di gudang |
| **Days of Supply (DOS)** | Stok saat ini / rata-rata demand harian = berapa hari stok bertahan |
| **Opening Stock** | Stok awal hari |
| **Closing Stock** | Stok akhir hari = Opening + Received − Shipped |
| **Dead Stock** | Stok yang tidak bergerak dalam waktu lama; overhead biaya simpan |

---

### 6.2 Formula Safety Stock Statis (Sederhana)

Digunakan ketika demand dan lead time dianggap konstan:

```
Safety Stock = Z × σ_demand × √lead_time

Reorder Point (ROP) = (Demand_harian_rata-rata × Lead_time_rata-rata) + Safety Stock
```

**Keterbatasan:** Mengasumsikan variabilitas lead time = 0. Kurang akurat untuk FMCG dengan supplier tidak konsisten.

---

### 6.3 Formula Safety Stock Dinamis — Joint Uncertainty (Digunakan dalam Proyek Ini)

Memperhitungkan ketidakpastian **demand** (σ_D) dan **lead time** (σ_L) secara bersamaan:

```
Safety Stock = Z × √( L̄ × σ_D² + D̄² × σ_L² )

Reorder Point (ROP) = ⌈ D̄ × L̄ + Safety Stock ⌉

Keterangan:
  Z   = z-score service level (90% → 1.282 | 95% → 1.645 | 98% → 2.054)
  D̄   = rata-rata demand harian (unit/hari)
  L̄   = rata-rata lead time (hari)
  σ_D = standar deviasi demand harian
  σ_L = standar deviasi lead time
```

**Mengapa lebih baik?** Supplier FMCG sering terlambat dengan variasi besar. Jika σ_L diabaikan, safety stock akan terlalu rendah tepat saat supplier bermasalah.

---

### 6.4 Hubungan Service Level dan Z-Score

| Service Level | Z-Score | Interpretasi |
| :---: | :---: | :--- |
| 90% | 1.282 | Stok habis 1 dari 10 siklus pemesanan |
| 95% | 1.645 | Stok habis 1 dari 20 siklus (standar industri FMCG mid-tier) |
| 98% | 2.054 | Stok habis 1 dari 50 siklus (standar distribusi premium) |
| 99% | 2.326 | Stok habis 1 dari 100 siklus |

**Trade-off:** Service level lebih tinggi = safety stock lebih besar = biaya simpan lebih tinggi. Tidak semua SKU perlu 99% — SKU Class C dengan demand rendah bisa efisien di 90%.

---

### 6.5 Holding Cost (Biaya Simpan)

```
Annual Holding Cost = Nilai Inventori × Holding Rate (% per tahun)

Proyek ini menggunakan: Holding Rate = 20% per tahun
```

Komponen holding cost dalam dunia nyata: modal tertahan, biaya gudang, asuransi, kerusakan, dan obsolescence.

---

### 6.6 Inventory Balance Equation

Ini adalah persamaan akuntansi stok dasar — harus selalu berlaku tanpa pengecualian:

```
Opening_qty + Received_qty − Shipped_qty = Closing_qty
```

Dalam proyek ini, 26,352 snapshot harian semuanya memenuhi persamaan ini (divalidasi oleh `test_project.py`).

---

## 7. Pemasok & Purchase Order

### 7.1 Alur Purchase Order

```
1. Gudang deteksi stok ≤ ROP
2. Purchase Requisition dibuat
3. PO dikirim ke supplier (order_date di fact_purchase_order_lines)
4. Supplier konfirmasi expected_date (tanggal janji)
5. Supplier kirim barang
6. Gudang terima barang (actual_receipt_date)
7. Stok di-update (received_qty di fact_inventory_daily)
```

### 7.2 Status PO

| Status | Makna |
| :--- | :--- |
| `open` | PO sudah dikirim ke supplier, belum diterima. **Dikecualikan dari denominator OTD.** |
| `received_full` | Semua unit diterima |
| `received_partial` | Sebagian unit diterima; sisa dibatalkan (penyederhanaan simulasi) |

### 7.3 Metrik Evaluasi Supplier

| Metrik | Formula | Interpretasi |
| :--- | :--- | :--- |
| **OTD Rate** | PO diterima tepat waktu / total PO received | Keandalan waktu pengiriman |
| **Average Delay (hari)** | AVG(actual_receipt_date − expected_date) untuk PO terlambat | Besarnya keterlambatan |
| **Lead Time Variance** | STDEV(actual_receipt_date − order_date) | Konsistensi lead time |
| **Fill Rate PO** | received_qty / ordered_qty | Kelengkapan pengiriman supplier |

### 7.4 Supplier Profil Proyek Ini

| Supplier | OTD Rate | Karakteristik |
| :--- | :---: | :--- |
| PT Niaga Mitra | 2.65% | Paling bermasalah — hampir selalu terlambat |
| PT Karya Maju Industri | 3.74% | Sangat tidak reliabel |
| PT Surya Ritelindo | 5.04% | Ketiga terburuk |
| PT Nusantara Kemasan | 63.8% | Relatif terbaik |
| PT Pangan Sentosa | 62.4% | Reliabel kedua |

---

## 8. Logistik & 3PL

### 8.1 Metrik Carrier

| Metrik | Formula |
| :--- | :--- |
| **On-Time Rate** | ORDER dengan delivered_date ≤ promised_date / total ORDER per carrier |
| **Cost per Shipment** | SUM(freight_cost) / COUNT(shipment) per carrier |
| **Volume Share** | ORDER dikirim carrier X / total ORDER |

### 8.2 Profil Carrier Proyek Ini

| Carrier | On-Time Rate | Freight/Shipment | Catatan |
| :--- | :---: | :---: | :--- |
| Mitra Trucking | 48.88% | Rp 32,461 | Terburuk; biaya setara carrier lebih baik |
| SiCepat GOKIL | 69.79% | Rp ~32,000 | On-time terbaik |
| J&T Cargo | 69.39% | Rp ~31,000 | Kompetitif |

**Insight kritis:** Mitra Trucking menyebabkan 848 order menjadi terlambat meskipun dikemas lengkap. Biaya per shipment hampir sama dengan carrier yang jauh lebih baik — ini adalah kasus reallocation volume, bukan negosiasi harga.

### 8.3 OTIF Failure karena Carrier

Carrier bottleneck menciptakan kasus "Late-but-Full" — kategori `on_time_flag = 0` dan `in_full_flag = 1`:

```
Late-but-Full Orders = COUNT(order dengan on_time_flag=0 AND in_full_flag=1)
                     = 848 order = 17.22% dari total
```

---

## 9. Klasifikasi ABC & Prioritas SKU

### 9.1 Definisi Kelas

Metode ABC membagi SKU berdasarkan kontribusi revenue kumulatif (Pareto principle):

| Kelas | Kriteria Revenue Kumulatif | Jumlah SKU | Kebijakan Stok |
| :---: | :---: | :---: | :--- |
| **A** | 0–80% | ~19 SKU | Service level 95–98%; reorder ketat; monitoring harian |
| **B** | 80–95% | ~14 SKU | Service level 90–95%; replenishment standar |
| **C** | 95–100% | ~15 SKU | Service level 85–90%; reorder cycle lebih panjang |

### 9.2 SQL untuk Klasifikasi ABC

```sql
WITH revenue_by_sku AS (
  SELECT
    p.sku, p.product_name,
    SUM(s.revenue) AS total_revenue
  FROM fact_sales_order_lines s
  JOIN dim_products p ON s.product_id = p.product_id
  GROUP BY p.product_id
),
cumulative AS (
  SELECT
    sku, product_name, total_revenue,
    SUM(total_revenue) OVER (ORDER BY total_revenue DESC
      ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_rev,
    SUM(total_revenue) OVER () AS grand_total
  FROM revenue_by_sku
)
SELECT
  sku, product_name, total_revenue,
  ROUND(100.0 * cumulative_rev / grand_total, 2) AS cum_rev_pct,
  CASE
    WHEN 100.0 * cumulative_rev / grand_total <= 80 THEN 'A'
    WHEN 100.0 * cumulative_rev / grand_total <= 95 THEN 'B'
    ELSE 'C'
  END AS abc_class
FROM cumulative
ORDER BY total_revenue DESC;
```

> Window function `ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW` memastikan SKU di batas 80%/95% diklasifikasikan tepat.

---

## 10. Root Cause Analysis — Kerangka Diagnosis

### 10.1 Tiga Friction Point dalam Proyek Ini

```
Masalah:  OTIF 42.90% (sangat di bawah benchmark ≥ 90%)
           |
           ├── PENYEBAB 1: Supplier tidak reliabel
           │   └── OTD 35.95% → PO sering terlambat → stok habis sebelum refill
           │
           ├── PENYEBAB 2: Reorder Point tidak adaptif
           │   └── 68/144 SKU-gudang di bawah ambang ROP 95%
           │   └── Stok pengaman terlalu kecil untuk variabilitas demand + lead time
           │
           └── PENYEBAB 3: Carrier underperforming
               └── Mitra Trucking on-time 48.88% vs. peer 69%+
               └── 848 order dikemas penuh tapi terlambat
```

### 10.2 Urutan Diagnosis yang Benar

1. **Cek OTIF secara keseluruhan** → seberapa parah masalahnya?
2. **Dekomposisi OTIF** → pisahkan masalah stok (in_full) dari masalah waktu (on_time)
3. **Analisis per gudang** → apakah masalah lokal atau sistemik?
4. **Analisis stok harian** → SKU dan gudang mana yang sering stockout?
5. **Analisis supplier** → apakah ada korelasi antara supplier OTD rendah dan SKU stockout tinggi?
6. **Analisis carrier** → carrier mana penyebab keterlambatan terbesar?
7. **Kuantifikasi opportunity cost** → berapa nilai demand yang tidak terpenuhi?

### 10.3 Perbedaan Korelasi vs. Kausalitas

| Temuan | Status |
| :--- | :--- |
| "Supplier X berada di OTD terendah DAN produknya sering stockout" | **Korelasi** — perlu diuji lebih lanjut |
| "Setelah PO Supplier X terlambat, stok SKU-nya turun ke nol dalam N hari" | **Indikasi kausalitas** (tapi masih perlu validasi) |
| "Menaikkan safety stock PASTI mengurangi stockout" | **Asumsi** — berlaku jika demand dan lead time tidak berubah drastis |

---

## 11. Business Impact Simulation — Cara Kerja Model Skenario

### 11.1 Tiga Skenario yang Dimodelkan

| Skenario | Service Level Target | Intervensi Utama |
| :--- | :---: | :--- |
| **A: Fast Stabilization** | 90% (Z=1.282) | Realokasi carrier + pilot ROP gudang Jakarta |
| **B: Recommended** | 95% (Z=1.645) | Penalti SLA supplier + ROP semua 68 node rentan |
| **C: Full Transformation** | 98% (Z=2.054) | Dual-sourcing + dedicated freight corridor |

### 11.2 Cara Menghitung Recoverable Revenue (Scenario B)

```
Langkah 1: Hitung Safety Stock baru untuk 68 SKU-gudang di bawah ambang
           SS_baru = 1.645 × √(L̄ × σ_D² + D̄² × σ_L²)

Langkah 2: Estimasi Fill Rate improvement
           Jika stockout share turun dari 14.31% → 4.20%,
           berarti ~70.6% dari "hari stockout" berhasil dieliminasi

Langkah 3: Estimasi demand yang sebelumnya tidak terpenuhi dan kini bisa dipenuhi
           Recoverable = 58% × Rp 1,013,750,500 ≈ Rp 587,900,000

Langkah 4: Hitung incremental holding cost
           Annual Holding Cost 95% = Rp 29,378,200
           Annual Holding Cost 90% = Rp 23,021,500
           Incremental = Rp 6,356,700/tahun

Langkah 5: Hitung ROI Ratio
           ROI = Rp 587,900,000 / Rp 6,356,700 ≈ 92.4x
```

> **Penting:** "Recoverable Revenue" adalah estimasi indikatif. Asumsinya: demand yang sebelumnya tidak terpenuhi tidak digantikan ke kompetitor, dan permintaan bersifat stabil.

### 11.3 Interpretasi ROI yang Benar

- **92.4x** bukan berarti profit bersih 92x lipat — ini rasio antara benefit yang dimodelkan vs. incremental holding cost
- Belum memperhitungkan: biaya implementasi, training, biaya renegosiasi kontrak supplier, dan biaya IT monitoring
- Digunakan sebagai argumen *prioritas* bukan *guaranteed return*

---

## 12. Ground Truth Proyek Ini

> Angka-angka ini adalah satu-satunya yang valid. Jangan gunakan nilai lain dalam analisis, presentasi, atau portfolio.

### Dataset Summary

| Dimensi | Nilai |
| :--- | ---: |
| Periode | 1 Apr – 30 Sep 2026 |
| Jumlah SKU | 48 |
| Jumlah Gudang | 3 |
| Jumlah Supplier | 8 |
| Jumlah Pelanggan | 36 |
| Jumlah Sales Order | 4,925 |
| Jumlah Sales Order Line | 8,534 |
| Jumlah Inventory Snapshots | 26,352 |

### KPI Aktual

| KPI | Nilai Aktual | Target Benchmark |
| :--- | :---: | :---: |
| **Fill Rate (Unit)** | 74.15% | ≥ 85.0% |
| **OTIF (Order)** | 42.90% | ≥ 90.0% |
| **In-Full Rate** | 60.12% | ≥ 95.0% |
| **On-Time Rate (Order)** | 63.65% | ≥ 95.0% |
| **Supplier OTD** | 35.95% | ≥ 85.0% |
| **Daily Stockout Share** | 14.31% | ≤ 5.0% |

### Finansial

| Metrik | Nilai |
| :--- | ---: |
| Revenue Fulfilled | Rp 3,324,652,500 |
| COGS | Rp 2,216,806,500 |
| Freight Cost | Rp 159,946,000 |
| Units Dipesan | 98,069 |
| Units Dipenuhi | 72,721 |
| Unserved Order Value (indikatif) | ~Rp 1,013,750,500 |

### Supplier OTD Terendah

| Supplier | OTD Rate |
| :--- | :---: |
| PT Niaga Mitra | 2.65% |
| PT Karya Maju Industri | 3.74% |
| PT Surya Ritelindo | 5.04% |

### Carrier Performance

| Carrier | On-Time Rate | Freight/Shipment |
| :--- | :---: | :---: |
| Mitra Trucking | 48.88% | Rp 32,461 |
| SiCepat GOKIL | 69.79% | ~Rp 32,000 |
| J&T Cargo | 69.39% | ~Rp 31,000 |

### Impact Simulation Results

| Skenario | Fill Rate | OTIF | Demand Recovered | Holding Cost Tambahan | ROI |
| :--- | :---: | :---: | :---: | :---: | :---: |
| Baseline (Actual) | 74.15% | 42.90% | Rp 0 | — | — |
| A: Fast Stabilization (Z=1.282) | 81.50% | 58.20% | Rp 324.5 M | Rp 0 | Infinite |
| **B: Recommended (Z=1.645)** | **88.60%** | **68.40%** | **Rp 587.9 M** | **+Rp 6.36 M/yr** | **92.4x** |
| C: Full Transformation (Z=2.054) | 94.20% | 78.90% | Rp 780.5 M | +Rp 13.58 M/yr | 57.5x |

---

## 13. Jebakan Analisis yang Harus Dihindari

### Kesalahan Teknis SQL

| Jebakan | Contoh Salah | Cara Benar |
| :--- | :--- | :--- |
| **Duplikasi freight** | `JOIN fact_shipments ON order_id` langsung dari fact_sales_order_lines | Agregasi dulu per order_id, baru JOIN |
| **OTIF dari fact_sales_order_lines** | `AVG(otif_flag)` dari tabel order lines | Gunakan `fact_shipments` (grain order) |
| **SUM stok harian lintas tanggal** | `SUM(closing_qty)` dari fact_inventory_daily | `AVG(closing_qty)` atau filter satu tanggal |
| **OTD dengan PO open** | Menyertakan PO status 'open' di denominator | `WHERE status IN ('received_full', 'received_partial')` |

### Kesalahan Interpretasi Bisnis

| Pernyataan Salah | Versi Benar |
| :--- | :--- |
| "Stockout 14.31% berarti 14.31% demand gagal dipenuhi" | Stockout share = proporsi *hari stok nol*, bukan proporsi demand gagal |
| "Unserved Value Rp 1 M adalah lost revenue" | Ini *indikasi* peluang; bukan confirmed lost sales |
| "ROI 92.4x adalah keuntungan bersih" | Ini rasio benefit-to-holding-cost; belum termasuk biaya implementasi lain |
| "Supplier X penyebab stockout SKU A" | Ini korelasi kuat; kausalitas butuh validasi tambahan |
| "OTIF 42.9% berarti 57.1% pelanggan tidak puas" | Ketidakpuasan pelanggan bergantung pada ekspektasi dan alternatif; OTIF mengukur pemenuhan SLA, bukan persepsi |

---

## 14. Glosarium Cepat

| Istilah | Definisi Singkat |
| :--- | :--- |
| **ABC Analysis** | Klasifikasi produk berdasarkan kontribusi revenue (A=80%, B=15%, C=5%) |
| **Backorder** | Pesanan yang belum bisa dipenuhi tapi akan dipenuhi saat stok datang — *tidak dimodelkan* dalam proyek ini |
| **Carrier / 3PL** | Perusahaan logistik pihak ketiga yang mengirim barang ke pelanggan |
| **Closing Stock** | Stok akhir hari = Opening + Received − Shipped |
| **COGS** | Cost of Goods Sold — biaya produksi/pembelian barang yang terjual |
| **DC (Distribution Center)** | Gudang yang mengelola aliran masuk (dari supplier) dan keluar (ke pelanggan) |
| **Dead Stock** | Stok yang tidak bergerak dalam waktu lama; pemborosan modal |
| **DOS (Days of Supply)** | Stok saat ini / demand harian rata-rata; berapa hari stok bertahan |
| **Dual Sourcing** | Memiliki dua atau lebih supplier untuk SKU yang sama, mengurangi risiko supplier tunggal |
| **Fill Rate** | Proporsi unit yang terpenuhi dari unit yang dipesan (grain: line item) |
| **Freight Cost** | Biaya pengiriman ke pelanggan, dibayar per shipment |
| **Grain** | Level detail terkecil dalam satu tabel (contoh: "grain fact_shipments = satu order") |
| **Holding Cost** | Biaya menyimpan inventori (modal, gudang, kerusakan) — diasumsikan 20%/tahun |
| **In-Full Rate** | Proporsi order yang dikirim 100% lengkap kuantitasnya (tidak memperhatikan waktu) |
| **Lead Time** | Waktu dari pembuatan PO sampai barang diterima di gudang |
| **On-Time Rate** | Proporsi order yang diterima pelanggan ≤ promised_date (tidak memperhatikan kelengkapan) |
| **OTIF** | On-Time In-Full — order dikirim lengkap DAN tepat waktu (grain: order) |
| **OTD** | On-Time Delivery — untuk supplier: PO diterima ≤ expected_date |
| **PO (Purchase Order)** | Dokumen pembelian dari gudang ke supplier |
| **ROP (Reorder Point)** | Titik stok di mana pemesanan ulang harus segera dilakukan |
| **Safety Stock** | Stok buffer ekstra di atas stok minimum untuk menyerap ketidakpastian |
| **Service Level** | Probabilitas tidak terjadi stockout dalam satu siklus pemesanan (90%, 95%, 98%) |
| **SKU** | Stock Keeping Unit — satu unit produk yang bisa dibedakan dari produk lain |
| **Snapshot** | Rekaman kondisi stok pada satu hari tertentu untuk satu SKU di satu gudang |
| **Stockout** | Kondisi stok = 0; pesanan baru tidak bisa dipenuhi |
| **Star Schema** | Desain database dimensional: fact tables di tengah, dimension tables di pinggir |
| **Unserved Order Value** | Nilai potensial demand yang tidak terpenuhi — indikator, bukan guaranteed revenue |
| **WAPE** | Weighted Absolute Percentage Error — metrik akurasi forecast yang lebih stabil dari MAPE untuk demand intermittent |
| **Z-Score** | Faktor pengali dalam formula safety stock yang menentukan level proteksi stockout |

---

*Dokumen ini di-generate berdasarkan analisis proyek SCM FMCG Portfolio — Pandu Pramana, 2026.*
*Seluruh data adalah sintetis. Tidak mewakili transaksi atau benchmark perusahaan nyata.*

