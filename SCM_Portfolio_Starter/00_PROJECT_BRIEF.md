# Project Brief | FMCG Supply Chain Performance & Inventory Optimization

## Identitas proyek

- **Tipe:** studi kasus latihan portofolio, seluruhnya data sintetis (bukan data perusahaan nyata).
- **Industri:** FMCG / distributor barang konsumen fiktif.
- **Periode simulasi:** 1 April–30 September 2026.
- **Grain utama:** sales order line, sales order / shipment, purchase order line, snapshot stok SKU-gudang-hari.
- **Organisasi simulasi:** 48 SKU, 3 gudang, 8 pemasok, 36 pelanggan, 4.925 sales order.

## Business problem

Perusahaan simulasi mengalami fulfillment dan OTIF yang rendah serta indikasi penumpukan dan kekurangan stok yang tidak merata. Tim manajemen meminta seorang analis untuk membangun laporan KPI dan mengusulkan langkah perbaikan yang terukur.

## Lima pertanyaan bisnis wajib dijawab

1. Produk dan gudang mana paling sering tidak dapat memenuhi seluruh unit pesanan?
2. Apakah masalah pemenuhan lebih dominan berasal dari stok habis, supplier terlambat, atau delivery terlambat?
3. Supplier mana paling tidak konsisten memenuhi tanggal janji PO? Apakah ukuran sampelnya memadai?
4. Apakah jumlah stok perlu dinaikkan untuk semua SKU, atau cukup untuk SKU fast moving dengan variabilitas permintaan tinggi?
5. Langkah prioritas mana yang berpotensi memperbaiki service level dengan beban stok tambahan yang masih masuk akal?

## Scope dan definisi KPI

- **Fill Rate (unit):** total fulfilled_qty / total ordered_qty pada sales order lines. Tidak menilai ketepatan tanggal.
- **OTIF (order):** jumlah order lengkap dan delivered_date <= promised_date dibagi jumlah order. Berbeda dari fill rate.
- **Supplier OTD:** jumlah PO diterima <= expected_date dibagi jumlah PO yang telah diterima; PO open dilaporkan terpisah.
- **Snapshot Stockout Share:** proporsi snapshot SKU-gudang-hari dengan closing_qty = 0; bukan proporsi permintaan gagal dipenuhi.
- **Unserved Order Value:** jumlah (ordered_qty - fulfilled_qty) * unit_price; indikator kesempatan order yang belum terpenuhi, **tidak** setara omzet hilang yang sudah terbukti.
- **Inventory Turnover:** COGS untuk periode terpilih dibagi rata-rata nilai persediaan pada periode tersebut, bukan langsung annualized.
- **Gross Profit:** revenue terpenuhi minus COGS yang terkait, **belum** mengurangkan semua operating expenses.

## Hasil analisis yang harus Anda serahkan

1. **SQL**: 12+ query yang menghasilkan KPI tepat, dengan kesimpulan 1–2 kalimat untuk tiap analisis.
2. **Power BI**: empat halaman interaktif (executive, inventory, procurement, logistics).
3. **Python**: script pengolahan data, baseline forecast berbasis waktu, dan tiga skenario reorder point dapat dijalankan ulang.
4. **Executive memo**: maksimal dua halaman, berisi diagnosis, prioritas tindakan, risiko dan pengukuran keberhasilan.
5. **GitHub README**: konteks masalah, metode, data, langkah reproduksi, hasil, batasan, screenshot, diagram data.
6. **Demo interview**: presentasi 5–7 menit dan jawab pertanyaan audit KPI.

## Kriteria kualitas

- Tidak ada duplikasi kunci utama, nilai stok negatif, atau saldo inventory yang tidak reconcile.
- KPI selalu menyebutkan satuan, grain, denominator, dan periode.
- Data tidak pernah diklaim sebagai transaksi nyata. Hasil simulasi tidak boleh diperlakukan sebagai impact bisnis aktual.
- Kesimpulan membedakan korelasi / indikasi dari hubungan sebab-akibat yang memerlukan penyelidikan lanjutan.
- Dashboard tidak menampilkan data sumber mentah sensitif karena proyek publik memakai data sintetis saja.

## Hipotesis untuk diuji (belum dianggap terbukti)

- Supplier dengan lead time lebih panjang mungkin berkaitan dengan tingkat stockout lebih tinggi untuk SKU yang dijualnya.
- SKU fast-moving mungkin lebih sering kehilangan peluang pemenuhan karena reorder point tidak mengikuti variabilitas permintaan.
- Penyedia jasa angkutan dengan on-time delivery rendah mungkin merupakan penyebab sebagian order tidak memenuhi indikator OTIF.

Setiap hipotesis perlu diuji melalui agregasi data yang relevan, pembandingan yang konsisten, dan evaluasi kemungkinan faktor lain.
