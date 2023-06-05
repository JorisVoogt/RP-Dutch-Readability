import io
import folia.main as folia
import csv
import pandas as pd
import textstat
import re
from nltk.corpus import stopwords

# The path to the BasiLex-Corpus Data folder.
dataset_path = "path/to/BasiLex/folder/Data/"

# The amount of folders and files in the BasiLex Data folder.
dataset_data_map = 68
dataset_map1 = 68
dataset_map2 = 67


def write_dataset(file_out: str, file_issues: str) -> None:
    """
    Reads FoLiA formatted xml files from the BasiLex-Corpus and stores
    the text, type, subtype and grade in a supplied csv file; first round of preprocessing.
    The path to the corpus should be entered at the top of this file.

    WARNING: This process can take a lot of time, approx. 5 hours!

    :param file_out:    The CSV file in which the data should be stored.
    :param file_issues: The CSV file in which issues should be stored (unable to read or no grade).
    :return:            None
    """
    writer_issues = None
    issues_file = None
    if file_issues is not None:
        writer_issues, issues_file = issues_writer(file_issues)

    with open(file_out, 'w', newline='', encoding='utf-8') as dataset_file:
        writer_dataset = csv.writer(dataset_file, delimiter=';')
        column_headers_dataset = ["text", "maintype", "type", "grade"]
        writer_dataset.writerow(column_headers_dataset)

        for map1 in range(dataset_data_map):
            for map2 in range(dataset_map1):
                for file_number in range(dataset_map2):

                    # The cut-off point as no further files exist in the BasiLex-Corpus.
                    if map1 == 67 and map2 == 11 and file_number == 5:
                        break

                    file_path = str(map1) + "/" + str(map2) + "/" + str(file_number) + ".xml"
                    data_path = dataset_path + file_path
                    data_entry = read_dataset_paragraph(data_path, file_path)

                    if file_issues is not None and len(data_entry) == 2:
                        writer_issues.writerow(data_entry)
                    else:
                        writer_dataset.writerow(data_entry)
                else:
                    continue
                break
            else:
                continue
            break

    if file_issues is not None:
        issues_file.close()


def read_dataset_paragraph(file_in: str, file_path: str) -> list[str]:
    """
    Tries to read a file from the BasiLex-Corpus.
    Warnings that the files have no FoLiA version could not be suppressed.

    :param file_in:   A FoLiA xml file from the BasiLex-Corpus.
    :param file_path: The path of a FoLiA xml file in the Data folder of the BasiLex-Corpus.
    :return:          List containing the issue with file_path or data.
    """
    try:
        doc = folia.Document(file=file_in)
    except folia.ParseError:
        return ["Cannot read file", file_path]

    text = doc.text()
    diction = doc.metadata
    maintype = diction["maintype"]
    subtype = diction["type"]

    try:
        grade = diction["grade"]
    except KeyError:
        return ["No grade for entry", file_path]

    return [text, maintype, subtype, grade]


def issues_writer(file: str) -> (csv.writer, io.TextIOWrapper):
    """
    CSV file writer for issues during write_dataset function.

    :param file: The CSV file in which the issues are stored.
    :return:     CSV file writer and the file to be closed.
    """
    issues_file = open(file, 'w', newline='', encoding='utf-8')
    writer_issues = csv.writer(issues_file, delimiter=';')
    column_headers_issues = ["issue", "file"]
    writer_issues.writerow(column_headers_issues)
    return writer_issues, issues_file


def filter_dataset(file_in: str, file_filtered: str, words: int = 75, sentences: int = 5, grades: set[str] = None) \
        -> None:
    """
    Filters the BasiLex dataset to only contain texts with enough words and sentences
    and removes texts not in grades; second round of preprocessing.

    :param file_in:       The BasiLex dataset CSV file obtained after the first round of preprocessing.
    :param file_filtered: The CSV file in which the filtered BasiLex dataset is stored.
    :param words:         (optional) The amount of words a text should contain, set to 75.
    :param sentences:     (optional) The amount of sentences a text should contain, set to 5.
    :param grades:        (optional) The grades a text is meant for, set to (3-8, 1VO and 2VO).
    :return:              None
    """
    if grades is None:
        grades = {"3", "4", "5", "6", "7", "8", "1VO", "2VO"}
    df = pd.read_csv(file_in, sep=';')
    df = df[df["text"].apply(lambda x: len(x.split()) >= words and textstat.sentence_count(x) >= sentences)]
    filtered = df[df["grade"].apply(lambda x: x in grades)]
    filtered.to_csv(file_filtered, index=False)


def preprocess_dataset(file_out: str, file_raw_data: str, file_issues: str = None) -> None:
    """
    The preprocessing of the BasiLex-Corpus.

    :param file_out:      The CSV file in which the preprocessed dataset is stored.
    :param file_raw_data: The CSV file in which the raw dataset is stored.
    :param file_issues:   (optional) The CSV file in which non-readable or entries with no grades are stored.
    :return:              None
    """
    write_dataset(file_raw_data, file_issues)
    filter_dataset(file_raw_data, file_out)


def preprocess_frequency_list(freq_list: str, freq77_file: str, freq77_no_stop_file: str) -> None:
    """
    The preprocessing of the frequency word list by Schrooten & Vermeer (Aflopende-frequentielijst (obv geo gem)
    https://annevermeer.github.io/woordwerken.html).
    Removes word meanings/additional information, duplicates and orders the list on highest total frequency.
    Keeps the words forming a cumulative 77% of the frequency list.

    :param freq_list:           The CSV file containing the frequency word list by Schrooten & Vermeer.
    :param freq77_file:         The CSV file in which the preprocessed frequency word list is stored.
    :param freq77_no_stop_file: The CSV file in which the preprocessed frequency word list without stopwords is stored.
    :return:                    None
    """
    fl = pd.read_csv(freq_list, sep=';')

    # Rename Dutch "woord" to English "word" and "fr-total" to "frequency".
    fl = fl.rename(columns={"woord": "word", "fr-total": "frequency"})

    fl = fl[["word", "frequency"]]

    # Remove additional information and variations to obtain base words.
    fl.loc[:, "word"] = fl["word"].apply(lambda x: re.sub(r"(\(.+\))|(_.*)|(\*.+)|(.+(?<!\()\.\.\.)", '', x))

    fl = fl.sort_values(by=["frequency"], ascending=False)

    # Remove Dutch stopwords in the NLTK package from the frequency list.
    stops = set(stopwords.words("dutch"))
    fl_no_stop = fl[fl["word"].apply(lambda x: x not in stops)]
    fl_no_stop.loc[:, ["frequency"]] = fl_no_stop["frequency"].cumsum()

    # Frequency word list with stopwords
    fl.loc[:, "frequency"] = fl["frequency"].cumsum()

    percent77 = fl["frequency"].iloc[-1] * 0.77
    percent77_no_stop = fl_no_stop["frequency"].iloc[-1] * 0.77

    freq77 = fl[fl["frequency"].apply(lambda x: x <= percent77)].drop_duplicates(subset=["word"])
    freq77_no_stop = fl_no_stop[fl_no_stop["frequency"].apply(lambda x: x <= percent77_no_stop)] \
        .drop_duplicates(subset=["word"])

    freq77.loc[:, "word"] = freq77["word"].apply(lambda x: textstat.remove_punctuation(x))
    freq77_no_stop.loc[:, "word"] = freq77_no_stop["word"].apply(lambda x: textstat.remove_punctuation(x))

    freq77.loc[:, "word"].to_csv(freq77_file, index=False)
    freq77_no_stop.loc[:, "word"].to_csv(freq77_no_stop_file, index=False)
