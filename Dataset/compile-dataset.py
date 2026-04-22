import pandas as pd
import glob
import os

# Get all csv files in the current directory
all_files = glob.glob("*.csv")

# Create a list to hold the dataframes
df_list = []

for filename in all_files:
    # Read each file
    df = pd.read_csv(filename)
    df_list.append(df)

# Concatenate all files into one
combined_df = pd.concat(df_list, axis=0, ignore_index=True)

# Export to a new CSV
combined_df.to_csv("final-dataset.csv", index=False)

print("All files combined successfully into combined_output.csv")