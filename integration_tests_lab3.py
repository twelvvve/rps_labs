"""Интеграционные тесты работы с БД.

Важно: тесты используют ОТДЕЛЬНУЮ базу (sorting_app_test.db)
и обращаются к функциям слоя данных (db_layer.SqliteStorage).
"""

from __future__ import annotations

import random
import statistics
from time import perf_counter

from db_layer import SqliteStorage
from sort_alg import quick_sort


def gen_array() -> list[int]:
    n = random.randint(10, 120)
    return [random.randint(-1000, 1000) for _ in range(n)]


def bench_insert(db: SqliteStorage, count: int) -> tuple[bool, float]:
    payload = [gen_array() for _ in range(count)]
    t0 = perf_counter()
    ok = db.insert_bulk_test_arrays(payload)
    t1 = perf_counter()
    return ok and (db.total_count() >= count), (t1 - t0)


def bench_select_and_sort(db: SqliteStorage, take: int = 100) -> tuple[bool, float, float]:
    t0 = perf_counter()
    arrays = db.random_arrays(take)
    if len(arrays) != take:
        return False, 0.0, 0.0

    per_item = []
    for arr in arrays:
        s0 = perf_counter()
        _ = quick_sort(arr)
        s1 = perf_counter()
        per_item.append(s1 - s0)

    t1 = perf_counter()
    return True, (t1 - t0), statistics.mean(per_item)


def bench_clear(db: SqliteStorage) -> tuple[bool, float]:
    t0 = perf_counter()
    ok = db.clear_all_arrays()
    t1 = perf_counter()
    return ok and db.total_count() == 0, (t1 - t0)


def run_all() -> None:
    print("INTEGRATION TESTS: DB + SORT")
    print("DB: sorting_app_test.db\n")

    db = SqliteStorage("sorting_app_test.db")

    for n in (100, 1000, 10000):
        db.clear_all_arrays()
        ok, sec = bench_insert(db, n)
        print(f"[1] Insert {n:>5}: {'OK' if ok else 'FAIL'} | time={sec:.4f}s")

    print()

    for n in (100, 1000, 10000):
        db.clear_all_arrays()
        ok_ins, _ = bench_insert(db, n)
        if not ok_ins:
            print(f"[2] Select+Sort (base {n}): FAIL (prepare)")
            continue

        ok, total, avg = bench_select_and_sort(db, take=100)
        print(f"[2] Select+Sort (base {n:>5}): {'OK' if ok else 'FAIL'} | total={total:.4f}s | avg={avg:.6f}s")

    print()

    for n in (100, 1000, 10000):
        db.clear_all_arrays()
        ok_ins, _ = bench_insert(db, n)
        if not ok_ins:
            print(f"[3] Clear (base {n}): FAIL (prepare)")
            continue

        ok, sec = bench_clear(db)
        print(f"[3] Clear (base {n:>5}): {'OK' if ok else 'FAIL'} | time={sec:.4f}s")


if __name__ == "__main__":
    run_all()
