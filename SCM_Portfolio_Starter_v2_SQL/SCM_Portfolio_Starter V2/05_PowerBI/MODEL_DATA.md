# Model Data Power BI: Skema Bintang Multi-Fact

## Grain (tingkat detail) tabel

| Tabel | Grain (satu baris mewakili) | Kunci unik |
|---|---|---|
| `dim_products` | Satu SKU | `product_id` |
| `dim_warehouses` | Satu gudang | `warehouse_id` |
| `dim_suppliers` | Satu supplier | `supplier_id` |
| `dim_customers` | Satu pelanggan | `customer_id` |
| `dim_calendar` | Satu tanggal | `date` |
| `fact_sales_order_lines` | Satu item dalam sales order | `sales_line_id` |
| `fact_shipments` | Satu sales order (ringkasan pengiriman) | `shipment_id` dan `order_id` |
| `fact_purchase_order_lines` | Satu item PO (satu produk per PO di simulasi) | `po_line_id` |
| `fact_inventory_daily` | Satu SKU × gudang × tanggal | `inventory_id` |

## Hubungan yang dibuat di **Model View**

Atur semua relationship **One-to-many (1:*)**, filter direction **Single**, dari tabel dimensi ke tabel fakta.

```text
Dimensi                   Fakta
-----------------------------------------------------------------
dim_products[product_id] -> fact_sales_order_lines[product_id]
                         -> fact_purchase_order_lines[product_id]
                         -> fact_inventory_daily[product_id]

dim_warehouses[warehouse_id] -> fact_sales_order_lines[warehouse_id]
                             -> fact_shipments[warehouse_id]
                             -> fact_purchase_order_lines[warehouse_id]
                             -> fact_inventory_daily[warehouse_id]

dim_suppliers[supplier_id] -> fact_purchase_order_lines[supplier_id]

dim_customers[customer_id] -> fact_sales_order_lines[customer_id]
                           -> fact_shipments[customer_id]

dim_calendar[date] -> fact_sales_order_lines[order_date]
                   -> fact_shipments[order_date]
                   -> fact_purchase_order_lines[order_date]
                   -> fact_inventory_daily[snapshot_date]
```

**Penting**: Untuk tahap pemula, **jangan** menghubungkan `dim_suppliers[supplier_id]` langsung ke `dim_products[supplier_id]`, karena ada jalur lain lewat `fact_purchase_order_lines`. Jika keduanya aktif dan cross-filter dibuka dua arah, Anda dapat membuat hubungan ambigu. Hubungkan supplier ke PO saja, dan gunakan produk untuk analisis produk.

**Jangan** menghubungkan `fact_shipments` langsung ke `fact_sales_order_lines` melalui `order_id`, terutama saat menjumlah ongkir atau menghitung OTIF. Satu order dapat memiliki beberapa order line sehingga JOIN dapat menggandakan biaya order.

## Tipe data (Power Query)

- ID numerik, kuantitas, nilai IDR: **Whole number**.
- `order_date`, `snapshot_date`, `expected_date`, `actual_receipt_date`, `promised_date`, `shipped_date`, `delivered_date`, `dim_calendar[date]`: **Date**. `actual_receipt_date` berisi nilai kosong untuk PO yang masih open.
- `year_month`: **Text** (`2026-04`), untuk sorting grafik.
- Flag (`otif_flag`,`stockout_flag` dll.): **Whole number**, bernilai 0/1.

## Validasi setelah relasi dibuat

Gunakan **Card** untuk `Total Orders`, `Fill Rate %`, `OTIF %`, `Revenue IDR`. Tanpa filter, nilai yang diharapkan (simulasi):

- `Total Orders`: 4.925
- `Fill Rate %`: 74,15%
- `OTIF %`: 42,90%
- `Revenue IDR`: Rp3.324.652.500

Jika nilainya berubah setelah Anda mengubah relasi, periksa **grain** dan potensi filter ambigu atau double counting.

Sumber konsep: Microsoft Learn, Understand star schema and importance for Power BI:
https://learn.microsoft.com/en-us/power-bi/guidance/star-schema
