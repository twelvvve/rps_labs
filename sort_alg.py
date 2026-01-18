"""Алгоритм сортировки из лабораторной работы 2 (QuickSort).

Вынесен в отдельный модуль, чтобы GUI и тесты использовали одну и ту же реализацию.
"""

from __future__ import annotations

from typing import List


def quick_sort(values: List[int]) -> List[int]:
    """Функциональная реализация быстрой сортировки.

    Возвращает новый список, не изменяя исходный.
    """
    if len(values) <= 1:
        return list(values)

    pivot = values[len(values) // 2]
    less: List[int] = []
    equal: List[int] = []
    greater: List[int] = []

    for x in values:
        if x < pivot:
            less.append(x)
        elif x > pivot:
            greater.append(x)
        else:
            equal.append(x)

    return quick_sort(less) + equal + quick_sort(greater)
