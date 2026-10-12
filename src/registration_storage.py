import sqlite3

class RegistrationStorage:

    def __init__(self, path="PTPM.db"):
        self.connection = sqlite3.connect(path)

        with self.connection:
            self.connection.execute('''
            CREATE TABLE IF NOT EXISTS Registrations (
                login TEXT NOT NULL,
                password TEXT NOT NULL,
                password_confirm TEXT NOT NULL,
                result BOOLEAN NOT NULL,
                error_message TEXT NOT NULL,
                PRIMARY KEY (login, password, password_confirm)
            )
            ''')

    def insert_registration(self, login, password, password_confirm, result, error_message):
        with self.connection:
            self.connection.execute('''
            INSERT INTO Registrations (login, password, password_confirm, result, error_message)
            VALUES (?, ?, ?, ?, ?)
            ''', (login, password, password_confirm, result, error_message))

    def select_registration(self, login, password, password_confirm):
        with self.connection:
            cursor = self.connection.execute('''
            SELECT * FROM Registrations
            WHERE login = ? AND password = ? AND password_confirm = ?
            ''', (login, password, password_confirm))
            return cursor.fetchone()

    def delete_registration(self, login, password, password_confirm):
        with self.connection:
            self.connection.execute('''
            DELETE FROM Registrations
            WHERE login = ? AND password = ? AND password_confirm = ?
            ''', (login, password, password_confirm))