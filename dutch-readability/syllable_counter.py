import codecs
import textstat
import re
import unicodedata
from typing import Optional

celex_path = "path/to/celex/file/dpw.cd"


def dictionary_init() -> dict[str, int]:
    """
    Reads the CELEX dataset and turns it into a word-syllable count dictionary.

    :return: Dictionary containing Dutch words and their syllable count.
    """
    dictionary = {}

    f = codecs.open(celex_path, encoding='utf-8')
    lines = f.readlines()
    f.close()

    for line in lines:
        fields = line.split("\\")
        word = fields[1]
        syllables = fields[4]
        if syllables == "":
            continue
        syllable_count = len(syllables.split("-"))
        dictionary[word.lower()] = syllable_count

    return dictionary


def split_composite_word(word: str, split: int) -> (str, str):
    """
    Splits a string into two strings at the specified index.

    :param word:  The String that should be split.
    :param split: The index at which the String should be split.
    :return:      The two halves of the split String.
    """
    return word[0:split], word[split:len(word)]


def strip_accents(text: str) -> str:
    """
    Strip the accents from the input text by transforming to ASCII and back to UTF-8.

    :param text: The text given.
    :returns:    The text without accents.
    """
    text = unicodedata.normalize('NFD', text)
    text = text.encode('ascii', 'ignore')
    text = text.decode("utf-8")
    return str(text)


def remove_apostrophes(text: str) -> str:
    """
    Removes apostrophes from a text if these are not between letters, numbers or underscores.

    :param text: The text from which apostrophes not within words should be removed.
    :return:     The text without apostrophes except in words.
    """
    return re.sub(r"(?<!\w)\'(?=\w)|(?<=\w)\'(?!\w)|(?<!\w)\'(?!\w)", '', text)


def remove_punctuation(text: str) -> str:
    """
    Removes all forms of punctuation except apostrophes.

    :param text: The text from which punctuation should be removed.
    :return:     The text without punctuation except apostrophes.
    """
    return re.sub(r"[^\w\s\']", '', text)


def clean_text(text: str) -> str:
    """
    Cleans up text by lowering capital letters, removing accents, apostrophes not inside words and all
    other forms of punctuation.

    :param text: The text which should be cleaned.
    :return:     The cleaned text.
    """
    text = text.lower()
    text = strip_accents(text)
    text = remove_apostrophes(text)
    return remove_punctuation(text)


class SyllableCounter:
    """
    A syllable counter for Dutch words and texts using a dictionary of known Dutch words and their syllables.

    Attribute dictionary: Dictionary containing Dutch words as keys to their syllable counts.
    """

    __dictionary = dictionary_init()

    def __init__(self):
        """
        Sets the language of the used Textstat library to Dutch and sets the accuracy test counters to zero.
        """
        textstat.set_lang("nl")
        self.textstat_count = 0
        self.unknown_count = 0

    def get_dictionary(self) -> dict[str, int]:
        """
        Gets the dictionary attribute.

        :return: Dictionary with Dutch words as key and their syllable counts as value.
        """
        return self.__dictionary

    def composite_word_syllables(self, word: str, original: str, test_accuracy: bool = False) -> Optional[int]:
        """
        Splits the word into possibly multiple words and tries to match these in the class dictionary
        to obtain the amount of syllables of the word.
        test_accuracy is used in test_accuracy_syllable_counter.py to test the accuracy of the
        syllable counter.

        :param word:          The String to be split into possibly multiple Strings in order to count its syllables.
        :param original:      The original String when this method was called for the first time.
        :param test_accuracy: Boolean denoting if the count_syllables_word method is run as an accuracy test.
        :return:              The amount of syllables or None.
        """
        # Split a word while never dealing with a single character.
        for i in range(len(word) - 2, 1, -1):
            word1, word2 = split_composite_word(word, i)

            if word1 in self.__dictionary:
                if word2 in self.__dictionary:
                    # Word could be split into two known words.
                    return self.__dictionary[word1] + self.__dictionary[word2]

                # Checks if splitting the word earlier can give a better split.
                for j in range(len(word1), 1, -1):
                    split1, split2 = split_composite_word(word1, j)
                    split2 += word2

                    if split1 in self.__dictionary and split2 in self.__dictionary:
                        return self.__dictionary[split1] + self.__dictionary[split2]

                # Checks if a plural s in a compound word is part of the second word instead.
                if (word1.endswith("es") or word1.endswith("els") or word1.endswith("ens") or word1.endswith("ers")
                    or word1.endswith("ems") or word1.endswith("ies") or word1.endswith("eaus")) \
                        and word1[0:len(word1) - 1] in self.__dictionary:

                    return self.__dictionary[word1[0:len(word1) - 1]] \
                        + self.count_syllables_word("s" + word2, original, test_accuracy)

                # First part of the compound word is known.
                return self.__dictionary[word1] + self.count_syllables_word(word2, original, test_accuracy)

        # Checks if a connection s in a compound word was added.
        if word[0] == "s" and word != original:
            return self.count_syllables_word(word[1:len(word)], original, test_accuracy)

    def count_syllables_word(self, word: str, original: str, test_accuracy: bool = False) -> int:
        """
        Counts the amount of syllables in a given word String.
        test_accuracy is used in test_accuracy_syllable_counter.py to test the accuracy of the
        syllable counter.

        :param word:          The String for which syllables should be counted.
        :param original:      The original String entered.
        :param test_accuracy: Boolean denoting if this method is run as an accuracy test.
        :return:              The amount of syllables in the word.
        """
        if word in self.__dictionary:
            return self.__dictionary[word]

        # Checks if parts of the compound word are in the class dictionary.
        composite_syllables = self.composite_word_syllables(word, original, test_accuracy)
        if composite_syllables is not None:
            return composite_syllables

        if test_accuracy:
            self.textstat_count += 1
            if word == original:
                self.unknown_count += 1
        # If a word or parts of the word are not in the class dictionary, use Textstat's syllable_count method.
        return textstat.syllable_count(word)

    def count_syllables_text(self, text: str) -> int:
        """
        Counts the amount of syllables in a piece of text String.
        Uses the count_syllables_word method to count syllables for each word in the text.

        :param text: The String for which syllables should be counted
        :return:     The amount of syllables in the text.
        """
        text = clean_text(text)
        syllable_count = 0

        for word in text.split():
            syllable_count += self.count_syllables_word(word, word)

        return syllable_count
