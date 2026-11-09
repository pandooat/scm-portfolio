# MODUL 3 — Root Cause Analysis Supply Chain dengan SQL

**Untuk:** pemula dengan sertifikat Google Data Analytics  
**Kasus:** distributor FMCG fiktif dengan tiga gudang, 48 SKU, delapan supplier, April–September 2026.  
**Perkiraan waktu:** 5 sesi × 60–90 menit.  
**Prasyarat:** telah membuka database `02_Database/scm_portfolio.sqlite` di DB Browser for SQLite dan menyelesaikan Modul 2.  
**PENTING:** SEMUA DATA SINTETIS. Perhitungan analitis adalah hasil dataset simulasi, bukan statistik perusahaan nyata.

## Target kompetensi

Setelah modul ini, Anda harus bisa:
1. Menyebutkan perbedaan **gejala, hipotesis akar masalah, dan bukti sebab-akibat**.
2. Menggunakan SQL `GROUP BY`, `JOIN`, `CASE`, `WITH`/CTE untuk memeriksa KPI berdasarkan waktu, gudang, SKU, supplier, dan carrier.
3. Menjelaskan **grain** (satu baris mewakili apa) agar KPI tidak terduplikasi.
4. Menyusun memo bisnis satu halaman, dengan temuan yang diverifikasi dan rekomendasi yang masih memerlukan uji.

## Peta berpikir

**Gejala:** OTIF hanya 42,90%, fill rate unit 74,15% selama periode simulasi.  
**Pecah menjadi masalah:** tidak lengkap vs terlambat, per bulan, per gudang.  
**Cari konsentrasi:** SKU × gudang, nilai order tidak terpenuhi, hari stok nol.  
**Selidiki mekanisme yang mungkin:** keterlambatan purchase order, ketersediaan stok, dan on-time carrier.  
**Validasi:** gunakan waktu kejadian, grain transaksi, pembanding dan ketidakpastian.  
**Saran bisnis:** rancang pilot replenishment dan exception monitoring, ukur dampak sebelum/sesudah dengan baseline yang dapat dibandingkan.

---

## Sesi 1 — Temukan kapan kinerja menurun (Q1 dan Q2)

Buka `03_SQL/MODUL_3_ROOT_CAUSE_QUERIES.sql`. Jalankan **Q1** di tab *Execute SQL*.

| Bulan | Ordered (unit) | Fulfilled (unit) | Unit fill rate |
|---|---:|---:|---:|
| Apr | 14.465 | 11.050 | 76,39% |
| Mei | 13.759 | 10.993 | 79,90% |
| Jun | 14.629 | 11.614 | 79,39% |
| Jul | 19.066 | 13.310 | 69,81% |
| Agu | 21.626 | 14.551 | 67,28% |
| Sep | 14.524 | 11.203 | 77,13% |

**Latihan:**
- Mengapa `SUM(fulfilled_qty) / SUM(ordered_qty)` berbeda dari `AVG(fulfilled_qty * 1.0 / ordered_qty)`? Jawaban: agregasi berbobot unit vs rata-rata tingkat pemenuhan per baris order; unit besar dan kecil mendapat bobot berbeda.
- Hitung kenaikan permintaan Agustus dibanding Juni. Apa bedanya *terjadi bersamaan* dengan *disebabkan oleh*?
- Jalankan **Q2**. Pada Agustus, gudang mana memiliki fill rate terendah?

**Bukti terverifikasi:** Agustus 2026 menunjukkan fill rate 67,28%, dan Warehouse Surabaya 65,60% pada bulan yang sama. **Belum terbukti:** lonjakan permintaan adalah penyebab tunggal.

## Sesi 2 — Prioritaskan SKU yang paling relevan (Q3)

Jalankan **Q3**. Query memakai dua CTE: `unfulfilled` dan `stockouts`. Kedua sumber data diakumulasi **lebih dulu** ke satu baris per `warehouse_id × product_id`, baru di-*JOIN*. Metode ini mencegah baris inventory harian mengalikan transaksi penjualan.

Tiga kombinasi prioritas berdasarkan *nilai order tidak terpenuhi* selama enam bulan:

| Gudang × SKU | Unit tak terpenuhi | Nilai indikatif (Rp) | Hari stok akhir nol |
|---|---:|---:|---:|
| Surabaya × SKU0039 | 827 | 44.658.000 | 87 |
| Surabaya × SKU0004 | 654 | 43.491.000 | 71 |
| Bandung × SKU0004 | 625 | 41.562.500 | 59 |

**Perhatian:** nilai tersebut *bukan lost sales yang terbukti*. Data ini tidak memodelkan backorder, substitusi produk, atau pembatalan pelanggan.

**Latihan:** Sebutkan dua alasan mengapa kombinasi SKU yang bernilai order tidak terpenuhi tertinggi layak diteliti pertama, dan dua alasan mengapa peringkat tersebut **belum** menjadi prioritas final (mis. profit margin, biaya intervensi, customer importance).

## Sesi 3 — Cocokkan timeline stok dan permintaan (Q4)

Fokus: **Warehouse Surabaya × SKU0039** pada Agustus 2026. Jalankan **Q4**.

Hasil yang perlu ditemukan:
- Agustus: 479 unit dipesan, 190 unit terpenuhi, **289 unit tidak terpenuhi**.
- Pada 11 Agustus, 58 unit dipesan, 0 dipenuhi, stok akhir 0.
- Pada 13 Agustus, stok masuk 85 unit, seluruh 14 unit pesanan hari itu terpenuhi, stok akhir 71.
- Pada 25 dan 26 Agustus terjadi lagi hari dengan unit tidak terpenuhi saat stok akhir 0; 27 Agustus tercatat 78 unit barang masuk.

**Apa yang bisa dikatakan?** Terdapat kesesuaian waktu antara kekurangan stok dan tidak terpenuhinya pesanan di data simulasi.  
**Apa yang belum bisa dikatakan?** Bahwa satu supplier atau satu petugas gudang menyebabkan seluruh masalah tersebut. Snapshot stok adalah stok **akhir hari**, tidak menunjukkan waktu intrahari setiap order.

**Latihan mandiri:** ambil lima hari yang menurut Anda penting dan buat tabel: tanggal, stok awal, stok masuk, permintaan, unit terpenuhi, stok akhir, unit tidak terpenuhi.

## Sesi 4 — Periksa supplier dan carrier (Q5, Q6, Q7)

Jalankan **Q5** dan **Q6** untuk SKU0039 Surabaya:
- Supplier utama dalam dataset adalah **PT Surya Ritelindo (Simulasi)**.
- Ada **10 PO sudah diterima**, dan **1 tepat waktu** (OTD = 10%). Rata-rata tanggal penerimaan **3,2 hari lebih lambat** dari tanggal yang dijanjikan dalam kelompok PO tersebut.
- Salah satu PO yang diharapkan diterima 11 Agustus baru diterima 13 Agustus (dua hari setelah janji).
- Ada PO yang masih terbuka; jangan masukkan tanggal kosong ke pembagian OTD untuk PO yang telah diterima. Evaluasi **overdue open PO** terpisah dengan tanggal cut-off yang eksplisit.

Jalankan **Q7** untuk membandingkan keterlambatan last-mile di Surabaya. Metrik `on_time_pct` dan `in_full_pct` harus dibaca **terpisah**. Carrier tidak otomatis bertanggung jawab terhadap kekurangan isi order.

**Latihan berpikir:** Susun dua hipotesis dan cara mengujinya.

| Hipotesis | Bukti awal | Data/uji tambahan |
|---|---|---|
| Keterlambatan supply memperpanjang periode stockout SKU0039 | PO terlambat dan tanggal stok kosong pada periode yang berdekatan | Track shipment inbound, tanggal PO dirilis, stok intrahari, permintaan sebelum/sesudah penerimaan |
| Carrier tertentu memiliki risiko delivery delay lebih tinggi | Perbedaan carrier on-time performance | Bandingkan rute, SLA, jarak, jenis order, gudang, dan tren per bulan |

**Ingat:** *Berkaitan* tidak sama dengan *terbukti menyebabkan*.

## Sesi 5 — Data quality dan executive recommendation (Q8 dan Q9)

Jalankan **Q8** untuk melihat kesalahan `JOIN` langsung antara `fact_shipments` (1 baris per order) dan `fact_sales_order_lines` (1+ baris per order).

- Total ongkir yang **salah** setelah join tanpa mengontrol grain: **Rp301.445.000**.
- Total ongkir **benar** di tabel shipment: **Rp159.946.000**.
- Selisih merupakan efek perkalian baris, bukan kenaikan biaya nyata.

Jalankan **Q9**: di dalam dataset sintetis ini, seluruh **1.796 hari kombinasi SKU×gudang yang memiliki unit order tidak terpenuhi** juga tercatat dengan stok akhir nol. Ini sesuai mekanisme pembangkitan data, **bukan** generalisasi operasi gudang nyata.

**Tugas akhir:** buat memo 200–250 kata:
1. **Masalah:** periode, definisi KPI, angka baseline.
2. **Temuan:** bulan/gudang/SKU prioritas dan bagaimana Anda mengukurnya.
3. **Hipotesis:** pasokan terlambat dan kurangnya stok; nyatakan bahwa kausalitas belum diuji.
4. **Rekomendasi:** pilot pemantauan PO overdue, review replenishment SKU0039 Surabaya, dan evaluasi carrier yang setara kondisi operasionalnya.
5. **Pengukuran:** pantau fill rate SKU, stockout days, supplier OTD, OTIF, biaya stok dan logistik setelah uji.

## Pertanyaan technical interview

1. Mengapa Anda menggunakan `SUM(fulfilled_qty)/SUM(ordered_qty)` dan bukan `AVG()`?
2. Apa bahayanya menggabungkan dua fact table yang grain-nya berbeda?
3. Apakah 87 hari stok akhir nol membuktikan terjadinya 87 hari gagal layanan pelanggan? Mengapa?
4. Bagaimana Anda membedakan indikasi supplier bermasalah dari penyebab stockout yang terverifikasi?
5. Jika replenishment menaikkan fill rate tetapi membuat persediaan jauh lebih mahal, bagaimana Anda mengevaluasi keberhasilan?

### Rubrik penilaian diri (100 poin)

| Aspek | Bobot |
|---|---:|
| Semua 9 query dapat dijalankan dan hasilnya valid | 30 |
| Penjelasan grain & tidak melakukan double counting | 20 |
| Analisis terstruktur: gejala → hipotesis → bukti | 20 |
| Kejujuran interpretasi dan keterbatasan data | 15 |
| Rekomendasi yang terukur, jelas, dan layak diuji | 15 |

**Lulus latihan** bila mencapai setidaknya 80/100 *berdasarkan evaluasi kemampuan*, bukan hanya berhasil menyalin jawaban.

## Cara menjalankan pengujian file jawaban

Buka terminal di folder proyek lalu jalankan:

```bash
python 03_SQL/test_module_3.py
```

Harus muncul pesan `PASS: 9 root cause queries verified against the local synthetic database.` Pengujian SQL otomatis ini memastikan bentuk hasil, angka kunci dan hubungan dasar sesuai dataset. Pengujian **tidak** membuktikan kebenaran kausal atau menguji kemampuan interview.

**Selanjutnya:** Modul 4 (Power BI), bangun dashboard *Inventory Risk & Procurement Exceptions* dari CSV, kemudian buat ringkasan rekomendasi yang bisa dipresentasikan selama 3–5 menit.
