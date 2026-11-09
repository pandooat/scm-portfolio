"""Unit/integration tests for deterministic synthetic SCM dataset.
Run from any directory: python 04_Python/test_project.py
"""
import sqlite3
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / '02_Database' / 'scm_portfolio.sqlite'


class SCMDataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not DB.exists():
            raise FileNotFoundError(f'Database not found: {DB}. Run generate_data.py first.')
        cls.con = sqlite3.connect(DB)
        cls.con.row_factory = sqlite3.Row

    @classmethod
    def tearDownClass(cls):
        cls.con.close()

    def query(self, sql):
        return self.con.execute(sql).fetchone()[0]

    def test_dimension_counts(self):
        self.assertEqual(self.query('SELECT COUNT(*) FROM dim_products'), 48)
        self.assertEqual(self.query('SELECT COUNT(*) FROM dim_warehouses'), 3)
        self.assertEqual(self.query('SELECT COUNT(*) FROM dim_suppliers'), 8)

    def test_snapshot_daily_grain(self):
        self.assertEqual(self.query('SELECT COUNT(*) FROM fact_inventory_daily'), 183 * 48 * 3)
        self.assertEqual(self.query('SELECT COUNT(*) FROM (SELECT snapshot_date, product_id, warehouse_id, COUNT(*) n FROM fact_inventory_daily GROUP BY 1,2,3 HAVING n != 1)'), 0)

    def test_inventory_reconciles(self):
        self.assertEqual(self.query('SELECT COUNT(*) FROM fact_inventory_daily WHERE opening_qty + received_qty - shipped_qty != closing_qty'), 0)
        self.assertEqual(self.query('SELECT COUNT(*) FROM fact_inventory_daily WHERE closing_qty < 0 OR received_qty < 0 OR shipped_qty < 0'), 0)
        self.assertEqual(self.query('''SELECT COUNT(*) FROM (
            SELECT snapshot_date, product_id, warehouse_id, opening_qty,
                   LAG(closing_qty) OVER (PARTITION BY product_id, warehouse_id ORDER BY snapshot_date) prev_close
            FROM fact_inventory_daily) WHERE prev_close IS NOT NULL AND opening_qty != prev_close'''), 0)

    def test_order_and_shipment_quantities_reconcile(self):
        self.assertEqual(self.query('SELECT COUNT(*) FROM fact_sales_order_lines WHERE fulfilled_qty > ordered_qty OR fulfilled_qty < 0 OR ordered_qty <= 0'), 0)
        self.assertEqual(self.query('''SELECT COUNT(*) FROM (
            SELECT s.order_id FROM fact_shipments s
            JOIN (SELECT order_id, SUM(ordered_qty) ordered, SUM(fulfilled_qty) fulfilled FROM fact_sales_order_lines GROUP BY order_id) l
            ON s.order_id=l.order_id
            WHERE s.ordered_qty!=l.ordered OR s.shipped_qty!=l.fulfilled
        )'''), 0)
        self.assertEqual(self.query('SELECT COUNT(*) FROM fact_shipments WHERE otif_flag = 1 AND (shipped_qty != ordered_qty OR delivered_date > promised_date)'), 0)
        self.assertEqual(self.query('SELECT COUNT(*) FROM fact_sales_order_lines WHERE ABS(revenue - fulfilled_qty*unit_price) > 0.01'), 0)

    def test_po_receipts_reconcile(self):
        self.assertEqual(self.query('SELECT COUNT(*) FROM fact_purchase_order_lines WHERE received_qty > ordered_qty OR received_qty < 0'), 0)
        self.assertEqual(self.query('SELECT COUNT(*) FROM fact_purchase_order_lines WHERE actual_receipt_date IS NULL AND received_qty != 0'), 0)
        self.assertEqual(self.query('''SELECT COUNT(*) FROM (
            SELECT product_id, warehouse_id, actual_receipt_date date, SUM(received_qty) qty
            FROM fact_purchase_order_lines WHERE actual_receipt_date IS NOT NULL
            GROUP BY product_id, warehouse_id, actual_receipt_date
        ) p LEFT JOIN fact_inventory_daily s ON p.product_id=s.product_id AND p.warehouse_id=s.warehouse_id AND p.date=s.snapshot_date
        WHERE s.snapshot_date IS NULL OR p.qty != s.received_qty'''), 0)

    def test_sales_inventory_reconcile(self):
        self.assertEqual(self.query('''SELECT COUNT(*) FROM (
            SELECT product_id, warehouse_id, order_date date, SUM(fulfilled_qty) qty
            FROM fact_sales_order_lines GROUP BY product_id,warehouse_id,order_date
        ) l JOIN fact_inventory_daily s ON l.product_id=s.product_id AND l.warehouse_id=s.warehouse_id AND l.date=s.snapshot_date
        WHERE l.qty != s.shipped_qty'''), 0)

    def test_foreign_keys(self):
        self.assertEqual(len(self.con.execute('PRAGMA foreign_key_check').fetchall()), 0)

    def test_useful_patterns_exist(self):
        self.assertGreater(self.query('SELECT SUM(ordered_qty-fulfilled_qty) FROM fact_sales_order_lines'), 0)
        self.assertGreater(self.query('SELECT SUM(otif_flag) FROM fact_shipments'), 0)
        self.assertGreater(self.query('SELECT COUNT(*) FROM fact_shipments WHERE otif_flag = 0'), 0)
        self.assertGreater(self.query('SELECT SUM(stockout_flag) FROM fact_inventory_daily'), 0)
        self.assertGreater(self.query('SELECT COUNT(*) FROM fact_purchase_order_lines WHERE actual_receipt_date > expected_date'), 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)
