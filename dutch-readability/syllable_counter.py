import codecs
import textstat
import re
import unicodedata
from typing import Optional

celex_path = "path/to/celex/file/dpw.cd"


def dictionary_init() -> dict[str]:
    """
    Reads the CELEX data and turns it into a word-syllable count dictionary.

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
    A class which contains a Dutch words with syllable count dictionary
    which is used to count the amount of syllables in a text.
    """

    def __init__(self):
        """
        Sets the language of the used Textstat library to Dutch and loads in the dictionary file.
        """
        textstat.set_lang("nl")
        self.dictionary = dictionary_init()

    def composite_word_syllables(self, word: str, original: str) -> Optional[int]:
        """
        Splits the word into possibly multiple words and tries to match these in the class dictionary
        to obtain the amount of syllables of the word.

        :param word:     The String to be split into possibly multiple Strings in order to count its syllables.
        :param original: The original String when this method was called for the first time.
        :return:         The amount of syllables or None.
        """
        # Split a word while never dealing with a single character.
        for i in range(len(word) - 2, 1, -1):
            word1, word2 = split_composite_word(word, i)

            if word1 in self.dictionary:
                if word2 in self.dictionary:
                    # Word could be split into two known words.
                    return self.dictionary[word1] + self.dictionary[word2]

                # Checks if splitting the word earlier can give a better split.
                for j in range(len(word1), 1, -1):
                    split1, split2 = split_composite_word(word1, j)
                    split2 += word2

                    if split1 in self.dictionary and split2 in self.dictionary:
                        return self.dictionary[split1] + self.dictionary[split2]

                # Checks if a plural s in a compound word is part of the second word instead.
                if (word1.endswith("es") or word1.endswith("els") or word1.endswith("ens") or word1.endswith("ers")
                    or word1.endswith("ems") or word1.endswith("ies") or word1.endswith("eaus")) \
                        and word1[0:len(word1) - 1] in self.dictionary:

                    return self.dictionary[word1[0:len(word1) - 1]] + self.count_syllables_word("s" + word2, original)

                # First part of the compound word is known.
                return self.dictionary[word1] + self.count_syllables_word(word2, original)

        # Checks if a connection s in a compound word was added.
        if word[0] == "s" and word != original:
            return self.count_syllables_word(word[1:len(word)], original)

    def count_syllables_word(self, word: str, original: str) -> int:
        """
        Counts the amount of syllables in a given word String.

        :param word:     The String for which syllables should be counted.
        :param original: The original String entered.
        :return:         The amount of syllables in the word.
        """
        if word in self.dictionary:
            return self.dictionary[word]

        # Checks if parts of the compound word are in the class dictionary.
        composite_syllables = self.composite_word_syllables(word, original)
        if composite_syllables is not None:
            return composite_syllables

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
