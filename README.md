# CSV Reader Project

A Python utility that reconciles MemberPress exports against Genius Referrals and produces a CSV you can import into Genius Referrals.

## Installation

```bash
pip install -r requirements.txt
```

## Input Files

Place the following files inside `data/` before running the tool:

1. `memberpress.csv` – export from MemberPress that must include `first_name`, `last_name`, and `email` columns.
2. `genius-referrals.csv` – export from Genius Referrals that must include a `MEMBER_EMAIL` column.

An `example.csv` file in `data/` shows the expected column order for the output that Genius Referrals accepts.

## Usage

```bash
python src/main.py
```

Optional arguments let you point to alternative locations:

```bash
python src/main.py --memberpress ~/exports/mp.csv --genius ~/exports/gr.csv --output ./output/custom.csv
```

Running the script will:

- Read both source CSV files.
- Compare users by email (case-insensitive).
- Log each missing user to the console so you can see who will be added.
- Write the import-ready CSV to `output/missing-memberpress-users.csv` using the same columns as `example.csv`.

If everyone in MemberPress already exists in Genius Referrals, the script prints a confirmation message and skips generating a file.

## Project Structure

- `src/` - Source code
- `data/` - CSV data files
- `tests/` - Unit tests
- `output/` - Generated CSV exports
