import pandas as pd
import numpy as np

# Set a seed for reproducibility
np.random.seed(42)

# Generating basic data
data = {
    "SaleID": np.arange(1, 200),
    "ProductID": np.random.randint(
        100, 125, size=199
    ),  # Adjusted size to maintain length
    "Quantity": np.random.randint(1, 5, size=199),  # Adjusted size to maintain length
    "Price": np.random.uniform(15, 65, size=199).round(
        2
    ),  # Adjusted size to maintain length
    "SaleDate": pd.date_range(
        start="2024-01-01", periods=199, freq="D"
    ),  # Adjusted size to maintain length
}

df = pd.DataFrame(data)

# Introduce duplicates
duplicates = df.sample(1)  # Adjusted to introduce only 1 duplicate
df = pd.concat([df, duplicates], ignore_index=True)

# Introduce missing values
for col in ["ProductID", "Quantity", "Price"]:
    df.loc[np.random.choice(df.index, 9, replace=False), col] = (
        np.nan
    )  # Adjusted to introduce 9 missing values

# Outliers
df.loc[0:5, "Price"] = [999, 1000, -999, -1000, 123456, -123456]

# Erroneous data types (e.g., numeric fields as strings)
df["ProductID"] = df["ProductID"].apply(lambda x: f"ID_{x}" if not pd.isna(x) else x)

# Text and formatting errors
df["SaleDate"] = df["SaleDate"].apply(
    lambda x: (
        x.strftime("%Y-%m-%d") if np.random.rand() > 0.1 else x.strftime("%d-%m-%Y")
    )
)

# Introduce extra columns randomly
extra_data = np.random.randn(200)
df["ExtraColumn"] = extra_data

# Simulate corrupted data by truncating the file
df = df.head(195)  # Assuming truncation removes last 5 entries

# Save to CSV with some issues in formatting
df.to_csv("data/sales_data_complex_errors.csv", index=False, sep=",", quotechar='"')

# Display some of the dataframe
df.head()
