import unittest

from src.converter import Converter


class TestConverterFirstRange(unittest.TestCase):
    """x ∈ [100.7; +∞) → 1000"""

    def test_boundary_100_7_returns_1000(self):
        self.assertEqual(Converter.do(100.7), 1000)

    def test_above_boundary_returns_1000(self):
        self.assertEqual(Converter.do(100.8), 1000)

    def test_large_value_returns_1000(self):
        self.assertEqual(Converter.do(1000.0), 1000)

    def test_very_large_value_returns_1000(self):
        self.assertEqual(Converter.do(1_000_000.0), 1000)


class TestConverterSecondRange(unittest.TestCase):
    """x ∈ (0; 100.7) → int(x)"""

    def test_boundary_just_below_100_7(self):
        # Самое большое допустимое значение из второго диапазона
        self.assertEqual(Converter.do(100.6), 100)

    def test_small_positive_truncated(self):
        self.assertEqual(Converter.do(0.1), 0)

    def test_positive_with_fraction_truncated(self):
        self.assertEqual(Converter.do(50.9), 50)

    def test_whole_positive(self):
        self.assertEqual(Converter.do(42.0), 42)

    def test_one_point_zero(self):
        self.assertEqual(Converter.do(1.0), 1)


class TestConverterZero(unittest.TestCase):
    """x == 0.0 → ValueError"""

    def test_zero_float_raises_value_error(self):
        with self.assertRaises(ValueError):
            Converter.do(0.0)

    def test_zero_int_raises_value_error(self):
        # 0 == 0.0 в Python, поэтому тоже должен бросить
        with self.assertRaises(ValueError):
            Converter.do(0)


class TestConverterFourthRange(unittest.TestCase):
    """x ∈ [-30.4; 0) → int(x) - 5"""

    def test_boundary_minus_30_4(self):
        # int(-30.4) = -30; -30 - 5 = -35
        self.assertEqual(Converter.do(-30.4), -35)

    def test_small_negative(self):
        # int(-0.1) = 0; 0 - 5 = -5
        self.assertEqual(Converter.do(-0.1), -5)

    def test_mid_negative(self):
        # int(-15.5) = -15; -15 - 5 = -20
        self.assertEqual(Converter.do(-15.5), -20)

    def test_whole_negative(self):
        # int(-1.0) = -1; -1 - 5 = -6
        self.assertEqual(Converter.do(-1.0), -6)

    def test_just_above_boundary(self):
        # int(-30.3) = -30; -30 - 5 = -35
        self.assertEqual(Converter.do(-30.3), -35)


class TestConverterFifthRange(unittest.TestCase):
    """x ∈ (-∞; -30.5] → -2000"""

    def test_boundary_minus_30_5(self):
        self.assertEqual(Converter.do(-30.5), -2000)

    def test_just_below_boundary(self):
        self.assertEqual(Converter.do(-30.6), -2000)

    def test_large_negative(self):
        self.assertEqual(Converter.do(-1000.0), -2000)

    def test_very_large_negative(self):
        self.assertEqual(Converter.do(-1_000_000.0), -2000)


class TestConverterContract(unittest.TestCase):
    """Проверка контракта: метод статический и возвращает int"""

    def test_method_is_static(self):
        # Вызывается на классе без экземпляра
        self.assertEqual(Converter.do(50.0), 50)

    def test_returns_int_not_float(self):
        result = Converter.do(50.9)
        self.assertIsInstance(result, int)
        self.assertNotIsInstance(result, float)

    def test_returns_int_for_1000(self):
        self.assertIsInstance(Converter.do(200.0), int)

    def test_returns_int_for_minus_2000(self):
        self.assertIsInstance(Converter.do(-500.0), int)


if __name__ == "__main__":
    unittest.main()