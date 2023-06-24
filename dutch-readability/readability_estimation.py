import textstat
import syllable_counter
import spacy
import pandas as pd
from nltk.corpus import stopwords

# Training of spacy text lemmatizer.
nlp = spacy.load("nl_core_news_sm")

# Importing the frequency word lists.
freq77_list = "resources/freq77.csv"
freq77_no_stop_list = "resources/freq77_no_stop_words.csv"

# Importing Dutch stopwords from the NLTK package.
stops = set(stopwords.words("dutch"))

# The score-to-grade mappings for each readability formula.
# Edge cases for the score ranges are based upon the scores produced by the readability formulas.
flesch_douma_mapping = {range(-5, 30): [13], range(30, 45): [11, 12], range(45, 60): [9, 10], range(60, 70): [7, 8],
                        range(70, 80): [6], range(80, 90): [5], range(90, 101): [4], range(101, 130): [1, 2, 3]}

leesindex_a_mapping = {range(-20, 20): [13], range(20, 35): [11, 12, 13], range(35, 40): [10, 11, 12, 13],
                       range(40, 50): [10, 11], range(50, 55): [8, 9, 10, 11], range(55, 69): [8, 9, 10],
                       range(69, 74): [5, 6, 7, 8], range(74, 79): [4, 5], range(79, 84): [3, 4, 5],
                       range(84, 89): [3, 4], range(89, 101): [2, 3], range(101, 130): [1, 2]}

clib_mapping = {range(-25, 8): [1], range(8, 21): [2], range(21, 36): [3], range(36, 49): [4], range(49, 62): [5],
                range(62, 75): [6], range(75, 88): [7], range(88, 200): [8]}

cilt_mapping = {range(45, 59): [1], range(59, 64): [2], range(64, 68): [3], range(68, 72): [4],
                range(72, 75): [5], range(75, 135): [6, 7, 8]}


def remove_stop_words(text: str) -> (str, int):
    """
    Removes Dutch stop words in the NLTK Python library from a text.

    :param text: A String representing text.
    :return:     A tuple including the same string as input without stop words, capitals and punctuation
                 and an integer representing the amount of removed stop words.
    """
    text = text.lower()
    text = textstat.remove_punctuation(text)

    words = []
    stop_count = 0
    for word in text.split():
        if word not in stops:
            words.append(word)
        else:
            stop_count += 1

    return ' '.join(words), stop_count


def text_lemmatizer(text: str) -> list[str]:
    """
    Text lemmatization or changing words to their base form.
    WARNING: First word in the returned list is still capitalized!

    :param text: The String which should be lemmatized.
    :return:     Lemmatized string with no capitals or punctuation.
    """
    text = text.lower()
    text = textstat.remove_punctuation(text)
    doc = nlp(text)
    cleaned_lemmas = [t.lemma_ for t in doc]
    return cleaned_lemmas


def estimate_texts(dataset: str, file_out: str) -> None:
    """
    Calculates the readability scores for texts using the Flesch-Douma, Leesindex A, CLIB (two freq77 versions)
    and CILT (two freq77 versions).
    Adds the scores under new columns to the existing dataset of texts.

    :param dataset:  The CSV file containing the texts.
    :param file_out: The CSV file which will store the scores alongside the texts.
    :return:         None
    """
    df = pd.read_csv(dataset)
    fd, lia, clib, clib_stop, cilt, cilt_stop = [[] for _ in range(6)]

    for text in df["text"]:
        read_est = ReadabilityEstimation(text)
        fd.append(read_est.flesch_douma())
        lia.append(read_est.leesindex_a())
        clib.append(read_est.clib())
        clib_stop.append(read_est.clib(freq_no_stop=False))
        cilt.append(read_est.cilt())
        cilt_stop.append(read_est.cilt(freq_no_stop=False))

    df["FD-score"] = fd
    df["LiA-score"] = lia
    df["CLIB-score"] = clib
    df["CLIB_stop-score"] = clib_stop
    df["CILT-score"] = cilt
    df["CILT_stop-score"] = cilt_stop
    df.to_csv(file_out, index=False)


def map_score_to_grade(score: int, mapping: dict[range, [int]], formula: str) -> list[int]:
    """
    Maps a range of scores to a list (range) of school grade given the mapping.
    For the existing mappings, see top of this module.

    :param score:   An integer representing a score.
    :param mapping: A mapping from a range of scores to a list (range) of school grades.
    :param formula: The String representation of the formula being mapped.
    :return:        List (range) of school grades as integers.
    """
    for key in mapping:
        if score in key:
            return mapping[key]
    raise Exception("Invalid/Unknown score: " + str(score) + " for formula " + formula)


def scores_to_grades(scores_file: str) -> None:
    """
    Maps the readability formula scores to grades or ranges of grades using score to grade maps
    and adds the prediction grades as additional columns to the scores_file.

    :param scores_file: The CSV file containing the scores of the readability formulas.
    :return:            None.
    """
    df = pd.read_csv(scores_file)
    df["FD-grade"] = df["FD-score"].apply(lambda x: map_score_to_grade(x, flesch_douma_mapping, "Flesch-Douma"))
    df["LiA-grade"] = df["LiA-score"].apply(lambda x: map_score_to_grade(x, leesindex_a_mapping, "Leesindex A"))
    df["CLIB-grade"] = df["CLIB-score"].apply(lambda x: map_score_to_grade(x, clib_mapping, "CLIB"))
    df["CLIB_stop-grade"] = df["CLIB_stop-score"].apply(lambda x: map_score_to_grade(x, clib_mapping, "CLIB stop"))
    df["CILT-grade"] = df["CILT-score"].apply(lambda x: map_score_to_grade(x, cilt_mapping, "CILT"))
    df["CILT_stop-grade"] = df["CILT_stop-score"].apply(lambda x: map_score_to_grade(x, cilt_mapping, "CILT stop"))
    df.to_csv(scores_file, index=False)


class ReadabilityEstimation:
    """
    Readability estimation class for the Dutch language using four well-known Dutch traditional readability formulas:
    Flesch-Douma, Leesindex A, CLIB and CILT.
    Their scores are rounded down to the nearest integer.

    Attribute syllable_counter: A syllable counter class with a syllable dictionary.
                                Used for counting syllables in a text.
                                See syllable_counter.py for more information.
    """

    __syllable_counter = syllable_counter.SyllableCounter()

    def __init__(self, text: str):
        """
        Stores a piece of text, its main- and subtype and grade.
        Using the text, it calculates and stores variables used in multiple Dutch readability formulas.

        :param text:     A piece of text from the BasiLex-corpus.
        """
        self.text = text
        self.sentence_count = textstat.sentence_count(text)
        self.word_count = textstat.lexicon_count(text)
        self.letter_count = textstat.letter_count(text)
        self.syllable_count = self.__syllable_counter.count_syllables_text(text)
        self.freq77 = self.calculate_freq77(freq77_list, text)
        self.freq77_no_stop = self.calculate_freq77(freq77_no_stop_list, text, remove_stop=True)

    def calculate_freq77(self, file: str, text: str, remove_stop=False) -> float:
        """
        Calculates the freq77 variable from the CLIB and CILT formulas.
        Uses lemmatization as the frequency word list only contains lemmatized words.

        :param file:        A Dutch word list with a cumulative frequency of 77%,
                            i.e. the most frequent words in children's texts.
                            Based upon Schrooten & Vermeer's frequency list.
        :param text:        The String on which the freq77 should be calculated.
        :param remove_stop: Boolean signifying if stop words should be removed from the text or not.
        :return:            A float signifying the freq77.
        """
        fl = pd.read_csv(file)
        fl = fl["word"].tolist()

        stop_count = 0
        if remove_stop:
            text, stop_count = remove_stop_words(text)

        text = text_lemmatizer(text)

        frequent = 0
        for word in text:
            word = word.lower()
            if word in fl:
                frequent += 1
        try:
            return ((frequent + stop_count) / self.word_count) * 100
        except ZeroDivisionError:
            return 0.0

    def flesch_douma(self) -> int:
        """
        The Flesch-Douma readability formula, based upon the Flesch Reading Ease formula.
        Its variables are w/sen (average sentence length) and syl/w (average word length).

        :return: An integer score generated on a text by the Flesch-Douma formula.
        """
        try:
            return int(206.84 - (0.93 * (self.word_count / self.sentence_count))
                       - (77 * (self.syllable_count / self.word_count)))
        except ZeroDivisionError:
            return 0

    def leesindex_a(self) -> int:
        """
        The Leesindex A readability formula, based upon the Flesch Reading Ease formula.
        Its variables are w/sen (average sentence length) and syl/w (average word length).

        :return: An integer score generated on a text by the Leesindex A formula.
        """
        try:
            return int(195 - (2 * (self.word_count / self.sentence_count))
                       - (66.67 * (self.syllable_count / self.word_count)))
        except ZeroDivisionError:
            return 0

    def clib(self, freq_no_stop: bool = True) -> int:
        """
        The CLIB readability formula (Cito readability index for primary education).
        Its variables are freq77 (percentage of words found in a word list with a cumulative frequency of 77%),
        let/w (average word length), ttr (type-token ratio; percentage of unique words in a text)
        and psw (percentage of sentences in words; sen/w).

        :param freq_no_stop: Boolean indicating if the frequency word list should not include stop words, set to True.
        :return:             An integer score generated on a text by the CLIB formula.
        """
        if freq_no_stop:
            freq77 = self.freq77_no_stop
        else:
            freq77 = self.freq77

        unique_words = set()
        text = self.text.lower()
        text = textstat.remove_punctuation(text)

        for word in text.split():
            unique_words.add(word)

        try:
            return int(46 + (0.474 * freq77) - (6.603 * (self.letter_count / self.word_count))
                       - (0.364 * ((len(unique_words) / self.word_count) * 100))
                       + (1.425 * ((self.sentence_count / self.word_count) * 100)))
        except ZeroDivisionError:
            return 0

    def cilt(self, freq_no_stop: bool = True) -> int:
        """
        The CILT readability formula (Cito readability index technical reading).
        Its variables are freq77 (percentage of words found in a word list with a cumulative frequency of 77%) and
        let/w (average word length).
        The score requires a transformation by subtracting it from 150.

        :param freq_no_stop: Boolean indicating if the frequency word list should not include stop words, set to True.
        :return:             An integer score generated on a text by the CILT formula.
        """
        if freq_no_stop:
            freq77 = self.freq77_no_stop
        else:
            freq77 = self.freq77

        try:
            return int(150 - (114.49 + (0.28 * freq77) - (12.33 * (self.letter_count / self.word_count))))
        except ZeroDivisionError:
            return 0
