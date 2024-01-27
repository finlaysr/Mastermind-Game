"""Finlay Robb - 21/08/23 - AH Computing Standard Algorithms"""

def bubble_sort(array: list | set | tuple, val=lambda l: l, reverse: bool = False) -> list:
    """Sort an array using insertion sort and return sorted array
    @param array: list to be sorted
    @param val: which index in a > 1D array to be sorted by
    @param reverse: True to sort in descending order"""
    n = len(array); swapped = True
    while swapped and n >= 0:  # Loop while not done moving elements around
        swapped = False
        for i in range(0, n - 1):
            if (val(array[i]) > val(array[i + 1]) and not reverse) or (val(array[i]) < val(array[i + 1]) and reverse):
                array[i], array[i + 1] = array[i + 1], array[i]  # Swap elements
                swapped = True
        n -= 1  # Elements above n in list are now sorted so no need to go over them again
    return array

def insertion_sort(array: list | set | tuple, val=lambda l: l, reverse: bool = False) -> list:
    """Sort an array using insertion sort and return sorted array
    @param array: list to be sorted
    @param val: which index in a > 1D array to be sorted by
    @param reverse: True to sort in descending order"""
    for i in range(1, len(array)):  # Loop through each element in the array
        value = array[i]  # Initial value
        index = i
        while index > 0 and ((val(value) < val(array[index - 1]) and not reverse) or (
                val(value) > val(array[index - 1]) and reverse)):
            array[index] = array[index - 1]  # Copy element up one index in the list
            index -= 1
        array[index] = value  # Set the lowest index found to the initial value
    return array

def binary_search(array: list | set | tuple, target: str | int | float) -> int | None:
    """Locate a value in a sorted array using binary search and return index found at"""
    low = 0; found = False; high = len(array)
    while not found and low <= high:  # Repeat until value found or all values checked
        mid = (low + high) // 2  # // used so that whole number returned, not float
        if target == array[mid]:  # If found
            found = True
            return mid
        elif target > array[mid]:  # If too high
            low = mid + 1
        else:  # If too low
            high = mid - 1
    if not found:
        print('Target not found')
        return None
