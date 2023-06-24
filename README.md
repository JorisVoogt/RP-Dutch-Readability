# RP-Dutch-Readability

This repository contains the code to reproduce the experiments in our paper, *Leesbaarheid: An empirical exploration of the applicability of Dutch traditional readability formulas to texts targeting children*. The research is part of the [Research Project 2023 of the TU Delft](https://github.com/TU-Delft-CSE/Research-Project), and this is where our paper can be found.

# Requirements

In order to be able to fully reproduce our experiments, the following requirements must be met.

## Data Sets

- The BasiLex-corpus can be obtained [here](https://taalmaterialen.ivdnt.org/download/tstc-basilex-corpus/) using a non-commercial license.
- The CELEX data set (dpw.cd) used in the syllable counter can be found [here](https://github.com/KBNLresearch/scansion-generator).
- Schrooten & Vermeer's frequency word list can be downloaded from [here](https://annevermeer.github.io/woordwerken.html) (Aflopende-frequentielijst (obv geo gem)).

Adaptations of the frequency word list and intermediate results (readability formula scores) can be found under resources and depending on your use case
might prove enough.

## Packages

| File | Packages required |
| --- | --- |
| Preprocess Data | nltk, pandas, folia, textstat |
| Syllable Counter | textstat |
| Test Syllable Counter | textstat, pandas |
| Readability Estimation | textstat, spacy, pandas, nltk |
| Results | pandas, matplotlib, seaborn |
| Significance Testing | pandas |

