# Criteria Parser Training Data
Each line: `{"input": "criterion text", "output": {"rules": [...], "criteria_type": "inclusion|exclusion", "complexity": "simple|compound|conditional"}}`
Expand to 200-300 examples from real ClinicalTrials.gov eligibility criteria. Train on Colab with `train_criteria_parser.ipynb`.
