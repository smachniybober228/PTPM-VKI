import os
import unittest
from unittest.mock import Mock, patch

from src.controller import Controller
from src.registration_validator import RegistrationValidator
from src.registration_storage import RegistrationStorage
from src.user_interface import UserInterface
from src.sender import EmailSenderInterface, EmailSenderStub



# ---------- Вспомогательные фабрики ----------

def _make_storage() -> RegistrationStorage:
    """Свежий SQLite в памяти: настоящий SQL, но без файловых следов."""
    return RegistrationStorage(path=":memory:")


def _make_validator() -> RegistrationValidator:
    """
    Настоящий валидатор, но лог пишем в os.devnull,
    чтобы не плодить registration.log в рабочей папке.
    """
    return RegistrationValidator(log_file=os.devnull)


def _build_controller(ui, storage, validator, sender) -> Controller:
    """
    Собирает Controller с подставленными зависимостями.
    Патчим символы в модуле controller, чтобы его __init__
    не создавал настоящий PTPM.db и дефолтные объекты.
    """
    with patch("src.controller.UserInterface", return_value=ui), \
         patch("src.controller.RegistrationStorage", return_value=storage), \
         patch("src.controller.RegistrationValidator", return_value=validator), \
         patch("src.controller.EmailSenderStub", return_value=sender):
        return Controller()


# ---------- Интеграционные тесты ----------

class TestControllerIntegration(unittest.TestCase):
    """Проверяют связку Controller + Validator + Storage + Sender."""

    def test_new_registration_saves_result_to_db_and_sends_email(self):
        """Записи нет -> валидация, вставка в БД, письмо с результатом."""
        ui = Mock(spec=UserInterface)
        ui.registration_input.return_value = ("user_123", "Пароль1!", "Пароль1!")
        storage = _make_storage()
        validator = _make_validator()
        sender = Mock(spec=EmailSenderInterface)

        controller = _build_controller(ui, storage, validator, sender)
        result = controller.run()

        # 1) Контроллер вернул True
        self.assertTrue(result)

        # 2) В БД действительно появилась запись с result=True и пустой ошибкой
        row = storage.select_registration("user_123", "Пароль1!", "Пароль1!")
        self.assertIsNotNone(row)
        self.assertTrue(bool(row[3]))
        self.assertEqual(row[4], "")

        # 3) Сторонняя зависимость получила строку результата
        sender.send.assert_called_once()
        self.assertEqual(sender.send.call_args.args[2], "True")

    def test_second_run_uses_cached_result_without_revalidation(self):
        """Повторный запуск на тех же данных берёт результат из БД."""
        ui = Mock(spec=UserInterface)
        ui.registration_input.return_value = ("user_123", "Пароль1!", "Пароль1!")
        storage = _make_storage()
        # Spy: реальный вызов + подсчёт вызовов
        validator_spy = Mock(wraps=_make_validator())
        sender = Mock(spec=EmailSenderInterface)

        controller = _build_controller(ui, storage, validator_spy, sender)

        # Первый запуск: валидатор вызывается один раз
        self.assertTrue(controller.run())
        self.assertEqual(validator_spy.process_registration.call_count, 1)

        # Второй запуск: валидатор НЕ вызывается, но email уходит снова
        self.assertTrue(controller.run())
        self.assertEqual(validator_spy.process_registration.call_count, 1)
        self.assertEqual(sender.send.call_count, 2)

    def test_invalid_registration_saves_failure_to_db_and_sends_false(self):
        """Невалидные данные -> result=False в БД, письмо с 'False'."""
        ui = Mock(spec=UserInterface)
        ui.registration_input.return_value = ("ab", "short", "short")
        storage = _make_storage()
        validator = _make_validator()
        sender = Mock(spec=EmailSenderInterface)

        controller = _build_controller(ui, storage, validator, sender)
        result = controller.run()

        self.assertFalse(result)

        row = storage.select_registration("ab", "short", "short")
        self.assertIsNotNone(row)
        self.assertFalse(bool(row[3]))
        self.assertNotEqual(row[4], "")

        sender.send.assert_called_once()
        self.assertEqual(sender.send.call_args.args[2], "False")

    def test_cached_failed_result_is_returned_not_overridden(self):
        """
        Если в БД уже лежит неуспешный результат,
        контроллер возвращает его, а не подменяет на True.
        """
        storage = _make_storage()
        storage.insert_registration("ab", "short", "short", False, "старая ошибка")

        ui = Mock(spec=UserInterface)
        ui.registration_input.return_value = ("ab", "short", "short")
        validator = Mock(spec=RegistrationValidator)  # не должен вызваться
        sender = Mock(spec=EmailSenderInterface)

        controller = _build_controller(ui, storage, validator, sender)
        result = controller.run()

        self.assertFalse(result)
        validator.process_registration.assert_not_called()
        sender.send.assert_called_once()
        self.assertEqual(sender.send.call_args.args[2], "False")


# ---------- Модульные тесты ----------

class TestUserInterface(unittest.TestCase):
    """Изолированно проверяем класс ввода через мок input()."""

    @patch("builtins.input", side_effect=["login1", "pass1", "pass1"])
    def test_returns_three_values_in_order(self, mock_input):
        ui = UserInterface()
        self.assertEqual(ui.registration_input(), ("login1", "pass1", "pass1"))
        self.assertEqual(mock_input.call_count, 3)


class TestEmailSenderStub(unittest.TestCase):
    """Изолированно проверяем заглушку отправки."""

    def test_send_does_not_raise_and_returns_none(self):
        stub = EmailSenderStub()
        self.assertIsNone(stub.send("a@b.c", "subj", "body"))

    def test_interface_cannot_be_instantiated(self):
        with self.assertRaises(TypeError):
            EmailSenderInterface()


class TestRegistrationStorage(unittest.TestCase):
    """CRUD хранилища на реальном SQLite в памяти."""

    def setUp(self):
        self.storage = RegistrationStorage(path=":memory:")

    def test_insert_then_select_returns_row(self):
        self.storage.insert_registration("l1", "p1", "p1", True, "")
        row = self.storage.select_registration("l1", "p1", "p1")
        self.assertIsNotNone(row)
        self.assertEqual(row[0], "l1")
        self.assertTrue(bool(row[3]))

    def test_select_missing_returns_none(self):
        self.assertIsNone(self.storage.select_registration("x", "y", "z"))

    def test_delete_removes_row(self):
        self.storage.insert_registration("l1", "p1", "p1", True, "")
        self.storage.delete_registration("l1", "p1", "p1")
        self.assertIsNone(self.storage.select_registration("l1", "p1", "p1"))


if __name__ == "__main__":
    unittest.main()