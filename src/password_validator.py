def validate_password(password: str) -> bool:
    """
    Выполняет валидацию строки пароля на соответствие политикам безопасности.

    :param password: Проверяемый пароль
    :return: True, если пароль удовлетворяет всем условиям, иначе False
    :raises TypeError: Если входной параметр не является строкой
    :raises ValueError: Если входная строка содержит символы пробела
    """
    if not isinstance(password, str):
        raise TypeError("Пароль должен быть строкой")

    if " " in password:
        raise ValueError("Пароль не должен содержать пробелы")

    if not (8 <= len(password) <= 20):
        return False

    has_upper = any(ch.isupper() for ch in password)
    has_lower = any(ch.islower() for ch in password)
    has_digit = any(ch.isdigit() for ch in password)

    special_chars = set("!@#$%^&*")
    has_special = any(ch in special_chars for ch in password)

    return has_upper and has_lower and has_digit and has_special