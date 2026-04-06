import time
import random
import json
import sqlite3


class DatabaseManager:
    def __init__(self):
        self.db_file = 'test.db'
        self.connection = self.get_connection()
        self.create_table()

    def get_connection(self):
        try:
            connection = sqlite3.connect(self.db_file)
            connection.row_factory = sqlite3.Row
            return connection
        except Exception as e:
            print(f"Ошибка подключения к SQLite: {e}")
            return None

    def create_table(self):
        if not self.connection:
            return
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS arrays (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    array_data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            self.connection.commit()
            cursor.close()
        except Exception as e:
            print(f"Ошибка создания таблицы: {e}")

    def insert_multiple_arrays(self, arrays):
        if not self.connection:
            return False
        try:
            cursor = self.connection.cursor()
            arrays_json = [json.dumps(arr) for arr in arrays]
            cursor.executemany(
                "INSERT INTO arrays (array_data) VALUES (?)",
                [(arr,) for arr in arrays_json]
            )
            self.connection.commit()
            cursor.close()
            return True
        except Exception as e:
            print(f"Ошибка вставки: {e}")
            return False

    def get_random_arrays(self, count):
        if not self.connection:
            return []
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT array_data FROM arrays ORDER BY RANDOM() LIMIT ?",
                (count,)
            )
            results = cursor.fetchall()
            arrays = [json.loads(row[0]) for row in results]
            cursor.close()
            return arrays
        except Exception as e:
            print(f"Ошибка получения: {e}")
            return []

    def get_total_count(self):
        if not self.connection:
            return 0
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM arrays")
            count = cursor.fetchone()[0]
            cursor.close()
            return count
        except Exception as e:
            print(f"Ошибка подсчета: {e}")
            return 0

    def clear_database(self):
        if not self.connection:
            return False
        try:
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM arrays")
            self.connection.commit()
            cursor.close()
            return True
        except Exception as e:
            print(f"Ошибка очистки: {e}")
            return False

    def close(self):
        if self.connection:
            self.connection.close()


# генерация массива
def generate_random_array(size, min_val=1, max_val=1000):
    return [random.randint(min_val, max_val) for _ in range(size)]


def generate_test_data(db, count):
    arrays = []
    for i in range(count):
        array_size = random.randint(10, 100)
        arrays.append(generate_random_array(array_size))
    success = db.insert_multiple_arrays(arrays)
    if success:
        print(f"База заполнена: {db.get_total_count()} записей")
    else:
        print("Ошибка заполнения базы данных")
    return success


def test_insert_arrays():
    print("\n1. ТЕСТ ДОБАВЛЕНИЯ МАССИВОВ")

    db = DatabaseManager()
    if not db.connection:
        return

    counts_to_test = [100, 1000, 10000]

    for count in counts_to_test:
        print(f"\n Тест добавления {count} массивов")

        # генерация тестовых данных
        arrays = []
        for i in range(count):
            array_size = random.randint(10, 100)
            arrays.append(generate_random_array(array_size))

        # тестирование вставки
        start_time = time.time()
        success = db.insert_multiple_arrays(arrays)
        end_time = time.time()

        execution_time = end_time - start_time

        # проверка результата
        if success:
            actual_count = db.get_total_count()
            status = "Успешно!" if actual_count >= count else "Неудачно"
            print(f"Статус: {status}")
            print(f"Время выполнения: {execution_time:.4f} секунд")
        else:
            print("Статус: Неудача")
            print(f"Время выполнения: {execution_time:.4f} секунд")

        # очистка перед следующим тестом
        db.clear_database()

    db.close()


def test_select_and_sort():
    print("\n2. ТЕСТ ВЫГРУЗКИ И СОРТИРОВКИ")

    db = DatabaseManager()
    if not db.connection:
        return

    record_counts = [100, 1000, 10000]
    select_count = 100

    for record_count in record_counts:
        print(f"\nТест для базы с {record_count} записями")

        # подготовка тестовых данных
        if not generate_test_data(db, record_count):
            continue

        total_start_time = time.time()

        arrays = db.get_random_arrays(select_count)

        if not arrays:
            print("Ошибка: не удалось получить массивы из базы")
            db.clear_database()
            continue

        # сортировка каждого массива
        sort_times = []

        for arr in arrays:
            start_sort = time.time()
            sorted(arr)
            end_sort = time.time()
            sort_times.append(end_sort - start_sort)

        # замер общего времени окончания операции
        total_end_time = time.time()
        total_time = total_end_time - total_start_time

        print(f"Статус: Успешно!")
        print(f"Общее время работы: {total_time:.4f} секунд")
        print(f"Среднее время работы с 1 массивом: {sum(sort_times) / len(sort_times):.6f} секунд")

        db.clear_database()

    db.close()


def test_cleanup_database():
    print("\n3. ТЕСТ ОЧИСТКИ БАЗЫ ДАННЫХ")

    db = DatabaseManager()
    if not db.connection:
        return

    record_counts = [100, 1000, 10000]

    for count in record_counts:
        print(f"\nТест очистки для базы с {count} записями")

        if not generate_test_data(db, count):
            continue

        start_time = time.time()
        success = db.clear_database()
        end_time = time.time()

        execution_time = end_time - start_time
        final_count = db.get_total_count()

        if success and final_count == 0:
            status = "Успешно!"
        else:
            status = "Неудачно"

        print(f"Статус: {status}")
        print(f"Время выполнения: {execution_time:.4f} секунд")

    db.close()


def run_all_tests():
    print("ЗАПУСК ИНТЕГРАЦИОННЫХ ТЕСТОВ")
    print("=" * 50)

    test_insert_arrays()
    test_select_and_sort()
    test_cleanup_database()

    print("\n" + "=" * 50)
    print("ВСЕ ТЕСТЫ ЗАВЕРШЕНЫ")


if __name__ == "__main__":
    run_all_tests()