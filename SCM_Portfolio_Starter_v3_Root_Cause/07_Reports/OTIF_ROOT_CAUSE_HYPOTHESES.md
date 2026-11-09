# OTIF Decomposition: Analisis Awal (DATA SINTETIS)

Analisis pada **4.925 order** mencatat empat kelompok:

| On time? | In full? | Jumlah order | Implikasi awal |
|---|---|---:|---|
| Ya | Ya | 2.113 | Berhasil OTIF |
| Ya | Tidak | 1.022 | Tidak lengkap meskipun tiba tepat waktu |
| Tidak | Ya | 848 | Order lengkap tetapi terlambat |
| Tidak | Tidak | 942 | Dua masalah sekaligus |

Dengan demikian, **2.812 order gagal memenuhi OTIF**. Menghitung jumlah kegagalan kelengkapan dan ketepatan secara terpisah kemudian menjumlahkannya akan menghitung kelompok 'keduanya gagal' dua kali. Gunakan diagram perpotongan atau kategori eksklusif seperti tabel ini.

## SQL verifikasi

```sql
SELECT on_time_flag, in_full_flag, COUNT(*) AS orders
FROM fact_shipments
GROUP BY on_time_flag, in_full_flag
ORDER BY on_time_flag, in_full_flag;
```

## Analisis akar masalah yang harus dilanjutkan

- **Order tepat waktu tetapi tidak lengkap:** cek SKU-gudang, reorder point, frekuensi closing stock nol, dan PO supplier.
- **Order lengkap tetapi terlambat:** bandingkan lead time last-mile per carrier dan warehouse.
- **Order tidak lengkap dan terlambat:** cek apakah masalah supply dan delivery terkonsentrasi pada gudang/produk yang sama.

**Jangan membuat klaim sebab-akibat tanpa analisis pendukung.** Data saat ini memadai untuk mengidentifikasi pola dan menyusun hipotesis, tetapi tidak membuktikan bahwa keterlambatan supplier adalah satu-satunya penyebab rendahnya OTIF.

## Draft 3 prioritas kerja untuk business memo

1. **Stock availability:** identifikasi SKU-gudang dengan unfulfilled units terbesar; uji pembaruan replenishment parameter pada SKU prioritas.
2. **Supplier reliability:** buat weekly PO exception list; pantau overdue open PO dan supplier OTD dengan ukuran sampel.
3. **Delivery execution:** buat tabel carrier vs ketepatan waktu, biaya per shipped order, dan rute untuk menyaring inefisiensi pengiriman.

**Pengukuran pasca-intervensi bila diterapkan sungguhan:** bandingkan perubahan OTIF, fill rate, biaya persediaan, dan ongkir dengan baseline yang sebanding, sambil mengontrol perubahan mix SKU dan musiman.
