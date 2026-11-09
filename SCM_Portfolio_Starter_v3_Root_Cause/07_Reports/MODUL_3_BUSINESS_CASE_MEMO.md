# Business Case Memo | Investigasi Fill Rate (Data Simulasi)

**Status:** Contoh laporan analitis portofolio, seluruhnya menggunakan data sintetis.  
**Periode:** 1 April–30 September 2026.  
**Unit analisis:** unit order, SKU×gudang, satu baris PO, dan satu baris shipment per order, sesuai metrik masing-masing.

## Masalah bisnis

Unit fill rate enam bulan adalah **74,15%**, sedangkan OTIF order-level adalah **42,90%**. Pada Agustus 2026, permintaan mencapai **21.626 unit** dengan fill rate **67,28%**, lebih rendah daripada Juni (79,39%). Warehouse Surabaya memiliki fill rate Agustus **65,60%**.

## Temuan yang dapat diverifikasi

- Kombinasi **Warehouse Surabaya × SKU0039** mencatat **827 unit order tidak terpenuhi** selama enam bulan, dengan nilai pesanan indikatif **Rp44.658.000**; stok akhir nol terjadi pada **87/183 hari**.
- Pada Agustus 2026, SKU tersebut mencatat **479 unit dipesan** dan **190 dipenuhi**. Di tanggal 11 Agustus, 58 unit tidak terpenuhi dan stok akhir nol.
- Supplier utama SKU0039 di dalam dataset adalah **PT Surya Ritelindo (Simulasi)**. Dari 10 PO yang sudah diterima untuk kombinasi tersebut, **1 tepat waktu**. PO yang dijanjikan tiba 11 Agustus tercatat diterima 13 Agustus.
- Nilai freight cost perlu dihitung pada tingkat order, bukan setelah join langsung dengan order line. Join salah menghasilkan Rp301.445.000, dibanding nilai benar Rp159.946.000.

## Hipotesis, bukan klaim sebab-akibat

1. Ketidakselarasan demand dan replenishment meningkatkan risiko stok tidak mencukupi pada SKU berpermintaan tinggi.
2. Penerimaan dari supplier yang meleset dari tanggal janji mungkin memperpanjang periode kekosongan persediaan.
3. Keterlambatan last-mile juga berkontribusi pada KPI OTIF, namun harus diuji terpisah dari masalah kelengkapan order.

## Rekomendasi yang dapat diuji

- Jalankan **pilot 4 minggu** untuk SKU0039 Surabaya: exception list PO tertunda, pemantauan replenishment, dan evaluasi persediaan pengaman.
- Ukur unit fill rate, hari dengan stok nol, proporsi PO tepat waktu, modal persediaan rata-rata, dan OTIF sebelum dan setelah pilot dengan pembanding yang sebanding.
- Validasi data inbound, stok intrahari, kalender promosi, batas lead time, kapasitas gudang dan karakteristik rute sebelum mengubah kebijakan secara permanen.

**Batasan penting:** Tidak ada intervensi yang benar-benar diterapkan dalam dataset ini. Nilai pesanan tidak terpenuhi bukan pendapatan yang pasti hilang. Tidak ada klaim penghematan atau dampak operasional aktual.

## Tiga hal yang harus bisa dijelaskan ketika interview

1. *Why this KPI?* Mengapa unit fill rate dan OTIF diukur pada grain berbeda.
2. *Why this SKU?* Memilih SKU berdasarkan nilai unit order tidak terpenuhi, bukan sekadar banyaknya order.
3. *What's next?* Menguji supplier-delay, stok, dan carrier performance melalui data tambahan dan pilot terukur, bukan menarik kesimpulan kausal prematur.
