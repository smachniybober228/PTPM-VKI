class UserInterface:
    def registration_input(self) -> tuple[str, str, str]:
        login = input()
        password = input()
        confirm = input()

        return (login, password, confirm)