import textstat
import syllable_counter
import spacy
import pandas as pd
from nltk.corpus import stopwords

nlp = spacy.load("nl_core_news_sm")

freq77_list = "Data/freq77.csv"
freq77_no_stop_list = "Data/freq77_no_stop_words.csv"

stops = set(stopwords.words("dutch"))

flesh_douma_mapping = {range(0, 30): [13], range(30, 45): [11, 12], range(45, 60): [9, 10], range(60, 70): [7, 8],
                       range(70, 80): [6], range(80, 90): [5], range(90, 100): [4]}

leesindex_a_mapping = {range(0, 20): [13], range(20, 35): [11, 12, 13], range(35, 40): [10, 11, 12, 13],
                       range(40, 50): [10, 11], range(50, 55): [8, 9, 10, 11], range(55, 70): [8, 9, 10],
                       range(70, 75): [7, 8, 9, 10], range(75, 80): [7, 8], range(80, 85): [1, 2, 3, 4, 5, 6, 7, 8],
                       range(85, 100): [1, 2, 3, 4, 5, 6]}

clib_mapping = {range(1, 7): [1], range(8, 20): [2], range(21, 35): [3], range(36, 48): [4], range(49, 61): [5],
                range(62, 74): [6], range(75, 87): [7], range(88, 100): [8]}

cilt_mapping = {range(50, 58): [1], range(59, 63): [2], range(64, 67): [3], range(68, 71): [4], range(72, 74): [5],
                range(75, 100): [6, 7, 8]}


def remove_stop_words(text: str) -> str:
    """
    Removes Dutch stop words from the NLTK Python library from a text.

    :param text: A String representing text.
    :return:     The same string without stop words, capitals and punctuation.
    """
    text = text.lower()
    text = textstat.remove_punctuation(text)
    words = [word for word in text if word not in stops]
    return ' '.join(words)


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


def map_score_to_grade(score: int, mapping: dict[range, [int]]) -> list[int]:
    """
    Maps a range of scores to a list (range) of school grade given the mapping.
    For the existing mappings, see top of this module.

    :param score:   An integer representing a score.
    :param mapping: A mapping from a range of scores to a list (range) of school grades.
    :return:        List (range) of school grades as integers or if score is out of range of the mapping,
                    -1 and the out of range score.
    """
    for key in mapping:
        if score in key:
            return mapping[key]
    return [-1, score]


class ReadabilityEstimation:
    """
    Readability estimation class for the Dutch language using four well-known Dutch traditional readability formulas
    and common NLP metrics.

    Attribute syllable_counter: A syllable counter class with a syllable dictionary.
                                Used for counting syllables in a text.
                                See syllable_counter.py for more information.
    """

    __syllable_counter = syllable_counter.SyllableCounter()

    def __init__(self, text: str, maintype: str, subtype: str, grade: str):
        """
        Stores a piece of text, its main- and subtype and grade.
        Using the text, it calculates and stores variables used in multiple Dutch readability formulas.

        :param text:     A piece of text from the BasiLex-corpus.
        :param maintype: The maintype of the text as is found in the BasiLex-corpus.
        :param subtype:  The subtype of the text as is found in the BasiLex-corpus.
        :param grade:    The school grade at which a child should be able to understand the text.
        """
        self.text = text
        self.maintype = maintype
        self.subtype = subtype
        self.grade = grade
        self.sentence_count = textstat.sentence_count(text)
        self.word_count = textstat.lexicon_count(text)
        self.character_count = textstat.char_count(text)
        self.syllable_count = self.__syllable_counter.count_syllables_text(text)
        self.freq77 = self.calculate_freq77(freq77_list, text)
        self.freq77_no_stop = self.calculate_freq77(freq77_no_stop_list, remove_stop_words(text))

    def calculate_freq77(self, file: str, text: str) -> float:
        """
        Calculates the freq77 variable from the CLIB and CILT formulas.
        Uses lemmatization as the frequency word list only contains lemmatized words.

        :param file: A Dutch word list with a cumulative frequency of 77%,
                     i.e. the most frequent words in children's texts. Based upon Schrooten & Vermeer's frequency list.
        :param text: The String on which the freq77 should be calculated.
        :return:     A float signifying the freq77.
        """
        fl = pd.read_csv(file)
        fl = fl["word"].tolist()

        text = text_lemmatizer(text)

        frequent = 0
        for word in text:
            word = word.lower()
            if word in fl:
                frequent += 1
        try:
            return frequent / self.word_count
        except ZeroDivisionError:
            return 0.0

    def flesch_douma(self) -> list[int]:
        """
        The Flesch-Douma readability formula, based upon the Flesch Reading Ease formula.
        Its variables are w/sen (average sentence length) and syl/w (average word length).

        :return: A list of school grades signifying at which grade the text is understandable.
        """
        try:
            score = round(
                          206.84 - (0.93 * (self.word_count / self.sentence_count))
                          - (77 * (self.syllable_count / self.word_count))
                         )
        except ZeroDivisionError:
            score = 0

        return map_score_to_grade(score, flesh_douma_mapping)

    def leesindex_a(self) -> list[int]:
        """
        The Leesindex A readability formula, based upon the Flesch Reading Ease formula.
        Its variables are w/sen (average sentence length) and syl/w (average word length).

        :return: A list of school grades signifying at which grade the text is understandable.
        """
        try:
            score = round(
                          195 - (2 * (self.word_count / self.sentence_count))
                          - (66.67 * (self.syllable_count / self.word_count))
                         )
        except ZeroDivisionError:
            score = 0

        return map_score_to_grade(score, leesindex_a_mapping)

    def clib(self, freq_no_stop: bool = True) -> list[int]:
        """
        The CLIB readability formula (Cito readability index for primary education).
        Its variables are freq77 (percentage of words found in a word list with a cumulative frequency of 77%),
        ch/w (average word length), ttr (type-token ratio; unique words / total amount of words)
        and psw (percentage of sentences in words; sen/w).

        :param freq_no_stop: Boolean indicating if the frequency word list should not include stop words, set to True.
        :return:             A list of school grades signifying at which grade the text is understandable.
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
            score = round(
                          46 + (0.474 * freq77) - (6.603 * (self.character_count / self.word_count))
                          - (0.364 * (len(unique_words) / self.word_count))
                          + (1.425 * (self.sentence_count / self.word_count))
                         )
        except ZeroDivisionError:
            score = 0

        return map_score_to_grade(score, clib_mapping)

    def cilt(self, freq_no_stop: bool = True) -> list[int]:
        """
        The CILT readability formula (Cito readability index technical reading).
        Its variables are freq77 (percentage of words found in a word list with a cumulative frequency of 77%) and
        ch/w (average word length).

        :param freq_no_stop: Boolean indicating if the frequency word list should not include stop words, set to True.
        :return:             A list of school grades signifying at which grade the text is readable, not necessarily
                             understandable.
        """
        if freq_no_stop:
            freq77 = self.freq77_no_stop
        else:
            freq77 = self.freq77

        try:
            score = round(114.49 + (0.28 * freq77) - (12.33 * (self.character_count / self.word_count)))
        except ZeroDivisionError:
            score = 0

        return map_score_to_grade(score, cilt_mapping)
