def sum_of_items(lst: list) -> int:
    """
    Given a list of integers, return the sum of these integers.
    If the list is empty, return 0.
    ex. [5, 6, 2, 1] --> 5+6+2+1=14
    ex. [0, 0] --> 0+0=0
    """
    sum = 0
    for i in lst:
        sum += i
    return sum

def dict_of_num_type_lsts(lst: list) -> dict:
    """
    Given a list of integers, create a dictionary with three keys: "pos_lst", "zero_lst", and "neg_lst".
    The value of key "pos_lst" should be the list of all positive integers in the argument.
    The value of key "zero_lst" should be the list of all zeroes in the argument.
    The value of key "neg_lst" should be the list of all negative integers in the argument.
    ex. [4, 2, 5, 0, 2, 1, 0, -1] -->
        {"pos_lst": [4, 2, 5, 2, 1], "zero_lst": [0, 0], "neg_lst": [-1]}
    """
    pos_lst = []
    neg_lst = []
    zero_lst = []
    for i in lst:
        pos_lst.append(i) if i > 0 else neg_lst.append(i) if i < 0 else zero_lst.append(i)
    return {"pos_lst":pos_lst,"zero_lst":zero_lst,"neg_lst":neg_lst}

def ratings_adjustment(ratings):
    """
    Given a dictionary containing the overall student ratings of the AppDev courses,
    with course names as keys and ratings as values, ensure that the results are correct.

    Naturally, any courses with a higher rating than 'backend' must have cheated,
    so they should be removed from the dictionary entirely.

    Return the corrected dictionary.
    """
    highest = ratings["backend"]
    correct = {}
    for course, rate in ratings.items():
        if not rate > highest:
            correct[course] = rate
    return correct

class Counter:
    """
    Implement this Counter class with three functions as outlined below:

    - 'getVal' that gets the 'value' of a Counter object.
    - 'inc' that increases the 'value' of the object by 1.
    - 'dec' that decreases the 'value' of the object by 1.

    Note:
    'value' would be an instance variable in this Counter class.
    On creation, this should be initialized to 0.
    """

    def __init__(self):
        self.value = 0

    def getVal(self):
        return self.value

    def inc(self):
        self.value += 1

    def dec(self):
        self.value -= 1


"""
YOU DO NOT HAVE TO MODIFY THE CODE BELOW.

It is there for you to check your answers with the expected values through
a series of print statements. If you would like to run the segment of code
below, run this Python script.
"""
if __name__ == "__main__":
    empty_lst = []
    big_lst = [-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5]
    small_lst = [-1, 0, 1]
    lst_with_only_zeroes = [0, 0, 0]

    print("sum_of_items results:")
    print(f"sum_of_items({empty_lst}): {sum_of_items(empty_lst)}")
    print(f"sum_of_items({big_lst}): {sum_of_items(big_lst)}")
    print(f"sum_of_items({small_lst}): {sum_of_items(small_lst)}")
    print(
        f"sum_of_items({lst_with_only_zeroes}): {sum_of_items(lst_with_only_zeroes)}"
    )
    print()

    print("dict_of_num_type_lsts results:")
    print(
        f"dict_of_num_type_lsts({empty_lst}): {dict_of_num_type_lsts(empty_lst)}"
    )
    print(f"dict_of_num_type_lsts({big_lst}): {dict_of_num_type_lsts(big_lst)}")
    print(
        f"dict_of_num_type_lsts({small_lst}): {dict_of_num_type_lsts(small_lst)}"
    )
    print(
        f"dict_of_num_type_lsts({lst_with_only_zeroes}): {dict_of_num_type_lsts(lst_with_only_zeroes)}"
    )
    print()

    test_ratings = {'backend': 5, 'ios': 3, 'android': 7}
    print("ratings_adjustment results:")
    print(f"ratings_adjustment({test_ratings}): {ratings_adjustment(test_ratings)}")
    print()

    print("Counter results:")
    counter = Counter()
    print(f"counter.getVal(): {counter.getVal()}")
    counter.inc()
    counter.inc()
    print(f"counter.inc(), counter.inc(): {counter.getVal()}")
    counter.dec()
    print(f"counter.dec(): {counter.getVal()}")
    print()


