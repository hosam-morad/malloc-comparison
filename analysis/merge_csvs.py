import pandas as pd
import argparse
import os

def merge_csvs(file1, dir1, file2, dir2, output_file):
    # Extract only the last part of the directory paths
    dir1 = os.path.basename(dir1.rstrip("/"))
    dir2 = os.path.basename(dir2.rstrip("/"))

    # Load the CSV files
    df1 = pd.read_csv(file1)
    df2 = pd.read_csv(file2)

    # Check if the "benchmark" column exists in both DataFrames
    if "benchmark" not in df1.columns:
        raise KeyError(f"'benchmark' column not found in {file1}")
    if "benchmark" not in df2.columns:
        raise KeyError(f"'benchmark' column not found in {file2}")

    # Rename columns dynamically based on directory and original column name
    df1 = df1.rename(columns={col: f"{dir1}-{col}" for col in df1.columns if col != "benchmark"})
    df2 = df2.rename(columns={col: f"{dir2}-{col}" for col in df2.columns if col != "benchmark"})

    # Merge the DataFrames on the "benchmark" column
    merged_df = pd.merge(df1, df2, on="benchmark", how="outer")

    # Save the merged DataFrame to the output file
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    merged_df.to_csv(output_file, index=False)
def main():
    parser = argparse.ArgumentParser(description="Merge two CSV files on the 'benchmark' column.")
    parser.add_argument("file1", help="Path to the first CSV file")
    parser.add_argument("dir1", help="Directory containing the first CSV file")
    parser.add_argument("file2", help="Path to the second CSV file")
    parser.add_argument("dir2", help="Directory containing the second CSV file")
    parser.add_argument("output_file", help="Path to save the merged CSV file")
    args = parser.parse_args()

    merge_csvs(args.file1, args.dir1, args.file2, args.dir2, args.output_file)

if __name__ == "__main__":
    main()