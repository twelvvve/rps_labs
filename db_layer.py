"""Слой доступа к данным.

В данной версии используется SQLite (встроенная SQL СУБД),
что упрощает развертывание: отдельный сервер не требуется.
"""

from __future__ import annotations

import hashlib
import json
import os
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional, Tuple


@dataclass(frozen=True)
class User:
    id: int
    username: str


class SqliteStorage:
    def __init__(self, db_path: str):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)
        self._init_schema()

    @contextmanager
    def _connect(self) -> Iterable[sqlite3.Connection]:
        conn = sqlite3.connect(self.db_path)
        try:
            conn.row_factory = sqlite3.Row
            yield conn
            conn.commit()
        finally:
            conn.close()

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS arrays (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    original_json TEXT NOT NULL,
                    sorted_json TEXT,
                    length INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                );
                """
            )

    @staticmethod
    def _hash_password(password: str) -> str:
        # SHA-256 достаточно для учебной работы; в реальных системах используют соль и адаптивные хеши.
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    def register_user(self, username: str, password: str) -> Tuple[bool, str]:
        username = username.strip()
        if len(username) < 3:
            return False, "Логин должен быть не короче 3 символов"
        if len(password) < 4:
            return False, "Пароль должен быть не короче 4 символов"

        pwd_hash = self._hash_password(password)
        try:
            with self._connect() as conn:
                conn.execute(
                    "INSERT INTO users(username, password_hash, created_at) VALUES (?, ?, ?)",
                    (username, pwd_hash, datetime.now().isoformat(timespec="seconds")),
                )
            return True, "Регистрация выполнена"
        except sqlite3.IntegrityError:
            return False, "Пользователь с таким логином уже существует"
        except Exception as e:
            return False, f"Ошибка регистрации: {e}"

    def authenticate_user(self, username: str, password: str) -> Tuple[bool, Any]:
        pwd_hash = self._hash_password(password)
        try:
            with self._connect() as conn:
                row = conn.execute(
                    "SELECT id, username FROM users WHERE username=? AND password_hash=?",
                    (username.strip(), pwd_hash),
                ).fetchone()
            if row:
                return True, User(id=int(row["id"]), username=str(row["username"]))
            return False, "Неверный логин или пароль"
        except Exception as e:
            return False, f"Ошибка подключения/запроса: {e}"

    def save_arrays(
        self,
        user_id: int,
        original: List[int],
        sorted_values: Optional[List[int]],
    ) -> Tuple[bool, str]:
        try:
            with self._connect() as conn:
                conn.execute(
                    """
                    INSERT INTO arrays(user_id, original_json, sorted_json, length, created_at)
                    VALUES(?, ?, ?, ?, ?)
                    """,
                    (
                        int(user_id),
                        json.dumps(original, ensure_ascii=False),
                        json.dumps(sorted_values, ensure_ascii=False) if sorted_values is not None else None,
                        len(original),
                        datetime.now().isoformat(timespec="seconds"),
                    ),
                )
            return True, "Данные сохранены"
        except Exception as e:
            return False, f"Ошибка сохранения: {e}"

    def list_user_arrays(self, user_id: int) -> Tuple[bool, Any]:
        try:
            with self._connect() as conn:
                rows = conn.execute(
                    """
                    SELECT id, original_json, sorted_json, length, created_at
                    FROM arrays
                    WHERE user_id=?
                    ORDER BY id DESC
                    """,
                    (int(user_id),),
                ).fetchall()
            result: List[Dict[str, Any]] = []
            for r in rows:
                result.append(
                    {
                        "id": int(r["id"]),
                        "original": json.loads(r["original_json"]),
                        "sorted": json.loads(r["sorted_json"]) if r["sorted_json"] else None,
                        "length": int(r["length"]),
                        "created_at": str(r["created_at"]),
                    }
                )
            return True, result
        except Exception as e:
            return False, f"Ошибка чтения: {e}"

    # Методы для интеграционных тестов (отдельная БД)
    def insert_bulk_test_arrays(self, arrays: List[List[int]]) -> bool:
        try:
            with self._connect() as conn:
                conn.executemany(
                    "INSERT INTO arrays(user_id, original_json, sorted_json, length, created_at) VALUES(?, ?, ?, ?, ?)",
                    [
                        (
                            0,
                            json.dumps(arr, ensure_ascii=False),
                            None,
                            len(arr),
                            datetime.now().isoformat(timespec="seconds"),
                        )
                        for arr in arrays
                    ],
                )
            return True
        except Exception:
            return False

    def random_arrays(self, count: int) -> List[List[int]]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT original_json FROM arrays ORDER BY RANDOM() LIMIT ?", (int(count),)
            ).fetchall()
        return [json.loads(r[0]) for r in rows]

    def total_count(self) -> int:
        with self._connect() as conn:
            row = conn.execute("SELECT COUNT(*) AS c FROM arrays").fetchone()
        return int(row["c"]) if row else 0

    def clear_all_arrays(self) -> bool:
        try:
            with self._connect() as conn:
                conn.execute("DELETE FROM arrays")
            return True
        except Exception:
            return False
