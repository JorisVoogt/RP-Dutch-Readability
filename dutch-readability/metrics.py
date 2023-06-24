import decimal
import math
from decimal import Decimal

# Use two decimal places for metric outputs.
D = decimal.Decimal
two_dec = D(10) ** -2


def accuracy(predict_list: list[list[int]], expect_list: list[int]) -> Decimal | str:
    """
    Calculates the accuracy of a prediction list of grades when compared to the expected grade.

    :param predict_list: List containing prediction grades or range of grades as integers.
    :param expect_list:  The expected grades as integers.
    :return:             The percentage of correct predictions when compared to the grade
                         as Decimal with two decimal places or '-' for no entries.
    """
    correct = 0

    for (pr, ex) in zip(predict_list, expect_list):
        if ex in pr:
            correct += 1

    try:
        return D(correct / len(predict_list)).quantize(two_dec)
    except ZeroDivisionError:
        return "-"


def abs_error_rate(predict: list[int], grade: int) -> int:
    """
    Calculates the difference between a predicted grade or range of grades and the expected grade.
    When a prediction is a range of grades, the grade in the range closest to the expected grade is taken
    for the error rate calculation.

    :param predict: The predicted grade or range of grades as integer.
    :param grade:   The expected grade as integer.
    :return:        The difference between the predicted and expected grade as integer.
    """
    return abs(min(predict, key=lambda x: abs(x - grade)) - grade)


def mae(predict_list: list[list[int]], expect_list: list[int]) -> Decimal | str:
    """
    Calculates the mean absolute error between a list of grade predictions and the expected grade.
    When a prediction is a range of grades, the grade in the range closest to the expected grade is taken
    for the error rate calculation.

    :param predict_list: A list of prediction grades or range of grades as integers.
    :param expect_list:  The expected grades as integers.
    :return:             The average error rate between predicted grades and the expected grade
                         as Decimal with two decimal places or '-' for no entries.
    """
    mae_sum = 0

    for (pr, ex) in zip(predict_list, expect_list):
        mae_sum += abs_error_rate(pr, ex)
        print(mae_sum)

    try:
        return D(mae_sum / len(predict_list)).quantize(two_dec)
    except ZeroDivisionError:
        return "-"


def rmse(predict_list: list[list[int]], expect_list: list[int]) -> Decimal | str:
    """
    Calculates the root-mean-square error between a list of prediction grades and the expected grade.
    When a prediction is a range of grades, the grade in the range closest to the expected grade is taken
    for the error rate calculation.

    :param predict_list: List of prediction grades or range of grades as integers.
    :param expect_list:  The expected grades as integers.
    :return:             The root-mean-square error between predicted grades and the expected grade
                         as Decimal with two decimal places or '-' for no entries.
    """
    rmse_sum = 0

    for (pr, ex) in zip(predict_list, expect_list):
        rmse_sum += pow((min(pr, key=lambda x: abs(x - ex)) - ex), 2)

    try:
        return D(math.sqrt(rmse_sum / len(predict_list))).quantize(two_dec)
    except ZeroDivisionError:
        return "-"
