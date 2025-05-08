#!/usr/bin/env python3

import pandas as pd
import argparse
import csv # For CSV sniffing

def find_duplicate_records(input_file, output_file, field_name):
    """
    Reads a CSV file, checks for headers, trims leading/trailing spaces
    from the specified field, identifies records with non-unique values
    in that field, saves these records to a new CSV file, and prints a
    summary report.

    Args:
        input_file (str): Path to the input CSV file.
        output_file (str): Path to save the CSV file with duplicate records.
        field_name (str): The name of the column to check for duplicates.
    """
    # 1) Check if the CSV has headers
    try:
        with open(input_file, 'r', newline='', encoding='utf-8') as f:
            sample = f.read(2048) # Read a sample for sniffing
            f.seek(0) # Reset file pointer
            sniffer = csv.Sniffer()
            if not sample: # Handle empty file before sniffing
                 print(f"Error: Input file '{input_file}' is empty.")
                 print("\n--- Summary Report ---")
                 print(f"Input Filename         : {input_file}")
                 print(f"Target Field for Duplicates: {field_name}")
                 print(f"Total Records Processed: 0")
                 print(f"Impacted Records (Duplicates Found): 0")
                 return
            has_header = sniffer.has_header(sample)
            if not has_header:
                print(f"Error: Input file '{input_file}' does not appear to have a header row.")
                print("This script requires a header row to identify the correct column for duplicate checking.")
                print("\n--- Summary Report ---")
                print(f"Input Filename         : {input_file}")
                print(f"Target Field for Duplicates: {field_name}")
                print(f"Total Records Processed: N/A (Header missing)")
                print(f"Impacted Records (Duplicates Found): 0 (Processing aborted)")
                return
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.")
        return
    except csv.Error: # Sniffer might raise csv.Error if it can't determine dialect/header on some files
        print(f"Warning: Could not reliably determine if '{input_file}' has a header using CSV sniffer. Assuming header is present.")
        # Or, you could choose to abort if unsure:
        # print(f"Error: Could not determine if '{input_file}' has a header. Processing aborted.")
        # return
    except Exception as e:
        print(f"An error occurred during header check for '{input_file}': {e}")
        return

    # Proceed to read with pandas, assuming header is present
    try:
        df = pd.read_csv(input_file)
        if df.empty and has_header: # File might just have a header row and no data
             print(f"Warning: Input file '{input_file}' contains only a header or is otherwise empty after header.")
             total_records = 0
             impacted_records = 0
    except pd.errors.EmptyDataError: # This catches files that are completely empty or unreadable as CSV by pandas
        print(f"Error: Input file '{input_file}' is effectively empty or not valid CSV for pandas after header check.")
        total_records = 0
        impacted_records = 0
        # Print a summary report
        print("\n--- Summary Report ---")
        print(f"Input Filename         : {input_file}")
        print(f"Target Field for Duplicates: {field_name}")
        print(f"Total Records Processed: {total_records}")
        print(f"Impacted Records (Duplicates Found): {impacted_records}")
        return
    except Exception as e:
        print(f"An error occurred while reading '{input_file}' with pandas: {e}")
        return

    total_records = len(df)
    if total_records == 0 and not (df.empty and has_header): # Re-check if df is empty but wasn't caught as header-only
        print(f"Warning: Input file '{input_file}' resulted in an empty dataset after reading.")
        impacted_records = 0
        print("\n--- Summary Report ---")
        print(f"Input Filename         : {input_file}")
        print(f"Target Field for Duplicates: {field_name}")
        print(f"Total Records Processed: {total_records}")
        print(f"Impacted Records (Duplicates Found): {impacted_records}")
        return


    # Check if the specified field_name column exists
    if field_name not in df.columns:
        print(f"Error: Column '{field_name}' not found in '{input_file}'.")
        print(f"Available columns are: {df.columns.tolist()}")
        print("\n--- Summary Report ---")
        print(f"Input Filename         : {input_file}")
        print(f"Target Field for Duplicates: {field_name}")
        print(f"Total Records Processed: {total_records}")
        print(f"Impacted Records (Duplicates Found): 0 (Specified field not found)")
        return

    # Trim leading or trailing spaces from the specified field column
    # Ensure the column is treated as string for stripping
    # Create a copy to avoid SettingWithCopyWarning if df is a slice
    df_processed = df.copy()
    if pd.api.types.is_numeric_dtype(df_processed[field_name]) and df_processed[field_name].notna().all():
        df_processed[field_name] = df_processed[field_name].astype(str).str.strip()
    else:
        # Handle potential NaNs by temporarily filling them, stripping, then restoring NaNs
        # This ensures that original NaNs are not converted to the string 'nan' and then stripped.
        original_nans = df_processed[field_name].isna()
        df_processed[field_name] = df_processed[field_name].astype(str).str.strip()
        df_processed.loc[original_nans, field_name] = pd.NA # Use pandas NA for consistency


    # Find duplicates in the specified field_name column after trimming
    duplicates_df = df_processed[df_processed.duplicated(subset=[field_name], keep=False)]
    impacted_records = len(duplicates_df)

    if duplicates_df.empty:
        print(f"No duplicate '{field_name}' values found after trimming spaces.")
    else:
        try:
            duplicates_df.to_csv(output_file, index=False)
            print(f"Duplicate records based on '{field_name}' (after trimming) have been saved to '{output_file}'")
        except Exception as e:
            print(f"An error occurred while writing to '{output_file}': {e}")
            impacted_records = 0

    print("\n--- Summary Report ---")
    print(f"Input Filename         : {input_file}")
    print(f"Target Field for Duplicates: {field_name}")
    print(f"Total Records Processed: {total_records}")
    print(f"Impacted Records (Duplicates Found): {impacted_records}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Find and list records with non-unique values in a specified field from a CSV file. "
                    "Checks for CSV headers and trims leading/trailing spaces from the target field.",
        formatter_class=argparse.RawTextHelpFormatter # For better help text display
    )
    parser.add_argument(
        "-i", "--input-file",
        required=True,
        help="Path to the input CSV file."
    )
    parser.add_argument(
        "-o", "--output-file",
        required=True,
        help="Path to save the output CSV file containing duplicate records."
    )
    parser.add_argument(
        "-f", "--field",
        required=True,
        help="Name of the field (column header) to check for duplicates."
    )

    args = parser.parse_args()
    find_duplicate_records(args.input_file, args.output_file, args.field)
