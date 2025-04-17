import glob
import os
from pathlib import Path

import pandas as pd

# Define the directory containing the CSV files
country_pairs_dir = Path("./data/country_pairs")
output_file = Path("./data/combined_trade_data.csv")

# Get a list of all CSV files in the directory
csv_files = glob.glob(str(country_pairs_dir / "*.csv"))

print(f"Found {len(csv_files)} CSV files to combine")

# Initialize an empty list to store dataframes
dfs = []

# Read each CSV file and append to the list
for i, file in enumerate(csv_files):
    print(f"Processing file {i+1}/{len(csv_files)}: {os.path.basename(file)}")
    try:
        df = pd.read_csv(file)
        dfs.append(df)
    except Exception as e:
        print(f"Error reading {file}: {e}")

# Combine all dataframes
print("Combining all dataframes...")
combined_df = pd.concat(dfs, ignore_index=True)

# Save the combined dataframe to a new CSV file
print(f"Saving combined data to {output_file}...")
combined_df.to_csv(output_file, index=False)

print(f"Successfully combined {len(csv_files)} files into {output_file}")
print(f"Total rows in combined file: {len(combined_df)}")
