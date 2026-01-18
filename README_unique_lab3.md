# Лабораторная работа 3 (вариант с SQLite)

## Что внутри
- `lab3_app.py` - desktop-приложение на Tkinter (авторизация, ввод/генерация массива, quicksort, сохранение, история).
- `db_layer.py` - слой работы с базой данных SQLite.
- `sort_alg.py` - алгоритм QuickSort (из лабораторной 2).
- `integration_tests_lab3.py` - интеграционные тесты БД (отдельная тестовая база).

## Запуск
```bash
python lab3_app.py
```

## Запуск интеграционных тестов
```bash
python integration_tests_lab3.py
```

## База данных
Файлы создаются автоматически:
- `sorting_app.db` - основная база приложения.
- `sorting_app_test.db` - база для тестов.
