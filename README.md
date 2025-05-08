# Accession number duplicate record finder

## Description

This Python script is designed to analyze CSV files to identify and extract records that have duplicate accession values in a user-specified column. It performs several pre-processing steps, including checking for CSV headers and trimming leading/trailing whitespace from the target column's values before comparison. The script outputs the identified duplicate records to a new CSV file and provides a summary report in the console.

## Requirements

* Python 3 
* `pandas` library

## Installation

1.  **Python 3**: Ensure Python 3 is installed on your system. You can download it from [python.org](https://www.python.org/).
2.  **pandas**: Install the `pandas` library using pip:
    ```bash
    pip install pandas
    ```

## Usage

To use the script, run it from your terminal, providing the necessary command-line arguments.

### Command Syntax

```bash
$ python3 ./accession_checker.py -i <input_file.csv> -o <output_duplicates.csv> -f "<Field Name>"
```

### Arguments

* -i or --input-file INPUT_FILE
* -o or --output-file OUTPUT_FILE
* -f or --field FIELD

## Output

### 1. Console Output

The script prints status messages, warnings, and errors to the console. Upon completion (or early
exit due to an error), it provides a summary report:

--- Summary Report ---
Input Filename         : source_data.csv
Target Field for Duplicates: Accession Number
Total Records Processed: 1500
Impacted Records (Duplicates Found): 30

*(The exact numbers will vary based on your input data.)*

Other console messages you might see include:
* `Duplicate records based on '<Field Name>' (after trimming) have been saved to '<output_file.csv>'`
* `No duplicate '<Field Name>' values found after trimming spaces.`
* Error messages if issues like "File not found," "Header missing," or "Field not found" occur.

### 2. Output CSV File

A new CSV file (e.g., `duplicate_entries.csv` if specified via the `-o` argument) will be created.
This file will contain:

- The header row from the input file.
- All records (entire rows) from the input file where the value in the specified `FIELD` was found
  to be a duplicate. This includes *all occurrences* of the duplicated values.
- If no duplicates are found, and an output file is still specified, this file will typically be
  created with only the header row.
