import os
import unittest

from src.registration_validator import RegistrationValidator


class _ValidatorTestBase(unittest.TestCase):
    """Общая настройка: свежий валидатор, лог в /dev/null (без файлов)."""

    def setUp(self):
        self.v = RegistrationValidator(log_file=os.devnull)


class TestValidateLogin(_ValidatorTestBase):
    def test_valid_phone_login_accepted(self):
        ok, msg = self.v._validate_login("+7-999-123-4567")
        self.assertTrue(ok)
        self.assertEqual(msg, "")

    def test_phone_with_space_separator_rejected(self):
        ok, _ = self.v._validate_login("+7 999 123 4567")
        self.assertFalse(ok)

    def test_phone_with_too_few_digits_rejected(self):
        ok, _ = self.v._validate_login("+7-99-123-4567")
        self.assertFalse(ok)

    def test_valid_email_login_accepted(self):
        ok, msg = self.v._validate_login("user@example.com")
        self.assertTrue(ok)
        self.assertEqual(msg, "")

    def test_email_without_tld_rejected(self):
        ok, _ = self.v._validate_login("user@example")
        self.assertFalse(ok)

    def test_valid_string_login_accepted(self):
        ok, _ = self.v._validate_login("user_123")
        self.assertTrue(ok)

    def test_empty_login_rejected(self):
        ok, msg = self.v._validate_login("")
        self.assertFalse(ok)
        self.assertIn("пуст", msg.lower())

    def test_blacklisted_login_rejected(self):
        ok, msg = self.v._validate_login("admin")
        self.assertFalse(ok)
        self.assertIn("черн", msg.lower())

    def test_blacklisted_login_is_case_insensitive(self):
        self.assertFalse(self.v._validate_login("ADMIN")[0])
        self.assertFalse(self.v._validate_login("AdMiN")[0])

    def test_string_login_too_short_rejected(self):
        ok, _ = self.v._validate_login("usr")
        self.assertFalse(ok)

    def test_string_login_with_cyrillic_rejected(self):
        ok, _ = self.v._validate_login("пользователь")
        self.assertFalse(ok)

    def test_string_login_with_dash_rejected(self):
        ok, _ = self.v._validate_login("user-name")
        self.assertFalse(ok)

    def test_string_login_exactly_five_chars_accepted(self):
        ok, _ = self.v._validate_login("user1")
        self.assertTrue(ok)


class TestValidatePassword(_ValidatorTestBase):
    def test_valid_password_accepted(self):
        ok, msg = self.v._validate_password("Пароль1!", "Пароль1!")
        self.assertTrue(ok)
        self.assertEqual(msg, "")

    def test_password_too_short_rejected(self):
        ok, _ = self.v._validate_password("Пар1!", "Пар1!")
        self.assertFalse(ok)

    def test_password_without_uppercase_rejected(self):
        ok, msg = self.v._validate_password("пароль1!", "пароль1!")
        self.assertFalse(ok)
        self.assertIn("заглавн", msg.lower())

    def test_password_without_lowercase_rejected(self):
        ok, msg = self.v._validate_password("ПАРОЛЬ1!", "ПАРОЛЬ1!")
        self.assertFalse(ok)
        self.assertIn("строчн", msg.lower())

    def test_password_without_digit_rejected(self):
        ok, _ = self.v._validate_password("Пароль!", "Пароль!")
        self.assertFalse(ok)

    def test_password_without_special_rejected(self):
        ok, _ = self.v._validate_password("Пароль1", "Пароль1")
        self.assertFalse(ok)

    def test_password_with_latin_chars_rejected(self):
        ok, _ = self.v._validate_password("Password1!", "Password1!")
        self.assertFalse(ok)

    def test_password_with_space_rejected(self):
        ok, _ = self.v._validate_password("Пароль 1!", "Пароль 1!")
        self.assertFalse(ok)

    def test_passwords_do_not_match_rejected(self):
        ok, msg = self.v._validate_password("Пароль1!", "Пароль2!")
        self.assertFalse(ok)
        self.assertIn("совпад", msg.lower())

    def test_empty_confirmation_rejected(self):
        ok, _ = self.v._validate_password("Пароль1!", "")
        self.assertFalse(ok)


class TestValidateRegistration(_ValidatorTestBase):
    def test_fully_valid_registration(self):
        ok, msg = self.v._validate_registration("user_123", "Пароль1!", "Пароль1!")
        self.assertTrue(ok)
        self.assertEqual(msg, "")

    def test_invalid_login_short_circuits_password_check(self):
        ok, msg = self.v._validate_registration("admin", "Пароль1!", "Пароль1!")
        self.assertFalse(ok)
        self.assertIn("черн", msg.lower())

    def test_invalid_password_reported(self):
        ok, msg = self.v._validate_registration("user_123", "short", "short")
        self.assertFalse(ok)
        self.assertIn("7", msg)


class TestMaskSecret(_ValidatorTestBase):
    def test_same_passwords_produce_same_mask(self):
        self.assertEqual(
            self.v._mask_secret("Пароль1!"),
            self.v._mask_secret("Пароль1!"),
        )

    def test_different_passwords_produce_different_masks(self):
        self.assertNotEqual(
            self.v._mask_secret("Пароль1!"),
            self.v._mask_secret("Пароль2!"),
        )

    def test_mask_does_not_leak_original_value(self):
        self.assertNotIn("Пароль1!", self.v._mask_secret("Пароль1!"))


if __name__ == "__main__":
    unittest.main()