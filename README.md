# RP-Dutch-Readability

This repository contains the code used in our paper, *Leesbaarheid: An empirical exploration of the applicability of Dutch traditional readability formulas to texts targeting children*. The research is part of the [Research Project 2023 of the TU Delft](https://github.com/TU-Delft-CSE/Research-Project), and this is where our paper can be found.

# Requirements

In order to be able to fully reproduce our experiments, the following requirements must be met.

## Data Sets

- The BasiLex-corpus can be obtained [here](https://taalmaterialen.ivdnt.org/download/tstc-basilex-corpus/) using a non-commercial license.
  Its path to the Data folder should be set in preprocess_data.py.
- The CELEX data set (dpw.cd) used in the syllable counter can be found [here](https://github.com/KBNLresearch/scansion-generator).
  Its path should be set in syllable_counter.py.
- Schrooten & Vermeer's frequency word list can be downloaded from [here](https://annevermeer.github.io/woordwerken.html) (Aflopende-frequentielijst (obv geo gem)).
  Its path can be set in main.py or directly used.

Adaptations of the frequency word list and intermediate results (readability formula scores) can be found under resources and depending on your use case
might prove to be enough.

## Packages

| File | Packages required |
| --- | --- |
| Preprocess Data | nltk, pandas, folia, textstat |
| Syllable Counter | textstat |
| Test Syllable Counter | textstat, pandas |
| Readability Estimation | textstat, spacy, pandas, nltk |
| Results | pandas, matplotlib, seaborn |
| Significance Testing | pandas |

# Usage

The main.py file gives an overview of the main functions used in the research.
The readability formulas are combined in a class for efficiency reasons, and so if you want to run a specific readability formula,
I advise you to copy the formula and required variable calculations to a new file.
