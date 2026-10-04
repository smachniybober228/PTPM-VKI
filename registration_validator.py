import hashlib
import logging
import re
import sys
from typing import Tuple

LOGGER_NAME = "user_registration"
LOG_FILE = "registration.log"
PEPPER = "registration-log-pepper-v1"

BLACKLIST = {
    "admin", "root", "user", "test", "guest",
    "qwerty", "support", "manager", "superuser", "login"
}

PHONE_RE = re.compile(r"^\+[0-9]-[0-9]{3}-[0-9]{3}-[0-9]{4}$")
EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
LOGIN_STRING_RE = re.compile(r"^[A-Za-z0-9_]{5,}$")

SPECIAL_CHARS = "!@#$%^&*()_+-=[]{};'\":\\|,.<>/?`~"
SPECIAL_RE = re.compile(f"[{re.escape(SPECIAL_CHARS)}]")
ALLOWED_PASSWORD_RE = re.compile(f"^[А-Яа-яЁё0-9{re.escape(SPECIAL_CHARS)}]+$")
CYRILLIC_UPPER_RE = re.compile(r"[А-ЯЁ]")
CYRILLIC_LOWER_RE = re.compile(r"[а-яё]")
DIGIT_RE = re.compile(r"[0-9]")


def setup_logging() -> logging.Logger:
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    if logger.handlers:
        logger.handlers.clear()

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    file_handler = logging.FileHandler(LOG_FILE, mode="a", encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger


def mask_secret(value: str) -> str:
    """
    Детерминированное маскирование.
    Одинаковые значения -> одинаковая маска.
    Разные значения -> разные маски.
    """
    if value is None:
        value = ""
    digest = hashlib.sha256((PEPPER + value).encode("utf-8")).hexdigest()
    return f"<masked:{digest[:12]}>"


def validate_login(login: str) -> Tuple[bool, str]:
    if not login:
        return False, "Логин не может быть пустым"

    if login.lower() in BLACKLIST:
        return False, "Логин находится в черном списке"

    if login.startswith("+"):
        if not PHONE_RE.fullmatch(login):
            return False, "Неверный формат телефона. Ожидается +x-xxx-xxx-xxxx"
        return True, ""

    if "@" in login:
        if not EMAIL_RE.fullmatch(login):
            return False, "Неверный формат email"
        return True, ""

    if len(login) < 5:
        return False, "Логин-строка должен содержать минимум 5 символов"

    if not LOGIN_STRING_RE.fullmatch(login):
        return False, "Логин-строка может содержать только латиницу, цифры и знак подчеркивания"

    return True, ""


def validate_password(password: str, confirm: str) -> Tuple[bool, str]:
    if not password:
        return False, "Пароль не может быть пустым"

    if len(password) < 7:
        return False, "Пароль должен содержать минимум 7 символов"

    if not ALLOWED_PASSWORD_RE.fullmatch(password):
        return False, "Пароль может содержать только кириллицу, цифры и спецсимволы"

    if not CYRILLIC_UPPER_RE.search(password):
        return False, "Пароль должен содержать минимум одну заглавную кириллическую букву"

    if not CYRILLIC_LOWER_RE.search(password):
        return False, "Пароль должен содержать минимум одну строчную кириллическую букву"

    if not DIGIT_RE.search(password):
        return False, "Пароль должен содержать минимум одну цифру"

    if not SPECIAL_RE.search(password):
        return False, "Пароль должен содержать минимум один спецсимвол"

    if not confirm:
        return False, "Подтверждение пароля не может быть пустым"

    if password != confirm:
        return False, "Пароль и подтверждение пароля не совпадают"

    return True, ""


def validate_registration(login: str, password: str, confirm: str) -> Tuple[bool, str]:
    ok, message = validate_login(login)
    if not ok:
        return False, message

    return validate_password(password, confirm)


def process_registration(login: str, password: str, confirm: str) -> Tuple[bool, str]:
    logger = logging.getLogger(LOGGER_NAME)

    logger.info(
        "Запрос регистрации. login=%r password=%s confirm=%s",
        login,
        mask_secret(password),
        mask_secret(confirm)
    )

    try:
        ok, message = validate_registration(login, password, confirm)

        if ok:
            logger.info(
                "Успешная регистрация. login=%r result=True message=''",
                login
            )
            return True, ""

        logger.warning(
            "Неуспешная регистрация. login=%r result=False error=%r",
            login,
            message
        )
        return False, message

    except Exception as exc:
        logger.exception(
            "Сбой при обработке регистрации. login=%r error=%s",
            login,
            exc
        )
        return False, "Внутренняя ошибка при проверке данных"


def main() -> None:
    setup_logging()

    login = sys.stdin.readline().rstrip("\r\n")
    password = sys.stdin.readline().rstrip("\r\n")
    confirm = sys.stdin.readline().rstrip("\r\n")

    ok, message = process_registration(login, password, confirm)

    print("True" if ok else "False")
    print(message)


if __name__ == "__main__":
    main()