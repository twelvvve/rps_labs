#include "gtest/gtest.h"
#include "quicksort.h"
#include "validation.h"
#include "array.h"
using namespace std;

// вспомогательна€ функци€ Ч сортирует и возвращает результат
static vector<int> sorted(vector<int> arr) {
    if (!arr.empty())
        quickSort(arr, 0, (int)arr.size() - 1);
    return arr;
}

TEST(QuickSortTest, positive_num) {
    vector<int> arr = { 1, 5, 3, 9, 6, 33 };
    vector<int> expected = { 1, 3, 5, 6, 9, 33 };
    EXPECT_EQ(sorted(arr), expected);
}

TEST(QuickSortTest, negative_num) {
    vector<int> arr = { -1, -5, -3, -9, -6, -33 };
    vector<int> expected = { -33, -9, -6, -5, -3, -1 };
    EXPECT_EQ(sorted(arr), expected);
}

TEST(QuickSortTest, identical_num) {
    vector<int> arr = { 5, 5, 5, 5 };
    vector<int> expected = { 5, 5, 5, 5 };
    EXPECT_EQ(sorted(arr), expected);
}

TEST(QuickSortTest, single_element) {
    vector<int> arr = { 42 };
    vector<int> expected = { 42 };
    EXPECT_EQ(sorted(arr), expected);
}

TEST(QuickSortTest, empty_array) {
    vector<int> arr = {};
    vector<int> expected = {};
    EXPECT_EQ(sorted(arr), expected);
}

TEST(QuickSortTest, reverse_sorted) {
    vector<int> arr = { 9, 7, 5, 3, 1 };
    vector<int> expected = { 1, 3, 5, 7, 9 };
    EXPECT_EQ(sorted(arr), expected);
}

TEST(IsSortedTest, sorted_array) {
    vector<int> arr = { 1, 2, 3, 4, 5 };
    EXPECT_TRUE(isSorted(arr));
}

TEST(IsSortedTest, unsorted_array) {
    vector<int> arr = { 1, 3, 2, 4 };
    EXPECT_FALSE(isSorted(arr));
}

TEST(CreateArrayTest, correct_size) {
    auto arr = createRandomArray(10, 0, 100);
    EXPECT_EQ((int)arr.size(), 10);
}

TEST(CreateArrayTest, values_in_range) {
    auto arr = createRandomArray(100, 5, 50);
    for (int val : arr) {
        EXPECT_GE(val, 5);
        EXPECT_LE(val, 50);
    }
}