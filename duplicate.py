import pandas as pd

# Load the CSV file into a DataFrame
df = pd.read_csv("/path/to/directory/")

# Drop duplicate tweets (keep the first occurrence)
df_cleaned = df.drop_duplicates(subset=['Text'], keep='first')

# Save the cleaned DataFrame back to a new CSV file
df_cleaned.to_csv("cleaned_tweets_no_duplicates.csv", index=False)

print("Duplicates removed. Cleaned file saved as cleaned_tweets_no_duplicates.csv")
