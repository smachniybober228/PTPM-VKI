import sqlite3
from typing import Optional

class DatabaseRepository:
    MAX_NAME: int = 256
    MAX_MESSAGE: int = 8096

    def __init__(self, path="PTPM.db") -> None:
        self.connection = sqlite3.connect(path)
        self.connection.row_factory = sqlite3.Row

        with self.connection:
            self.connection.execute(f'''
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL CHECK(length(name) <= {self.MAX_NAME}),
                message TEXT NOT NULL CHECK(length(message) <= {self.MAX_MESSAGE})
            )
            ''', (self.MAX_NAME, self.MAX_MESSAGE))

    # ---------- Валидация ----------

    def _validate_comment_id(self, comment_id: int) -> None:
        if not isinstance(comment_id, int) or isinstance(comment_id, bool): # bool - подкласс int, и может пройти первую проверку
            raise TypeError("comment_id должен быть int")

    def _validate_username(self, username: str) -> None:
        if not isinstance(username, str):
            raise TypeError("username должен быть str")
        if not (len(username) <= self.MAX_NAME):
            raise ValueError(f"username: длина должна быть до {self.MAX_NAME} символов")

    def _validate_message(self, message: str) -> None:
        if not isinstance(message, str):
            raise TypeError("message должен быть str")
        if not (len(message) <= self.MAX_MESSAGE):
            raise ValueError(f"message: длина должна быть до {self.MAX_MESSAGE} символов")

    # ---------- CRUD ----------

    def get_by_id(self, comment_id: int) -> Optional[sqlite3.Row]:
        self._validate_comment_id(comment_id)
        cursor = self.connection.execute('''
        SELECT * FROM comments
        WHERE id = ?
        ''', (comment_id,))
        return cursor.fetchone()

    def get_by_name(self, username: str) -> list[sqlite3.Row]:
        self._validate_username(username)
        cursor = self.connection.execute('''
        SELECT * FROM comments
        WHERE name = ?
        ''', (username,))
        return cursor.fetchall()

    def add(self, comment_id: int, username: str, message: str) -> bool:
        self._validate_comment_id(comment_id)
        self._validate_username(username)
        self._validate_message(message)
        
        with self.connection:
            self.connection.execute('''
            INSERT INTO comments (id, name, message)
            VALUES (?, ?, ?)
            ''', (comment_id, username, message))
        
        return True

    def update(self, comment_id: int, new_message: str) -> bool:
        self._validate_comment_id(comment_id)
        self._validate_message(new_message)

        with self.connection:
            cursor = self.connection.execute('''
            UPDATE comments
            SET message = ?
            WHERE id = ?
            ''', (new_message, comment_id))

        # True, если запись была найдена и обновлена; False, если id не существует
        return cursor.rowcount > 0

    def delete(self, comment_id: int) -> bool:
        self._validate_comment_id(comment_id)

        with self.connection:
            cursor = self.connection.execute('''
            DELETE FROM comments
            WHERE id = ?
            ''', (comment_id,))

        # True, если запись была найдена и обновлена; False, если id не существует
        return cursor.rowcount > 0