from .. import syllable_counter
import pandas as pd
import textstat


def read_unique_words(file_in: str) -> set["str"]:
    """
    Extracts the unique words from a set of texts in a CSV file.
    File must contain a column header 'text' for other files to work.

    :param file_in: A CSV file containing texts in a column named 'text'.
    :return:        A set of unique words in texts in the supplied file.
    """
    dataset = pd.read_csv(file_in)
    unique_words_set = set()

    for text in dataset["text"]:
        text = syllable_counter.clean_text(text)
        for word in text.split():
            unique_words_set.add(word)

    return unique_words_set


def accuracy_whole_unique_words(dataset: set[str]) -> str:
    """
    Calculates the percentage of unique words which are in the CELEX dictionary.
    As these have their supplied syllable amounts, this percentage equals accuracy.

    :param dataset: A dataset of unique words for which accuracy should be tested.
    :return:        Message including the accuracy of correct syllable counts for the supplied dataset.
    """
    dictionary = syllable_counter.dictionary_init()
    in_dictionary = 0

    for word in dataset:
        if word in dictionary:
            in_dictionary += 1

    return "Accuracy whole unique words in CELEX dataset: " + str((in_dictionary/len(dataset)) * 100)


def accuracy_compound_unique_words(dataset: set[str]) -> str:
    """
    Calculates the percentage of compound unique words which are in the CELEX dictionary.
    As these have their supplied syllable amounts, this percentage equals accuracy.

    :param dataset: A dataset of unique words for which accuracy should be tested.
    :return:        Message including the accuracy of correct syllable counts for the supplied dataset,
                    percentage of words partially in the CELEX dictionary and
                    percentage of words not in the CELEX dictionary.
    """
    sc = syllable_counter.SyllableCounter()
    total = len(dataset)

    for word in dataset:
        sc.count_syllables_word(word, word, test_accuracy=True)

    return "Accuracy compound unique words in CELEX dataset: " + str(((total-sc.get_textstat_count())/total)*100) \
        + "\nPercentage of words partially using Textstat's syllable_count: " \
        + str(((sc.get_textstat_count()-sc.get_unknown_count())/total)*100) \
        + "\nPercentage of words completely using Textstat's syllable_count: " + str((sc.get_unknown_count()/total)*100)


def accuracy_syllable_counter(file: str = "Data/words_and_syllables.csv") -> str:
    """
    Calculates the accuracies of both the SyllableCounter class and Textstat's syllable_count() method.

    :param file: A CSV file with two columns, one with header 'word' containing Dutch words,
                 the other with header 'syllables' containing the amount of syllables for the word in the same row.
    :return:     Message including accuracies for both syllable counters.
    """
    sc = syllable_counter.SyllableCounter()
    words_syllables = pd.read_csv(file, sep=';')

    syllable_count_sc = words_syllables["word"].apply(lambda x: sc.count_syllables_word(x, x))
    syllable_count_ts = words_syllables["word"].apply(lambda x: textstat.syllable_count(x))

    accuracy_sc = (syllable_count_sc == words_syllables["syllables"]).mean()
    accuracy_ts = (syllable_count_ts == words_syllables["syllables"]).mean()

    return "Accuracy SyllableCounter: " + str(accuracy_sc*100) + "\nAccuracy Textstat's syllable_count: " \
        + str(accuracy_ts*100)
