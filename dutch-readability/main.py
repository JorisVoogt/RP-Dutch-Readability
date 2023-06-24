import preprocess_data
import readability_estimation
import results

# This shows how to reproduce the research one-to-one.
# The BasiLex-corpus, CELEX dpw.cd file and frequency word list by Schrooten & Vermeer are required
# for full reproducibility, see README.md.
# The BasiLex-corpus path must be set in preprocess_data.py and the CELEX dpw.cd file path must be set
# in syllable_counter.py.

if __name__ == '__main__':
    # Insert path to the frequency word list by Schrooten & Vermeer.
    freq_list_path = "FREQList.csv"

    # Preprocesses both the BasiLex-corpus and the frequency word list.
    # Preprocessing the BasiLex-corpus can take up to five hours.
    preprocess_data.preprocess_dataset("Data/basilex.csv", "Data/dataset.csv")
    preprocess_data.preprocess_frequency_list(freq_list_path, "Data/freq77.csv", "Data/freq77_no_stop_words.csv")

    # Estimates the readability score for each text in the dataset for each readability formula.
    # Takes up to one and a half hour.
    readability_estimation.estimate_texts("Data/dataset.csv", "Data/results.csv")

    # Maps the scores to grades and adds these to the results.
    # Can use the intermediate_results.csv here instead if you do not want to replicate
    # the first couple of steps.
    readability_estimation.scores_to_grades("Data/results.csv")

    # Results:
    # Tables as seen in the appendix of the research.
    results.create_tables("Data/results.csv")

    # Figure plotting absolute error rates as seen in the results section of the research.
    results.create_boxplot_data("Data/results.csv", "Data/boxplot_data.csv")
    results.boxplot_error_rates("Data/boxplot_data.csv")
