#include "array.h"
#include <cstdlib>
#include <ctime>

std::vector<int> createRandomArray(int size, int min, int max) {
    std::srand(static_cast<unsigned>(std::time(nullptr)));
    std::vector<int> arr(size);

    for (int i = 0; i < size; i++) {
        arr[i] = min + std::rand() % (max - min + 1);
    }
    return arr;
}
