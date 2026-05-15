# AST-based-SQL-Evaluation

This repository contains the implementation of an AST-based evaluation pipeline for incorrect SQL queries in text-to-SQL parsing. The algorithm classifies prediction errors by comparing the AST representation of the predicted SQL against the gold SQL, and independently tags gold queries by structural complexity.

This code accompanies the paper:
> **Comparative Study of Text-to-SQL Models of Different Training Paradigm**
> Cong-Kien Nguyen, Manh-Cuong Do, Thanh-Huu Nguyen
> Faculty of Information Technology, University of Science, Ho Chi Minh City, Vietnam

---

## Overview

The pipeline operates in two parallel tracks on each incorrect prediction:

- **Error Classification**: An ordered, short-circuit cascade of AST comparisons between predicted and gold SQL. Each prediction is assigned the first matching error category, which reflects the root cause of failure. Nine error categories are defined: `parse_fail`, `wrong_columns`, `missing_join`, `wrong_tables`, `wrong_set_op_type`, `wrong_set_op_content`, `wrong_order_limit`, `wrong_condition`, and `exec_only`.

- **Complexity Analysis**: Independent structural tagging of gold SQL queries along three orthogonal dimensions: `is_nested` (contains nested subqueries), `has_joins` (contains at least one join condition), and `high_clauses` (total clause count ≥ 5).

---

## Repository Structure

```
.
├── evaluation_spider.py        # Modified Spider evaluation script
├── evaluation_bird_ex.py       # Modified BIRD evaluation script (Execution Accuracy)
├── evaluation_bird_ves.py      # Modified BIRD evaluation script (Valid Efficiency Score)
├── process_sql.py              # Original Spider AST parser (from Spider repo)
├── process_sql_bird.py         # Modified AST parser for BIRD-specific syntax
├── get_token.py                # Parses BIRD incorrect query files into AST representations
├── get_token_gold.py           # Variant of get_token.py for gold SQL only (complexity analysis)
├── analyzed_incorrect.py       # Main analysis script: error classification + complexity tagging
└── analyzed_gold.py            # Complexity-only analysis on gold SQL
```

---

## Requirements

- Python 3.8+
- Dependencies from the original Spider and BIRD evaluation scripts (see links below)
- SQLite3 (standard library, no install needed)

No additional packages are required beyond the original benchmark dependencies.

---

## Usage

The pipeline differs slightly between Spider and BIRD due to differences in how each benchmark's evaluation script outputs results.

### Spider

**Step 1.** Run the modified Spider evaluation script to generate the incorrect query file. Follow the original Spider instructions for setup, using `evaluation_spider.py` in place of the original:

> Original Spider repo: https://github.com/taoyds/spider/tree/master

The script outputs a JSON file containing all incorrect query pairs, including their AST representations, alongside the standard evaluation metrics.

**Step 2.** Run the analysis directly on the output file

---

### BIRD

**Step 1.** Run the modified BIRD evaluation script to generate the incorrect query file. Follow the original BIRD instructions for setup, using `evaluation_bird_ex.py` (for EX) or `evaluation_bird_ves.py` (for VES) in place of the originals:

> Original BIRD repo: https://github.com/AlibabaResearch/DAMO-ConvAI/tree/main/bird

Unlike Spider, the BIRD output does not include AST representations.

**Step 2.** Parse AST representations into the output file (`get_token.py`)

This produces an augmented file with AST representations added to each query pair, ready for analysis.

**Step 3.** Run the analysis (`analyzed_incorrect.py`)

---

### Complexity-only analysis (gold SQL)

To run complexity tagging on gold SQL without requiring incorrect predictions, used the code file `analyzed_gold.py`

For BIRD, use `get_token_gold.py` first to extract gold ASTs before running `analyzed_gold.py`.

---

## Output

Both `analyzed_incorrect.py` and `analyzed_gold.py` print results to stdout in the following format:

**Error classification counts** (analyzed_incorrect.py):
```
parse_fail: N examples
wrong_columns: N examples
missing_join: N examples
wrong_tables: N examples
wrong_set_op_type: N examples
wrong_set_op_content: N examples
wrong_order_limit: N examples
wrong_condition: N examples
exec_only: N examples
```

**Complexity analysis counts** (both scripts):
```
Has Joins (>=1): N examples
High Clauses (>=5): N examples
Nested Queries: N examples
```

---

## A Note on `parse_fail`

The `parse_fail` category denotes queries that could not be parsed into Spider's internal AST representation by the `get_sql()` function in `process_sql.py`. This includes genuinely malformed SQL, but also syntactically valid SQL that uses constructs outside Spider's parser grammar (e.g., `INNER JOIN`, non-standard casing). `parse_fail` should therefore be interpreted as an upper bound on true syntax errors rather than a precise count.

Similarly, the `exec_only` category captures queries that pass all structural AST checks but are still marked incorrect by the official evaluation script. Manual inspection shows that a portion of these are false positives caused by AST surface sensitivity (alias equivalence across joined columns, case normalization differences, whitespace tokenization artifacts). `exec_only` is best understood as an upper bound on residual semantic errors.

---

## Citation

If you use this code in your work, please cite our Github page.

---

## Acknowledgements

The evaluation scripts in this repository are modified from the official Spider and BIRD benchmark repositories. The original AST parsing logic in `process_sql.py` is from the Spider repository by Yu et al. (2018).