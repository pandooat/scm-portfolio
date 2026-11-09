"""Unit tests written first for forecast/reorder point math."""
import math
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from replenishment_scenarios import reorder_point, wape

class ForecastMathTests(unittest.TestCase):
    def test_zero_uncertainty_means_no_safety_stock(self):
        reorder, safety=reorder_point(demand_mean=10,demand_sd=0,lead_mean=5,lead_sd=0,z=1.645)
        self.assertEqual(reorder,50)
        self.assertEqual(safety,0)

    def test_demand_uncertainty_and_constant_lead(self):
        reorder, safety=reorder_point(demand_mean=10,demand_sd=2,lead_mean=4,lead_sd=0,z=1.645)
        self.assertEqual(reorder,47)  # 40 + 6.58, ceiling
        self.assertEqual(safety,7)

    def test_safety_stock_non_decreasing_in_service_level(self):
        low=reorder_point(10,2,4,1,1.282)[0]
        high=reorder_point(10,2,4,1,1.645)[0]
        self.assertGreaterEqual(high,low)

    def test_wape_handles_all_zero_demand(self):
        self.assertIsNone(wape(0,0))
        self.assertAlmostEqual(wape(30,100),0.3)

if __name__=='__main__':unittest.main(verbosity=2)
