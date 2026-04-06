import hashlib
import json
import sqlite3
import os


class DatabaseManager:
    def __init__(self):
        # SQLite использует файл базы данных
        self.db_file = 'sorting_app.db'  # файл базы данных
        self.create_tables()

    def get_connection(self):
        """Получение соединения с базой данных"""
        try:
            connection = sqlite3.connect(self.db_file)
            # Включаем поддержку внешних ключей
            connection.execute("PRAGMA foreign_keys = ON")
            # Возвращаем строки как словари
            connection.row_factory = sqlite3.Row
            return connection
        except Exception as e:
            print(f"Ошибка подключения к SQLite: {e}")
            return None

    def create_tables(self):
        """Создание таблиц, если они не существуют"""
        connection = self.get_connection()
        if connection is None:
            print("Не удалось создать таблицы")
            return

        try:
            cursor = connection.cursor()

            # Создание таблицы users
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Создание таблицы arrays
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS arrays (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    original_array TEXT NOT NULL,
                    sorted_array TEXT,
                    array_size INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)

            connection.commit()
            print("Таблицы успешно созданы")

        except Exception as e:
            print(f"Ошибка создания таблиц: {e}")
        finally:
            cursor.close()
            connection.close()

    # регистрация пользователя
    def register_user(self, username, password):
        connection = self.get_connection()
        if connection is None:
            return False, "Ошибка подключения к базе данных"

        try:
            cursor = connection.cursor()
            # хеширование пароля
            hashed_password = hashlib.sha256(password.encode()).hexdigest()

            cursor.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, hashed_password)
            )
            connection.commit()
            return True, "Пользователь успешно зарегистрирован"

        except sqlite3.IntegrityError:
            return False, "Пользователь с таким именем уже существует"
        except Exception as e:
            return False, f"Ошибка регистрации: {str(e)}"
        finally:
            cursor.close()
            connection.close()

    # вход пользователя
    def authenticate_user(self, username, password):
        connection = self.get_connection()
        if connection is None:
            return False, "Ошибка подключения к базе данных"

        try:
            cursor = connection.cursor()
            hashed_password = hashlib.sha256(password.encode()).hexdigest()

            cursor.execute(
                "SELECT id, username FROM users WHERE username = ? AND password = ?",
                (username, hashed_password)
            )
            user = cursor.fetchone()

            if user:
                return True, {"id": user[0], "username": user[1]}
            else:
                return False, "Неверное имя пользователя или пароль"

        except Exception as e:
            return False, f"Ошибка аутентификации: {str(e)}"
        finally:
            cursor.close()
            connection.close()

    # сохранение массива в бд
    def save_array(self, user_id, original_array, sorted_array):
        connection = self.get_connection()
        if connection is None:
            return False, "Ошибка подключения к базе данных"

        try:
            cursor = connection.cursor()
            # преобразуем массивы в JSON строки
            original_json = json.dumps(original_array)
            sorted_json = json.dumps(sorted_array) if sorted_array else None
            array_size = len(original_array)

            cursor.execute(
                """INSERT INTO arrays (user_id, original_array, sorted_array, array_size) 
                VALUES (?, ?, ?, ?)""",
                (user_id, original_json, sorted_json, array_size)
            )
            connection.commit()
            return True, "Массив успешно сохранен"

        except Exception as e:
            return False, f"Ошибка сохранения: {str(e)}"
        finally:
            cursor.close()
            connection.close()

    # считывание массивов
    def get_user_arrays(self, user_id):
        connection = self.get_connection()
        if connection is None:
            return False, "Ошибка подключения к базе данных"

        try:
            cursor = connection.cursor()
            cursor.execute(
                "SELECT id, original_array, sorted_array, created_at FROM arrays WHERE user_id = ?",
                (user_id,)
            )
            rows = cursor.fetchall()

            # преобразуем в список словарей
            arrays = []
            for row in rows:
                arrays.append({
                    'id': row[0],
                    'original_array': json.loads(row[1]),
                    'sorted_array': json.loads(row[2]) if row[2] else [],
                    'created_at': row[3]
                })

            return True, arrays

        except Exception as e:
            return False, f"Ошибка получения массивов: {str(e)}"
        finally:
            cursor.close()
            connection.close()


# создаем глобальный экземпляр менеджера БД
db_manager = DatabaseManager()