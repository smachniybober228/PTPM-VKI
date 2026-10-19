from user_interface import UserInterface
from registration_storage import RegistrationStorage
from registration_validator import RegistrationValidator
from sender import EmailSenderInterface, EmailSenderStub


class Controller:
    def __init__(self):
        self.user_interface = UserInterface()
        self.registration_storage = RegistrationStorage()
        self.registration_validator = RegistrationValidator()
        self.sender: EmailSenderInterface = EmailSenderStub()

    def run(self) -> bool:
        # 1. Получаем входные данные
        login, password, confirm = self.user_interface.registration_input()

        # 2. Проверяем, есть ли запись в БД
        row = self.registration_storage.select_registration(login, password, confirm)

        if row is None:
            # Записи нет — вычисляем и сохраняем
            result, message = self.registration_validator.process_registration(
                login, password, confirm
            )
            self.registration_storage.insert_registration(
                login, password, confirm, result, message
            )
        else:
            # Запись есть — берём результат из БД
            # row = (login, password, password_apply, result, error_message)
            result = bool(row[3])
            message = row[4]

        # 3. Отправляем строку-результат сторонней зависимости
        self.sender.send(
            "user@example.com",
            "Результат регистрации",
            str(result),
        )

        # 4. Возвращаем результат операции
        return result


def main() -> None:
    controller = Controller()
    ok = controller.run()
    print("True" if ok else "False")


if __name__ == "__main__":
    main()