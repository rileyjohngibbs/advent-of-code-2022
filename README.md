# Advent of Code 2022 Solutions

Written with Python 3.11.0

## Running a solution

```python
python -m solutions day_no input_file [-v version_no] [--timeit] [--debug]
```

Where `day_no` is the day of the month (1-25) and `input_file` is a path to a file containing your puzzle input (or a test input).

The `version_no` is a non-negative integer used to find the solution to run in `__main__.solution_functions`.

## Starting a new solution

```bash
./newday.sh day_name
```

This creates a new module named `day<day_name>.py` (e.g. `day05.py` if `day_name` is `05`), with a single function `alpha` defined in it. This function is added to `__main__.solution_functions` so that it may be run with, e.g., `python -m solutions 5 inputs/day05.txt`.
