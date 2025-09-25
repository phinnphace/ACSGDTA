"""
ACS Data Cleaning Script
Cleans the circus-like ACS data and creates random samples by income tertile
"""

import pandas as pd
import numpy as np

def clean_acs_data(filepath):
    # Load and transpose the data
    df = pd.read_csv(filepath)
    clean_df = df.T.reset_index()
    clean_df.columns = ['Full_Label', 'Value']

    # Split labels and pivot
    clean_df[['County', 'Metric']] = clean_df['Full_Label'].str.split('!!', expand=True)
    clean_df = clean_df.pivot(index='County', columns='Metric', values='Value').reset_index()

    # Clean up and remove NaN column
    clean_df = clean_df[['County', 'Estimate', 'Margin of Error']]
    clean_df.columns = ['County', 'Income', 'MOE']
    clean_df = clean_df[~clean_df['County'].str.contains('Label|United States')]

    # Convert income to numeric
    clean_df['Income'] = clean_df['Income'].str.replace(',', '').str.replace('±', '')
    clean_df['Income'] = pd.to_numeric(clean_df['Income'], errors='coerce')
    clean_df = clean_df.dropna(subset=['Income'])

    return clean_df

def create_random_sample(clean_df, total_samples=100, random_seed=42):
    # Create tertiles and random sample
    clean_df['Tertile'] = pd.qcut(clean_df['Income'], q=3, labels=['Low', 'Medium', 'High'])

    np.random.seed(random_seed)
    n_low = 33 if (clean_df['Tertile'] == 'Low').sum() >= 33 else (clean_df['Tertile'] == 'Low').sum()
    n_medium = 33 if (clean_df['Tertile'] == 'Medium').sum() >= 33 else (clean_df['Tertile'] == 'Medium').sum()
    n_high = 34 if (clean_df['Tertile'] == 'High').sum() >= 34 else (clean_df['Tertile'] == 'High').sum()

    low_sample = clean_df[clean_df['Tertile'] == 'Low'].sample(n=n_low, random_state=random_seed)
    medium_sample = clean_df[clean_df['Tertile'] == 'Medium'].sample(n=n_medium, random_state=random_seed)
    high_sample = clean_df[clean_df['Tertile'] == 'High'].sample(n=n_high, random_state=random_seed)

    return pd.concat([low_sample, medium_sample, high_sample])

# Example usage
if __name__ == "__main__":
    cleaned_data = clean_acs_data('/Users/phinnmarkson/Desktop/ACS_cleaned_.csv')
    random_sample = create_random_sample(cleaned_data)
    random_sample.to_csv('random_county_sample.csv', index=False)
    print("Done! Saved random_county_sample.csv")

    # Optional: save cleaned data for transparency
    cleaned_data.to_csv('cleaned_income_data.csv', index=False)
    print("Saved cleaned_income_data.csv")

    # Reload merged file to double-check contents
    import os
    merged_path = os.path.expanduser("~/Desktop/acs-data/random_county_sample_edit.csv")
    if os.path.exists(merged_path):
        merged_df = pd.read_csv(merged_path)
        print("Merged sample preview:")
        print(merged_df.head())
    else:
        print("Merged dataset not found at", merged_path)

    # Auto git commit if file exists
    os.system("git add cleaned_income_data.csv")
    os.system("git add random_county_sample.csv")
    os.system('git commit -m "Add income tertile sample and cleaned data export"')
    print("Git commit created (if repo present)")
