import os
import pandas as pd

# Defining the directory where the CSV files are located
directory = '/Users/wiktoria/Documents/master/Master thesis/untitled folder'  # Replacing with the actual path

# Define the output file path
output_file = "tweets_merged.csv"  # Changing the output file name, if needed
# Get the list of CSV files in the directory
csv_files = sorted([file for file in os.listdir(directory) if file.endswith(".csv")])

# Initialize a list to store dataframes
dfs = []

# Loop through the CSV files and append them
for idx, file in enumerate(csv_files):
    file_path = os.path.join(directory, file)
    
    if idx == 0:
        # For the first file, include the header (additonally, specifying an encoding that handles a winder range of characters)
        df = pd.read_csv(file_path, encoding='ISO-8859-1')
    else:
        # For subsequent files, skip the header
        df = pd.read_csv(file_path, header=0, encoding='ISO-8859-1')
    
    dfs.append(df)

# Concatenate all dataframes
merged_df = pd.concat(dfs, ignore_index=True)

# Save the merged dataframe to a new CSV file
merged_df.to_csv(os.path.join(directory, output_file), index=False)

print(f"CSV files merged into {output_file}")
