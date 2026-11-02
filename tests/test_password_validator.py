import unittest

from src.password_validator import validate_password


class TestPasswordValidator(unittest.TestCase):
    def test_valid_latin_password(self):
        self.assertTrue(validate_password("SecurePass1!"))

    def test_valid_cyrillic_password(self):
        self.assertTrue(validate_password("ПарольТест9#"))

    def test_length_7_is_invalid(self):
        self.assertFalse(validate_password("Aa1!aaa"))

    def test_boundary_length_8_is_valid(self):
        self.assertTrue(validate_password("Aa1!aaaa"))

    def test_boundary_length_20_is_valid(self):
        self.assertTrue(validate_password("Aa1!" + "a" * 16))

    def test_length_21_is_invalid(self):
        self.assertFalse(validate_password("Aa1!" + "a" * 17))

    def test_missing_uppercase(self):
        self.assertFalse(validate_password("securepass1!"))

    def test_missing_lowercase(self):
        self.assertFalse(validate_password("SECUREPASS1!"))

    def test_missing_digit(self):
        self.assertFalse(validate_password("SecurePassword!"))

    def test_missing_special_character(self):
        self.assertFalse(validate_password("SecurePassword1"))

    def test_underscore_is_not_special_character(self):
        self.assertFalse(validate_password("SecurePass1_"))

    def test_question_mark_is_not_special_character(self):
        self.assertFalse(validate_password("SecurePass1?"))

    def test_empty_password_is_invalid(self):
        self.assertFalse(validate_password(""))

    def test_space_inside_raises_value_error(self):
        with self.assertRaises(ValueError):
            validate_password("Pass 1234!")

    def test_space_at_start_raises_value_error(self):
        with self.assertRaises(ValueError):
            validate_password(" Pass1234!")

    def test_space_at_end_raises_value_error(self):
        with self.assertRaises(ValueError):
            validate_password("Pass1234! ")

    def test_none_raises_type_error(self):
        with self.assertRaises(TypeError):
            validate_password(None)

    def test_int_raises_type_error(self):
        with self.assertRaises(TypeError):
            validate_password(12345678)

    def test_list_raises_type_error(self):
        with self.assertRaises(TypeError):
            validate_password(["P", "a", "s", "s", "1", "!"])


if __name__ == "__main__":
    unittest.main()