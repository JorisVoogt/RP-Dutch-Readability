import pandas as pd

# Actual significance testing is done in R.
# These functions construct the significance testing dataframes.


def error_rates_per_formula_and_type(results_file: str, file_out: str, type_to_compare=None) -> None:
    """
    Creates a dataframe with text types and for each readability formula a column of its absolute error rates.

    :param results_file:    The CSV file containing expected grades, text types and predicted grades for each
                            readability formula.
    :param file_out:        The CSV file containing the dataframe ready for significance testing.
    :param type_to_compare: A specific type to compare to the other types. This limits the entries by a grade range.
    :return:                None.
    """
    df = pd.read_csv(results_file)
    out = df[["grade", "maintype", "FD-er", "LiA-er", "CLIB-er", "CLIB_stop-er", "CILT-er", "CILT_stop-er"]].copy()
    out = out.rename(columns={"FD-er": "FD", "LiA-er": "LiA", "CLIB-er": "CLIB", "CLIB_stop-er": "CLIB_stop",
                              "CILT-er": "CILT", "CILT_stop-er": "CILT_stop"})

    if type_to_compare == "media":
        out = out[(out["grade"] <= 6) & (out["grade"] >= 3)]
    if type_to_compare == "school":
        out = out[out["grade"] <= 6]

    out.to_csv(file_out, index=False)


def formula_dataframe(df: pd.DataFrame, formula: str) -> pd.DataFrame:
    """
    Creates a dataframe of the absolute error rates of one readability formula and adds a column with the name of that
    readability formula.

    :param df:      Dataframe containing the error rates on every text in the data set of the supplied
                    readability formula.
    :param formula: The name of the readability formula for which a dataframe is constructed.
    :return:        Dataframe containing error rates and name of the readability formula.
    """
    er_f = formula + "-er"
    fd = df[[er_f]].copy()
    fd["Formula"] = formula
    fd = fd.rename(columns={er_f: "error_rate"})
    return fd


def error_rates_per_text_and_formula(error_rates: str, file_out: str) -> None:
    """
    Creates a dataframe containing the absolute error rates for each six readability formulas per text and stores
    for each error rate which readability formula was used to generate it.

    :param error_rates: The CSV file containing the absolute error rates for each readability formula on all texts.
    :param file_out:    The CSV file containing all the error rates for each text across all six readability formulas
                        with a column stating which readability formula generated which error rate.
                        Used in significance testing.
    :return:            None.
    """
    df = pd.read_csv(error_rates)

    fd = formula_dataframe(df, "FD")
    lia = formula_dataframe(df, "LiA")
    clib = formula_dataframe(df, "CLIB")
    clib_stop = formula_dataframe(df, "CLIB_stop")
    cilt = formula_dataframe(df, "CILT")
    cilt_stop = formula_dataframe(df, "CILT_stop")

    out = pd.concat([fd, lia, clib, clib_stop, cilt, cilt_stop])
    out.to_csv(file_out, index=False)
