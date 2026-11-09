import sqlite3

class DatabaseRepository:
    def __init__(self, path="PTPM.db"):
        self.connection = sqlite3.connect(path)

        self.max_name = 256
        self.max_message = 8096

        with self.connection:
            self.connection.execute('''
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL CHECK(length(name) <= ?),
                message TEXT NOT NULL CHECK(length(message) <= ?)
            )
            ''', (self.max_name, self.max_message))

    def get_by_id(self, comment_id: int):
        with self.connection:
            cursor = self.connection.execute('''
            SELECT * FROM comments
            WHERE id = ?
            ''', (comment_id))
            return cursor.fetchone()

    def get_by_name(self, username: str):
        with self.connection:
            cursor = self.connection.execute('''
            SELECT * FROM comments
            WHERE name = ?
            ''', (username))
            return cursor.fetchall()

    def add(self, comment_id: int, username: str, message: str):

        if not isinstance(comment_id, int) or isinstance(comment_id, bool): # bool - подкласс int, и может пройти первую проверку
            raise TypeError("comment_id должен быть int")
        if not isinstance(username, str):
            raise TypeError("username должен быть str")
        if not isinstance(message, str):
            raise TypeError("message должен быть str")

        if not (len(username) <= self.max_name):
            raise ValueError("username: длина должна быть до ${self.max_name} символов")
        if not (len(message) <= self.max_message):
            raise ValueError("message: длина должна быть до ${self.max_message} символов")

        with self.connection:
            self.connection.execute('''
            INSERT INTO comments (id, name, message)
            VALUES (?, ?, ?)
            ''', (comment_id, username, message))
        
        return True

    def update(self, comment_id: int, new_message: str):

        if not isinstance(comment_id, int) or isinstance(comment_id, bool): # bool - подкласс int, и может пройти первую проверку
            raise TypeError("comment_id должен быть int")
        if not isinstance(new_message, str):
            raise TypeError("message должен быть str")

        if not (len(new_message) <= self.max_message):
            raise ValueError("message: длина должна быть до ${self.max_message} символов")

        with self.connection:
            self.connection.execute('''
            UPDATE comments
            SET message = ?
            WHERE id = ?
            ''', (new_message, comment_id))

    def delete (self, comment_id: int):
        with self.connection:
            self.connection.execute('''
            DELETE FROM comments
            WHERE id = ?
            ''', (comment_id))