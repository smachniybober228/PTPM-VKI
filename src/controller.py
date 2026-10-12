from user_interface import UserInterface
from registration_storage import RegistrationStorage
from registration_validator import RegistrationValidator

class Controller:
    def __init__(self):
        self.user_interface = UserInterface()
        self.registraion_storage = RegistrationStorage()
        self.registraion_validator = RegistrationValidator()

        login, password, confirm = self.user_interface.registration_input()
        result = self.registraion_storage.select_registration(login, password, confirm)
        if result is None:
            # Вычисление через registration_validator
            ok, message = self.registraion_validator.process_registration(login, password, confirm)
            self.registraion_storage.insert_registration(login, password, confirm, ok, message)

        # Сторонняя зависимость
        # Должен вернуть результат выполнения
        pass


def main() -> None:
    controller = Controller()

if __name__ == "__main__":
    main()