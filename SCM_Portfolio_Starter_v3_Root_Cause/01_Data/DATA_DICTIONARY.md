# Data Dictionary | Synthetic FMCG Supply Chain

**PENTING:** 9 file CSV ini dibuat dengan generator pseudorandom menggunakan seed `2026`. Semua nama supplier/pelanggan dan seluruh transaksi fiktif. Bukan data produksi atau benchmarking industri.

## dim_products.csv
- `product_id`: primary key ID numerik.
- `sku`: kode produk unik; `product_name`: nama produk fiktif.
- `category`: Food, Personal Care, Home Care, Beverage.
- `supplier_id`: pemasok utama produk, referensi `dim_suppliers`.
- `unit_cost`: biaya standar per unit dalam rupiah; `unit_price`: harga jual per unit dalam rupiah.
- `demand_segment`: Fast, Medium, Slow, dibuat sebagai parameter simulasi, bukan hasil perhitungan klasifikasi ABC.

## dim_suppliers.csv
- `supplier_id`: primary key; `supplier_name`: nama fiktif; `province`: provinsi lokasi simulasi.
- `promised_lead_days`: target lead time dasar supplier (hari kalender).
- `reliability_segment`: tinggi, sedang, rendah; parameter simulasi, jangan diperlakukan sebagai hasil evaluasi independen.

## dim_warehouses.csv
- `warehouse_id`, `warehouse_name`, `city`, `province`: tiga lokasi gudang simulasi.

## dim_customers.csv
- `customer_id`, `customer_name`, `customer_segment`, `city`: identitas pelanggan fiktif.

## dim_calendar.csv
- `date`, `year`, `month`, `month_name`, `year_month`, `quarter`, `weekday_name`: kalender harian 183 hari.

## fact_sales_order_lines.csv
- Grain: satu item SKU pada satu `order_id`.
- `sales_line_id`: primary key; `order_id`: kode sales order, bisa muncul pada beberapa baris SKU.
- `order_date`, `customer_id`, `warehouse_id`, `product_id`: kunci dimensi.
- `ordered_qty`: jumlah unit dipesan; `fulfilled_qty`: unit berhasil dialokasikan dan diterbitkan pada tanggal order.
- `unit_price`: harga jual per unit; `revenue`: fulfilled_qty × unit_price (rupiah).
- `cogs`: fulfilled_qty × biaya standar SKU (rupiah).
- `line_status`: fulfilled, partial, unfulfilled.
- Simulasi **tidak mengimplementasikan** backorder/return; kekurangan pada order langsung tidak dipenuhi.

## fact_shipments.csv
- Grain: satu sales order; satu `order_id` unik.
- `shipment_id`: primary key; `order_date`,`customer_id`,`warehouse_id`: kunci.
- `carrier_name`: nama provider simulasi; `promised_date`: tanggal janji customer.
- `shipped_date`: sama dengan tanggal order saat unit tersedia; kosong bila tidak ada unit dipenuhi.
- `delivered_date`: tanggal tiba (dapat melewati 30 September; diasumsikan sudah tercatat pada cut-off data 15 Oktober 2026).
- `ordered_qty`: jumlah unit order dari semua baris; `shipped_qty`: jumlah fulfilled_qty seluruh baris.
- `on_time_flag`: 1 bila delivered_date <= promised_date; 0 lainnya.
- `in_full_flag`: 1 bila shipped_qty = ordered_qty; 0 lainnya.
- `otif_flag`: 1 bila `on_time_flag` DAN `in_full_flag` sama-sama 1.
- `freight_cost`: biaya pengiriman order dalam rupiah, 0 bila tidak ada unit dikirim.

## fact_purchase_order_lines.csv
- Grain: satu line PO / satu SKU per PO dalam simulasi.
- `po_line_id`,`po_id`: identitas PO unik; `order_date`,`supplier_id`,`warehouse_id`,`product_id`: kunci.
- `ordered_qty`: jumlah unit dipesan; `received_qty`: unit yang diterima dalam periode.
- `unit_cost`: harga beli unit pada PO, dapat berbeda dari standar biaya SKU.
- `expected_date`: tanggal janji penerimaan; `actual_receipt_date`: tanggal penerimaan aktual, kosong untuk PO masih open.
- `status`: open, received_full, received_partial. Partial receipt dianggap selesai sebagian, sisanya dibatalkan untuk menyederhanakan simulasi.

## fact_inventory_daily.csv
- Grain: satu `snapshot_date` × satu `warehouse_id` × satu `product_id`.
- `inventory_id`: primary key.
- `opening_qty`: unit stok awal hari.
- `received_qty`: unit masuk dari PO yang diterima pada hari terkait.
- `shipped_qty`: unit keluar yang dialokasikan kepada sales order pada hari terkait (disederhanakan sebagai issue stock saat order).
- `closing_qty`: opening_qty + received_qty − shipped_qty, tidak boleh negatif.
- `inventory_value`: closing_qty × unit_cost standar dim_products, dalam rupiah.
- `stockout_flag`: 1 bila closing_qty = 0, 0 selainnya.

## Catatan model dan kualitas data

1. Biaya standard `dim_products.unit_cost` dipakai untuk COGS dan nilai persediaan; harga beli PO dapat sedikit bervariasi. Ini bukan model akuntansi FIFO/weighted average.
2. Simulasi tidak memodelkan retur, shrinkage, pemesanan multi-supplier, multi-shipment, atau alokasi ulang backorder.
3. Nilai stok snapshot harian **tidak boleh langsung dijumlahkan lintas semua tanggal** untuk memperoleh stok terkini.
4. `order_id` yang sama dapat berulang di `fact_sales_order_lines`; jika tabel ini JOIN langsung ke `fact_shipments` tanpa agregasi, ongkir bisa **terduplikasi**.
5. Gunakan `python 04_Python/test_project.py` untuk menguji integritas utama.
