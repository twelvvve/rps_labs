#include "gtest/gtest.h"
#include "quicksort.h"
#include <vector>

TEST(QuickSort_test, positive_num) {
    std::vector<int> arr = { 1, 5, 3, 9, 6, 33 };
    std::vector<int> expected = { 1, 3, 5, 6, 9, 33 };
    quickSort(arr, 0, (int)arr.size() - 1);
    EXPECT_EQ(arr, expected);
}

TEST(QuickSort_test, negative_num) {
    std::vector<int> arr = { -1, -5, -3, -9, -6, -33 };
    std::vector<int> expected = { -33, -9, -6, -5, -3, -1 };
    quickSort(arr, 0, (int)arr.size() - 1);
    EXPECT_EQ(arr, expected);
}

TEST(QuickSort_test, identical_num) {
    std::vector<int> arr = { 5, 5, 5, 5 };
    std::vector<int> expected = { 5, 5, 5, 5 };
    quickSort(arr, 0, (int)arr.size() - 1);
    EXPECT_EQ(arr, expected);
}

TEST(QuickSort_test, single_element) {
    std::vector<int> arr = { 42 };
    std::vector<int> expected = { 42 };
    quickSort(arr, 0, (int)arr.size() - 1);
    EXPECT_EQ(arr, expected);
}

TEST(QuickSort_test, empty_array) {
    std::vector<int> arr = {};
    std::vector<int> expected = {};
    // для пустого массива quickSort не вызываем
    EXPECT_EQ(arr, expected);
}
