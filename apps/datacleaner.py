
import pandas as pd 

df = pd.read_csv("data/final/model_data.csv")

#Drop unwanted columns
df = df.drop(columns=["tradeagreementindex", "maritime_connectivity", "sentiment_index"])

# Create total export column 
bec_cols = [f"bec_{i}" for i in range(1, 9)]
df["total_export_A_to_B"] = df[bec_cols].sum(axis=1)

# Create reversed (B to A) version for import info
import_df = df.copy()

# Rename columns for import side
import_df = import_df.rename(columns={
    "country_a": "country_b",
    "country_b": "country_a",
    "total_export_A_to_B": "total_import_of_A_from_B",
    **{col: f"bec_{col.split('_')[1]}_import_A_from_B" for col in bec_cols}
})

# Merge export and import side on (country_a, country_b, year) 
merged = pd.merge(
    df,
    import_df,
    on=["country_a", "country_b", "year"],
    how="left",
    suffixes=("", "_import"),
    indicator=True
)

# Make sure no missing pairs
missing_pairs = merged[merged["_merge"] == "left_only"][["country_a", "country_b", "year"]]
missing_pairs_list = list(missing_pairs.itertuples(index=False, name=None))

# Drop merge indicator
merged = merged.drop(columns=["_merge"])

# Rename export BEC columns ----
merged = merged.rename(columns={
    col: f"bec_{col.split('_')[1]}_export_A_to_B"
    for col in bec_cols
})

# Compute trade volume ----
merged["trade_volume"] = merged["total_export_A_to_B"] + merged["total_import_of_A_from_B"]

# Reorder
export_cols = [f"bec_{i}_export_A_to_B" for i in range(1, 9)]
import_cols = [f"bec_{i}_import_A_from_B" for i in range(1, 9)]

final_cols = [
    "country_a", "country_b", "year",
    "total_export_A_to_B", "total_import_of_A_from_B", "trade_volume"
] + export_cols + import_cols

merged = merged[[col for col in final_cols if col in merged.columns]]

# random check for symmetry between import and export 
import random

def test_symmetric_values(df):
    print("Running symmetric value tests...\n")
    passed = True
    for _ in range(100): 
        row = df.sample(1).iloc[0]
        a, b, y = row["country_a"], row["country_b"], row["year"]
        mirror_row = df[(df["country_a"] == b) & (df["country_b"] == a) & (df["year"] == y)]
        
        if mirror_row.empty:
            print(f"Missing reverse row for {b} → {a} in {y}")
            continue
        
        mirror_row = mirror_row.iloc[0]

        for i in range(1, 9):
            if row[f"bec_{i}_export_A_to_B"] != mirror_row[f"bec_{i}_import_A_from_B"]:
                print(f"Mismatch in BEC {i} export/import for {a}→{b} and {b}→{a} in {y}")
                passed = False
            if row[f"bec_{i}_import_A_from_B"] != mirror_row[f"bec_{i}_export_A_to_B"]:
                print(f"Mismatch in BEC {i} import/export for {a}→{b} and {b}→{a} in {y}")
                passed = False

        if row["total_export_A_to_B"] != mirror_row["total_import_of_A_from_B"]:
            print(f"Mismatch in total export/import for {a}→{b} and {b}→{a} in {y}")
            passed = False

        if row["total_import_of_A_from_B"] != mirror_row["total_export_A_to_B"]:
            print(f"Mismatch in reverse total export/import for {a}→{b} and {b}→{a} in {y}")
            passed = False

    if passed:
        print("✅ All symmetry checks passed!")
    else:
        print("❌ Some checks failed. See messages above.")

test_symmetric_values(merged)

# ---- Output ----
# merged is your final dataframe
# missing_pairs_list contains all (a, b, year) combinations where reverse data was missing
print(missing_pairs_list)


for col in merged.columns:
    print(col)

merged.to_csv("data/final/historical_data.csv", index=False)
