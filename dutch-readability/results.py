from typing import Callable
from decimal import Decimal
import pandas as pd
from ast import literal_eval
import matplotlib.pyplot as plt
import seaborn as sns
import metrics


def str_to_list(column: pd.Series) -> list[list[int]]:
    """
    Changes a string representation of a list back to an actual list in Python using the Abstract Syntax Trees library.

    :param column: The pandas series containing string representations of lists.
    :return:       A list containing list representations of integers.
    """
    return column.apply(lambda x: literal_eval(x))


def create_type_column(df: pd.DataFrame, pr_grades_column: str,
                       metric: Callable[[list[list[int]], list[int]], Decimal]) -> list[Decimal]:
    """
    Creates a text type column for a specific readability formula and metric across the grades.

    :param df:               The expected and predicted grades for a certain text type and readability formula.
    :param pr_grades_column: The name of the predicted grades column for a specific readability formula and text type.
    :param metric:           The metric to be calculated on the predicted and expected grades.
    :return:                 A table column as a list containing the metric values rounded to two decimal places.
    """
    column = []

    for grade in range(8):
        df_grade = df[df["grade"] == grade + 1]
        column.append(metric(df_grade[pr_grades_column], df_grade["grade"]))

    column.append(metric(df[pr_grades_column], df["grade"]))

    return column


def create_grade_type_table(results_file: str, pr_grades_column: str, table_file: str,
                            metric: Callable[[list[list[int]], list[int]], Decimal]) -> None:
    """
    Creates a table for a readability formula containing metric values for a specified metric across text types
    and grades.

    :param results_file:     The CSV file containing expected grades, text types and predicted grades for each
                             readability formula.
    :param pr_grades_column: The name of the predicted grades column for a specific readability formula and text type.
    :param table_file:       The CSV file in which the resulting pandas dataframe or table will be stored.
    :param metric:           The metric to be calculated on the predicted and expected grades.
    :return:                 None.
    """
    df = pd.read_csv(results_file)

    df[pr_grades_column] = str_to_list(df[pr_grades_column])
    table = pd.DataFrame()

    table[None] = ["Grade 1", "Grade 2", "Grade 3", "Grade 4", "Grade 5", "Grade 6", "Grade 7", "Grade 8", "All grades"]
    table["School"] = create_type_column(df[df["maintype"] == "school"].loc[:, ["grade", pr_grades_column]],
                                         pr_grades_column, metric)
    table["Books"] = create_type_column(df[df["maintype"] == "leesboeken"].loc[:, ["grade", pr_grades_column]],
                                        pr_grades_column, metric)
    table["Media"] = create_type_column(df[df["maintype"] == "media"].loc[:, ["grade", pr_grades_column]],
                                        pr_grades_column, metric)
    table["All types"] = create_type_column(df.loc[:, ["grade", pr_grades_column]], pr_grades_column, metric)

    table.to_csv(table_file, index=False)


def create_formula_tables(results_file: str, pr_grades_column: str, formula: str) -> None:
    """
    Creates three tables for a specific readability formula containing three different metric values
    across both text types and grades.

    :param results_file:     The CSV file containing expected grades, text types and predicted grades for each
                             readability formula.
    :param pr_grades_column: The name of the predicted grades column for a specific readability formula and text type.
    :param formula:          The name of the readability formula for which three metric tables should be created.
    :return:                 None.
    """
    table_file = "Data/Tables/"
    create_grade_type_table(results_file, pr_grades_column, table_file + formula +
                            "_accuracy_table.csv", metrics.accuracy)
    create_grade_type_table(results_file, pr_grades_column, table_file + formula + "_mae_table.csv", metrics.mae)
    create_grade_type_table(results_file, pr_grades_column, table_file + formula + "_rmse_table.csv", metrics.rmse)


def create_tables(results_file: str) -> None:
    """
    Creates 18 tables, three for each readability formula (three different metrics), containing metric values across
    text types and grades.

    :param results_file: The CSV file containing expected grades, text types and predicted grades for each
                         readability formula.
    :return:             None.
    """
    create_formula_tables(results_file, "FD-grade", "Flesch-Douma")
    create_formula_tables(results_file, "LiA-grade", "Leesindex_A")
    create_formula_tables(results_file, "CLIB-grade", "CLIB")
    create_formula_tables(results_file, "CLIB_stop-grade", "CLIB_stop")
    create_formula_tables(results_file, "CILT-grade", "CILT")
    create_formula_tables(results_file, "CILT_stop-grade", "CILT_stop")


def calculate_error_rate_per_formula(expect_list: list[int], predict_list: list[list[int]]) -> list[int]:
    """
    Calculates the error rates between a column of expected grades and a column of predicted grades of a specific
    readability formula.

    :param expect_list:  A column or list containing the expected grades of texts.
    :param predict_list: A column or list containing lists or ranges of predicted grades of texts from a readability
                         formula.
    :return:             A column or list containing the absolute error rates between each expected grade and list of
                         predicted grades.
    """
    error_rates = []

    for (pr, ex) in zip(predict_list, expect_list):
        error_rates.append(metrics.abs_error_rate(pr, ex))

    return error_rates


def calculate_error_rates(results_file: str) -> None:
    """
    Calculates the absolute error rates between the expected grades of the data set and the predicted grades
    of the six readability formulas. The absolute error rates are appended to the data set file supplied as input.

    :param results_file: The CSV file containing expected grades, text types and predicted grades for each
                         readability formula.
    :return:             None.
    """
    df = pd.read_csv(results_file)
    ex = df["grade"]

    df["FD-er"] = calculate_error_rate_per_formula(ex, str_to_list(df["FD-grade"]))
    df["LiA-er"] = calculate_error_rate_per_formula(ex, str_to_list(df["LiA-grade"]))
    df["CLIB-er"] = calculate_error_rate_per_formula(ex, str_to_list(df["CLIB-grade"]))
    df["CLIB_stop-er"] = calculate_error_rate_per_formula(ex, str_to_list(df["CLIB_stop-grade"]))
    df["CILT-er"] = calculate_error_rate_per_formula(ex, str_to_list(df["CILT-grade"]))
    df["CILT_stop-er"] = calculate_error_rate_per_formula(ex, str_to_list(df["CILT_stop-grade"]))

    df.to_csv(results_file, index=False)


def create_formula_dataframe(df: pd.DataFrame, formula: str) -> pd.DataFrame:
    """
    Creates a pandas dataframe for a specific readability formula containing expected grades,
    absolute error rates between expected grades and predicted grades, name of the readability formula and text type.

    :param df:      Dataframe containing expected grades and absolute error rates on each of the six readability
                    formulas.
    :param formula: The name of the readability formula for which the dataframe should be created.
    :return:        Dataframe containing expected grades, absolute error rates, name of readability formula and the text
                    type.
    """
    er_f = formula + "-er"
    df_form = df[["grade", er_f]].copy()
    df_form["Formula"] = formula
    df_form = df_form.rename(columns={er_f: "error_rate"})
    return df_form


def create_type_dataframe(df: pd.DataFrame, maintype: str) -> pd.DataFrame:
    """
    Creates a dataframe for a specific text type containing expected grades, absolute error rates
    between expected grades and predicted grades, names of the readability formulas and text type.

    :param df:       Dataframe containing expected grades, text types and absolute error rates for each readability
                     formula.
    :param maintype: The text type for which a dataframe should be created.
    :return:         Dataframe containing expected grades, absolute error rates, names of readability formulas and the
                     text type.
    """
    df_type = df[df["maintype"] == maintype]

    df_type = df_type[["grade", "FD-er", "LiA-er", "CLIB-er", "CLIB_stop-er", "CILT-er", "CILT_stop-er"]]

    df_fd = create_formula_dataframe(df_type, "FD")
    df_lia = create_formula_dataframe(df_type, "LiA")
    df_clib = create_formula_dataframe(df_type, "CLIB")
    df_clib_stop = create_formula_dataframe(df_type, "CLIB_stop")
    df_cilt = create_formula_dataframe(df_type, "CILT")
    df_cilt_stop = create_formula_dataframe(df_type, "CILT_stop")

    df_type = pd.concat([df_fd, df_lia, df_clib, df_clib_stop, df_cilt, df_cilt_stop])

    # Changes Dutch text types to English.
    match maintype:
        case "school":
            maintype = "School"
        case "leesboeken":
            maintype = "Books"
        case "media":
            maintype = "Media"

    df_type["Type"] = maintype

    return df_type


def create_boxplot_data(results_file: str, file_out: str) -> None:
    """
    Creates a dataframe which allows for absolute error rates to be plotted across readability formulas, text types
    and grades. It is stored as a CSV file.

    :param results_file: The CSV file containing expected grades, text types and predicted grades for each
                         readability formula.
    :param file_out:     The CSV file containing a dataframe of absolute error rates which is plottable.
    :return:             None.
    """
    calculate_error_rates(results_file)
    df = pd.read_csv(results_file)

    school = create_type_dataframe(df, "school")
    books = create_type_dataframe(df, "leesboeken")
    media = create_type_dataframe(df, "media")

    merged = pd.concat([school, books, media])
    merged.to_csv(file_out, index=False)


def boxplot_error_rates(boxplot_data: str) -> None:
    """
    Creates box plots for the absolute error rates across readability formulas, text types and grades.
    The plots are saved as a figure.

    :param boxplot_data: The CSV file containing absolute error rates per grade, readability formula and text type.
    :return:             None.
    """
    df = pd.read_csv(boxplot_data)

    g = sns.FacetGrid(df, col="Type", row="Formula", margin_titles=True, sharex=False)
    g.map_dataframe(sns.boxplot, x="grade", y="error_rate", palette="crest", linewidth=1.5)
    g.set_titles(row_template="{row_name}", col_template="{col_name}", size=14)

    [g.axes[i, 0].set_ylabel("MAE", fontsize=14) for i in range(6)]
    [g.axes[5, j].set_xlabel("Grade", fontsize=14) for j in range(3)]

    plt.gcf().set_size_inches(10, 10)
    g.savefig(fname="Data/Figures/error_rates_test.png")
