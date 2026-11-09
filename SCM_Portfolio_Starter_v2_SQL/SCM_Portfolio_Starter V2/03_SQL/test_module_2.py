"""Verifikasi modul praktik SQL pekan 1-2 (Python standard library)."""
import re
import sqlite3
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SQL_FILE = ROOT / 'PRAKTIK_MINGGU_1_2_JAWABAN.sql'
DB_FILE = ROOT.parent / '02_Database' / 'scm_portfolio.sqlite'


def query(number: int) -> str:
    content = SQL_FILE.read_text(encoding='utf-8')
    match = re.search(rf'-- START Q{number}\n(.*?)\n-- END Q{number}', content, flags=re.S)
    if not match:
        raise AssertionError(f'Query Q{number} tidak ditemukan')
    return match.group(1).strip()


class SQLLessonTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = sqlite3.connect(DB_FILE)
        cls.db.row_factory = sqlite3.Row

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def run_query(self, number):
        return self.db.execute(query(number)).fetchall()

    def test_q1_overview(self):
        rows = self.run_query(1)
        self.assertEqual((rows[0]['total_orders'], rows[0]['otif_orders']), (4925, 2113))
        self.assertAlmostEqual(rows[0]['otif_pct'], 42.90, places=2)

    def test_q2_order_and_line_grain(self):
        r = self.run_query(2)[0]
        self.assertEqual((r['order_lines'], r['unique_orders']), (8534, 4925))

    def test_q3_warehouse_fill_rates(self):
        rows = self.run_query(3)
        data = {r['warehouse_name']: r['fill_rate_pct'] for r in rows}
        self.assertEqual(data, {'Warehouse Surabaya': 72.80, 'Warehouse Jakarta': 73.94, 'Warehouse Bandung': 75.76})

    def test_q4_order_categories(self):
        rows = self.run_query(4)
        counts = {r['category']: r['orders'] for r in rows}
        self.assertEqual(counts, {'Lengkap dan tepat waktu': 2113, 'Tidak lengkap namun tepat waktu': 1022, 'Lengkap tetapi terlambat': 848, 'Tidak lengkap dan terlambat': 942})
        self.assertEqual(sum(counts.values()), 4925)

    def test_q5_warehouse_otif(self):
        data = {r['warehouse_name']: r['otif_pct'] for r in self.run_query(5)}
        self.assertEqual(data, {'Warehouse Surabaya': 42.32, 'Warehouse Jakarta': 42.57, 'Warehouse Bandung': 43.82})

    def test_q6_carrier_otif(self):
        rows = self.run_query(6)
        self.assertEqual(rows[0]['carrier_name'], 'Mitra Trucking (Simulasi)')
        self.assertAlmostEqual(rows[0]['otif_pct'], 34.67)

    def test_q7_supplier_otd(self):
        rows = self.run_query(7)
        self.assertEqual(rows[0]['supplier_name'], 'PT Niaga Mitra (Simulasi)')
        self.assertAlmostEqual(rows[0]['supplier_otd_pct'], 2.83)

    def test_q8_zero_stock_days(self):
        rows = self.run_query(8)
        self.assertEqual(len(rows), 10)
        self.assertGreaterEqual(rows[0]['stockout_days'], rows[-1]['stockout_days'])

    def test_q9_unserved_order_value(self):
        rows = self.run_query(9)
        self.assertEqual(len(rows), 10)
        self.assertGreaterEqual(rows[0]['unserved_order_value_rp'], rows[-1]['unserved_order_value_rp'])

    def test_q10_inventory_balance_check(self):
        rows = self.run_query(10)
        self.assertEqual(rows[0]['invalid_snapshots'], 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)
