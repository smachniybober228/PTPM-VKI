import datetime
import unittest

from src.Delivery import calculate_delivery_cost


class TestDeliveryValidation(unittest.TestCase):
    def test_zero_weight_rejected(self):
        cost, date = calculate_delivery_cost(0.0, 100, "обычный")
        self.assertEqual(cost, -1)
        self.assertEqual(date, "0000-00-00")

    def test_weight_below_minimum_rejected(self):
        self.assertEqual(calculate_delivery_cost(0.05, 100, "обычный")[0], -1)

    def test_weight_above_maximum_rejected(self):
        self.assertEqual(calculate_delivery_cost(51.0, 100, "обычный")[0], -1)

    def test_zero_distance_rejected(self):
        self.assertEqual(calculate_delivery_cost(1.0, 0, "обычный")[0], -1)

    def test_negative_distance_rejected(self):
        self.assertEqual(calculate_delivery_cost(1.0, -10, "обычный")[0], -1)

    def test_distance_above_maximum_rejected(self):
        self.assertEqual(calculate_delivery_cost(1.0, 5001, "обычный")[0], -1)

    def test_invalid_package_type_rejected(self):
        self.assertEqual(calculate_delivery_cost(1.0, 100, "загадочный")[0], -1)

    def test_empty_package_type_rejected(self):
        self.assertEqual(calculate_delivery_cost(1.0, 100, "")[0], -1)


class TestDeliveryBoundaries(unittest.TestCase):
    def test_minimum_valid_weight_accepted(self):
        self.assertGreater(calculate_delivery_cost(0.1, 100, "обычный")[0], 0)

    def test_maximum_valid_weight_accepted(self):
        self.assertGreater(calculate_delivery_cost(50.0, 100, "обычный")[0], 0)

    def test_minimum_valid_distance_accepted(self):
        self.assertGreater(calculate_delivery_cost(1.0, 1, "обычный")[0], 0)

    def test_maximum_valid_distance_accepted(self):
        self.assertGreater(calculate_delivery_cost(1.0, 5000, "обычный")[0], 0)

    def test_weight_exactly_5kg_should_trigger_medium_coefficient(self):
        cost_at_5 = calculate_delivery_cost(5.0, 100, "обычный")[0]
        cost_at_4_9 = calculate_delivery_cost(4.9, 100, "обычный")[0]
        self.assertGreater(cost_at_5, cost_at_4_9)


class TestDeliveryCost(unittest.TestCase):
    def test_base_cost_for_simple_delivery(self):
        # 200 + 100 * 5 = 700
        self.assertEqual(calculate_delivery_cost(1.0, 100, "обычный")[0], 700)

    def test_medium_weight_applies_1_2_coefficient(self):
        expected = int((200 + 100 * 5) * 1.2)
        self.assertEqual(calculate_delivery_cost(10.0, 100, "обычный")[0], expected)

    def test_heavy_weight_applies_1_5_coefficient(self):
        expected = int((200 + 100 * 5) * 1.5)
        self.assertEqual(calculate_delivery_cost(25.0, 100, "обычный")[0], expected)

    def test_fragile_adds_300_rubles(self):
        base = 200 + 100 * 5
        self.assertEqual(calculate_delivery_cost(1.0, 100, "хрупкий")[0], base + 300)

    def test_dangerous_adds_1000_rubles(self):
        base = 200 + 100 * 5
        self.assertEqual(calculate_delivery_cost(1.0, 100, "опасный")[0], base + 1000)

    def test_express_costs_more_than_regular(self):
        regular = calculate_delivery_cost(1.0, 100, "обычный", is_express=False)[0]
        express = calculate_delivery_cost(1.0, 100, "обычный", is_express=True)[0]
        self.assertGreater(express, regular)


class TestDeliveryDate(unittest.TestCase):
    SEND_DATE = datetime.date(2026, 9, 3)

    def test_delivery_date_format(self):
        _, date = calculate_delivery_cost(1.0, 100, "обычный")
        datetime.datetime.strptime(date, "%Y-%m-%d")

    def test_short_distance_is_minimum_one_day(self):
        _, date = calculate_delivery_cost(1.0, 100, "обычный")
        delivered = datetime.datetime.strptime(date, "%Y-%m-%d").date()
        self.assertEqual((delivered - self.SEND_DATE).days, 1)

    def test_long_distance_scales_by_500km(self):
        _, date = calculate_delivery_cost(1.0, 1500, "обычный")
        delivered = datetime.datetime.strptime(date, "%Y-%m-%d").date()
        self.assertEqual((delivered - self.SEND_DATE).days, 3)

    def test_express_faster_than_regular(self):
        _, reg_date = calculate_delivery_cost(1.0, 1500, "обычный", is_express=False)
        _, exp_date = calculate_delivery_cost(1.0, 1500, "обычный", is_express=True)
        reg = datetime.datetime.strptime(reg_date, "%Y-%m-%d").date()
        exp = datetime.datetime.strptime(exp_date, "%Y-%m-%d").date()
        self.assertLess(exp, reg)

    def test_express_short_distance_still_at_least_one_day(self):
        _, date = calculate_delivery_cost(1.0, 500, "обычный", is_express=True)
        delivered = datetime.datetime.strptime(date, "%Y-%m-%d").date()
        self.assertGreaterEqual((delivered - self.SEND_DATE).days, 1)


class TestDeliveryCombinations(unittest.TestCase):
    def test_heavy_fragile_delivery(self):
        self.assertEqual(calculate_delivery_cost(25.0, 1000, "хрупкий")[0], 8100)

    def test_medium_dangerous_delivery(self):
        base = 200 + 500 * 5
        expected = int(base * 1.2) + 1000
        self.assertEqual(calculate_delivery_cost(10.0, 500, "опасный")[0], expected)


if __name__ == "__main__":
    unittest.main()