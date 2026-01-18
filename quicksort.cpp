#include "quicksort.h"

static int partition(std::vector<int>& arr, int left, int right) {
    int pivot = arr[left + (right - left) / 2];
    int i = left;
    int j = right;

    while (i <= j) {
        while (arr[i] < pivot) i++;
        while (arr[j] > pivot) j--;

        if (i <= j) {
            int tmp = arr[i];
            arr[i] = arr[j];
            arr[j] = tmp;
            i++;
            j--;
        }
    }
    return i;
}

void quickSort(std::vector<int>& arr, int left, int right) {
    if (left >= right) return;

    int index = partition(arr, left, right);

    quickSort(arr, left, index - 1);
    quickSort(arr, index, right);
}
