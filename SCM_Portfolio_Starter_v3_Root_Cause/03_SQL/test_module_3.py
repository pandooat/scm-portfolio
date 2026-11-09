"""Contract tests for module 3 SQL; run: python 03_SQL/test_module_3.py.
Uses only Python standard library and the included synthetic SQLite database.
"""
from pathlib import Path
import re
import sqlite3

HERE = Path(__file__).resolve().parent
DB = HERE.parent / '02_Database' / 'scm_portfolio.sqlite'
QUERIES = HERE / 'MODUL_3_ROOT_CAUSE_QUERIES.sql'


def main():
    assert DB.exists(), f'Missing project database: {DB}'
    assert QUERIES.exists(), f'Missing SQL workbook: {QUERIES}'
    text = QUERIES.read_text(encoding='utf-8')
    blocks = {}
    for n in range(1, 10):
        matches = re.findall(r'-- START Q' + str(n) + r'\s*\n(.*?)\n-- END Q' + str(n), text, re.S)
        assert len(matches) == 1, f'Expected exactly one Q{n} block'
        blocks[n] = matches[0].strip()
        first_sql = next((line.strip().lower() for line in blocks[n].splitlines() if line.strip() and not line.strip().startswith('--')), '')
        assert first_sql.startswith(('select', 'with')), f'Q{n} must be a SELECT/CTE'

    with sqlite3.connect(DB) as db:
        db.row_factory = sqlite3.Row
        results = {n: db.execute(sql).fetchall() for n, sql in blocks.items()}

    # Invariants: query output truly corresponds to records from this dataset.
    assert len(results[1]) == 6, 'Q1 must cover the six months'
    assert results[1][0]['year_month'] == '2026-04'
    assert results[1][4]['year_month'] == '2026-08'
    assert results[1][4]['requested_units'] == 21626
    assert results[1][4]['fill_rate_pct'] == 67.28

    assert len(results[2]) == 6, 'Q2 shows both peak months across three warehouses'
    assert len(results[3]) == 10, 'Q3 ranks top 10 SKU-warehouse priorities'
    for row in results[3]:
        assert row['unfulfilled_units'] >= 0
        assert row['stockout_days'] >= 0
    assert results[3][0]['sku'] == 'SKU0039'
    assert results[3][0]['warehouse_name'] == 'Warehouse Surabaya'
    assert results[3][0]['unserved_order_value_rp'] == 44658000

    assert len(results[4]) == 31, 'Q4 must cover every August snapshot day'
    assert sum(r['unfulfilled_units'] for r in results[4]) == 289
    assert len(results[5]) == 1, 'Q5 supplier context: one supplier/SKU/warehouse combination'
    assert results[5][0]['received_pos'] == 10
    assert len(results[6]) == 11, 'Q6 should show all 11 corresponding POs'
    assert len(results[7]) >= 3, 'Q7 must show carrier-level service performance'

    # Q8 deliberately compares wrong and correct order-level freight sums.
    assert len(results[8]) == 1
    v = results[8][0]
    assert v['wrong_freight_sum'] > v['correct_freight_sum']
    assert v['correct_freight_sum'] > 0

    for n, rows in results.items():
        print(f'Q{n}: PASS ({len(rows)} rows)')
    print('PASS: 9 root cause queries verified against the local synthetic database.')


if __name__ == '__main__':
    main()
