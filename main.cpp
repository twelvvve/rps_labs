#ifndef RUN_GTESTS
#define NOMINMAX
#include <windows.h>
#include <iostream>
#include <vector>
#include <string>
#include <limits>
#include <fstream>
#include <clocale>
#include "array.h"
#include "quicksort.h"
#include "validation.h"

static void setupConsoleRu() {
    setlocale(LC_ALL, "Russian");
    SetConsoleOutputCP(1251);
    SetConsoleCP(1251);
}

static void clearScreen() {
    HANDLE hConsole = GetStdHandle(STD_OUTPUT_HANDLE);
    CONSOLE_SCREEN_BUFFER_INFO csbi;
    DWORD count;
    DWORD cellCount;
    COORD homeCoords = { 0, 0 };

    if (hConsole == INVALID_HANDLE_VALUE) return;
    if (!GetConsoleScreenBufferInfo(hConsole, &csbi)) return;

    cellCount = csbi.dwSize.X * csbi.dwSize.Y;

    FillConsoleOutputCharacter(hConsole, (TCHAR)' ', cellCount, homeCoords, &count);
    FillConsoleOutputAttribute(hConsole, csbi.wAttributes, cellCount, homeCoords, &count);
    SetConsoleCursorPosition(hConsole, homeCoords);
}

static void pauseConsole() {
    std::cout << "\nНажмите Enter, чтобы продолжить...";
    std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
    std::cin.get();
}

static int readInt(const char* prompt) {
    while (true) {
        std::cout << prompt;
        int x;
        if (std::cin >> x) {
            std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
            return x;
        }
        std::cin.clear();
        std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
        std::cout << "Ошибка ввода. Введите целое число.\n";
    }
}

static void printVectorLine(const std::vector<int>& a, const char* title) {
    std::cout << title;
    for (int x : a) std::cout << x << ' ';
    std::cout << "\n";
}



int main() {
    setupConsoleRu();

    while (true) {
        clearScreen();

        std::cout
            << "==============================\n"
            << "       Быстрая сортировка     \n"
            << "==============================\n"
            << "1. Ввод массива с клавиатуры\n"
            << "2. Генерация случайного массива\n"
            << "3. Загрузка массива из файла\n"
            << "4. Выход\n\n";

        int choice = readInt("Выберите действие: ");

        if (choice == 4) {
            std::cout << "Выход.\n";
            return 0;
        }

        std::vector<int> original;

        if (choice == 1) {
            // ===== ВВОД С КЛАВИАТУРЫ =====
            int n = readInt("Введите размер массива: ");
            original.resize(n);
            for (int i = 0; i < n; ++i) {
                original[i] = readInt("Элемент: ");
            }
        }
        else if (choice == 2) {
            // ===== ГЕНЕРАЦИЯ =====
            int n = readInt("Размер массива: ");
            int lo = readInt("Минимум: ");
            int hi = readInt("Максимум: ");

            // ---- ВАЖНО: тут подставь твою функцию генерации ----
            // например: original = createRandomArray(n, lo, hi);
            original = createRandomArray(n, lo, hi);
        }
        else if (choice == 3) {
            // ===== ЗАГРУЗКА ИЗ ФАЙЛА =====
            std::cout << "Введите путь к файлу: ";
            std::string path;
            std::getline(std::cin, path);

            std::ifstream fin(path);
            if (!fin) {
                std::cout << "Не удалось открыть файл.\n";
                pauseConsole();
                continue;
            }

            int x;
            while (fin >> x) original.push_back(x);

            if (fin.fail() && !fin.eof()) {
                std::cout << "Ошибка: в файле есть нечисловые данные.\n";
                pauseConsole();
                continue;
            }
        }
        else {
            std::cout << "Неверный пункт меню.\n";
            pauseConsole();
            continue;
        }

        // ===== СОРТИРОВКА =====
        std::vector<int> sorted = original;

        if (!sorted.empty()) {
            // ---- ВАЖНО: подставь твою сортировку ----
            // если у тебя quickSort(arr, l, r):
            quickSort(sorted, 0, (int)sorted.size() - 1);

            // если у тебя QuickSort::sort(arr) возвращает новый:
            // sorted = QuickSort::sort(original);
        }

        clearScreen();
        printVectorLine(original, "Исходный массив: ");
        printVectorLine(sorted, "Отсортированный: ");

        // (необязательно) проверка
        if (!isSorted(sorted)) {
            std::cout << "ВНИМАНИЕ: массив не отсортирован корректно!\n";
        }

        // ===== СОХРАНИТЬ В ФАЙЛ =====
        std::cout << "\nСохранить оба массива в файл? (1-да, 2-нет): ";
        int save;
        std::cin >> save;
        std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');

        if (save == 1) {
            std::cout << "Введите путь для сохранения: ";
            std::string out;
            std::getline(std::cin, out);

            std::ofstream fout(out);
            if (!fout) {
                std::cout << "Не удалось создать файл.\n";
            }
            else {
                fout << "Original:\n";
                for (int v : original) fout << v << ' ';
                fout << "\n\nSorted:\n";
                for (int v : sorted) fout << v << ' ';
                fout << "\n";
                std::cout << "Сохранено.\n";
            }
        }

        pauseConsole();
    }
}
#endif