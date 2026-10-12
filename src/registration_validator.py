import hashlib
import logging
import re
from typing import Tuple

class RegistrationValidator:
    PEPPER = "registration-log-pepper-v1"

    BLACKLIST = {
        "admin", "root", "user", "test", "guest",
        "qwerty", "support", "manager", "superuser", "login",
    }

    PHONE_RE = re.compile(r"^\+[0-9]-[0-9]{3}-[0-9]{3}-[0-9]{4}$")
    EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
    LOGIN_STRING_RE = re.compile(r"^[A-Za-z0-9_]{5,}$")

    SPECIAL_CHARS = "!@#$%^&*()_+-=[]{};'\":\\|,.<>/?`~"
    SPECIAL_RE = re.compile(f"[{re.escape(SPECIAL_CHARS)}]")
    ALLOWED_PASSWORD_RE = re.compile(
        f"^[А-Яа-яЁё0-9{re.escape(SPECIAL_CHARS)}]+$"
    )
    CYRILLIC_UPPER_RE = re.compile(r"[А-ЯЁ]")
    CYRILLIC_LOWER_RE = re.compile(r"[а-яё]")
    DIGIT_RE = re.compile(r"[0-9]")

    def __init__(self, logger_name="user_registration",
                 log_file="registration.log"):
        self.logger_name = logger_name
        self.log_file = log_file
        self.logger = self._setup_logging()

    # --- logging ------------------------------------------------------
    def _setup_logging(self) -> logging.Logger:
        logger = logging.getLogger(self.logger_name)
        logger.setLevel(logging.DEBUG)
        logger.propagate = False

        for handler in list(logger.handlers):
            logger.removeHandler(handler)
            handler.close()

        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        file_handler = logging.FileHandler(
            self.log_file, mode="a", encoding="utf-8"
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)

        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        return logger

    # --- helpers ------------------------------------------------------
    def _mask_secret(self, value: str) -> str:
        if value is None:
            value = ""
        digest = hashlib.sha256(
            (self.PEPPER + value).encode("utf-8")
        ).hexdigest()
        return f"<masked:{digest[:12]}>"

    def _validate_login(self, login: str) -> Tuple[bool, str]:
        if not login:
            return False, "Логин не может быть пустым"

        if login.lower() in self.BLACKLIST:
            return False, "Логин находится в черном списке"

        if login.startswith("+"):
            if not self.PHONE_RE.fullmatch(login):
                return False, "Неверный формат телефона. Ожидается +x-xxx-xxx-xxxx"
            return True, ""

        if "@" in login:
            if not self.EMAIL_RE.fullmatch(login):
                return False, "Неверный формат email"
            return True, ""

        if len(login) < 5:
            return False, "Логин-строка должен содержать минимум 5 символов"

        if not self.LOGIN_STRING_RE.fullmatch(login):
            return False, "Логин-строка может содержать только латиницу, цифры и знак подчеркивания"

        return True, ""

    def _validate_password(self, password: str, confirm: str) -> Tuple[bool, str]:
        if not password:
            return False, "Пароль не может быть пустым"

        if len(password) < 7:
            return False, "Пароль должен содержать минимум 7 символов"

        if not self.ALLOWED_PASSWORD_RE.fullmatch(password):
            return False, "Пароль может содержать только кириллицу, цифры и спецсимволы"

        if not self.CYRILLIC_UPPER_RE.search(password):
            return False, "Пароль должен содержать минимум одну заглавную кириллическую букву"

        if not self.CYRILLIC_LOWER_RE.search(password):
            return False, "Пароль должен содержать минимум одну строчную кириллическую букву"

        if not self.DIGIT_RE.search(password):
            return False, "Пароль должен содержать минимум одну цифру"

        if not self.SPECIAL_RE.search(password):
            return False, "Пароль должен содержать минимум один спецсимвол"

        if not confirm:
            return False, "Подтверждение пароля не может быть пустым"

        if password != confirm:
            return False, "Пароль и подтверждение пароля не совпадают"

        return True, ""

    def _validate_registration(self, login, password, confirm) -> Tuple[bool, str]:
        ok, message = self._validate_login(login)
        if not ok:
            return False, message
        return self._validate_password(password, confirm)

    # --- public API ---------------------------------------------------
    def process_registration(self, login: str, password: str,
                             confirm: str) -> Tuple[bool, str]:
        self.logger.info(
            "Запрос регистрации. login=%r password=%s confirm=%s",
            login,
            self._mask_secret(password),
            self._mask_secret(confirm),
        )

        try:
            ok, message = self._validate_registration(login, password, confirm)

            if ok:
                self.logger.info(
                    "Успешная регистрация. login=%r result=True message=''",
                    login,
                )
                return True, ""

            self.logger.warning(
                "Неуспешная регистрация. login=%r result=False error=%r",
                login, message,
            )
            return False, message

        except Exception as exc:
            self.logger.exception(
                "Сбой при обработке регистрации. login=%r error=%s",
                login, exc,
            )
            return False, "Внутренняя ошибка при проверке данных"


def main() -> None:
    validator = RegistrationValidator()

    login = input()
    password = input()
    confirm = input()

    ok, message = validator.process_registration(login, password, confirm)

    print("True" if ok else "False")
    print(message)


if __name__ == "__main__":
    main()