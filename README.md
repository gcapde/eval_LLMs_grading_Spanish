# On the effectiveness of LLMs for automatic grading of open-ended questions in Spanish
Repository for the article "On the effectiveness of LLMs for automatic grading of open-ended questions in Spanish" submitted to the International Journal of Artificial Intelligence in Education, Springer.

This work is an extension of the previous work presented at IEEE URUCON 2024: https://ieeexplore.ieee.org/document/10850479/ (repo can be found here: https://github.com/gcapde/eval_llms_edutech_assessment).


The repository includes:

The prompt used to generate the responses corresponding to the different gradings: excellent, acceptable and incorrect (prompt_dataset.txt).
The different prompts tested with several LLMs (prompts_URUCON.txt and inverted_prompts_URUCON.txt).
Configuration file to run the tests with promptfoo (promptfooconfig_URUCON.yml).
Python code used to analyze the experiments results (JSON files from promptfoo) and generate the graphs included in the paper (analysis_results.py and Accuracy.py).
