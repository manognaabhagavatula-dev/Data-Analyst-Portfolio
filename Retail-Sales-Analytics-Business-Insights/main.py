import pandas as pd
from pathlib import Path

# ============================================================
# 1. DEFINE FILE PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data"

INPUT_FILE = DATA_DIR / "Superstore_Sales_Data.csv"
OUTPUT_FILE = DATA_DIR / "cleaned_superstore_sales.csv"


# ============================================================
# 2. LOAD THE ORIGINAL DATASET
# ============================================================

print("\n" + "=" * 60)
print("STEP 1: LOAD ORIGINAL DATASET")
print("=" * 60)

if not INPUT_FILE.exists():
    raise FileNotFoundError(
        f"Original dataset not found:\n{INPUT_FILE}\n\n"
        "Please check that Superstore_Sales_Data.csv "
        "exists inside the data folder."
    )

df = pd.read_csv(INPUT_FILE, encoding="cp1252")

print("Dataset loaded successfully.")
print(f"Original rows: {df.shape[0]:,}")
print(f"Original columns: {df.shape[1]}")


# ============================================================
# 3. INSPECT THE ORIGINAL DATASET
# ============================================================

print("\n" + "=" * 60)
print("STEP 2: INSPECT DATASET")
print("=" * 60)

print("\nFirst five rows:")
print(df.head())

print("\nColumn names:")
print(df.columns.tolist())

print("\nData types:")
print(df.dtypes)

print("\nDataset information:")
df.info()

print("\nSummary statistics:")
print(df.describe(include="all"))

print("\nUnique values per column:")
print(df.nunique())

print("\nMissing values per column:")
missing_values = df.isnull().sum()
print(missing_values[missing_values > 0])

print(
    "\nTotal missing cells:",
    int(df.isnull().sum().sum())
)

print(
    "Exact duplicate rows before cleaning:",
    int(df.duplicated().sum())
)


# ============================================================
# 4. CLEAN COLUMN NAMES
# ============================================================

print("\n" + "=" * 60)
print("STEP 3: CLEAN COLUMN NAMES")
print("=" * 60)

df.columns = df.columns.str.strip()

print("Column names cleaned.")
print(df.columns.tolist())


# ============================================================
# 5. CONVERT DATE COLUMNS
# ============================================================

print("\n" + "=" * 60)
print("STEP 4: CONVERT DATE COLUMNS")
print("=" * 60)

date_columns = ["Order Date", "Ship Date"]

for col in date_columns:
    if col in df.columns:
        df[col] = pd.to_datetime(
            df[col],
            errors="coerce"
        )

        print(f"{col}: {df[col].dtype}")

print("\nMissing dates after conversion:")

for col in date_columns:
    if col in df.columns:
        print(
            f"{col}: {int(df[col].isna().sum())}"
        )


# ============================================================
# 6. REMOVE EXACT DUPLICATE ROWS
# ============================================================

print("\n" + "=" * 60)
print("STEP 5: REMOVE EXACT DUPLICATES")
print("=" * 60)

rows_before = len(df)
duplicates_before = int(df.duplicated().sum())

print(f"Rows before cleaning: {rows_before:,}")
print(f"Exact duplicates found: {duplicates_before:,}")

# Remove rows that are identical across all columns.
# Keep the first occurrence of each row.
df = df.drop_duplicates(keep="first").copy()

rows_after = len(df)
duplicates_removed = rows_before - rows_after

print(f"Duplicate rows removed: {duplicates_removed:,}")
print(f"Rows after cleaning: {rows_after:,}")
print(
    "Remaining exact duplicates:",
    int(df.duplicated().sum())
)

if df.duplicated().any():
    raise ValueError(
        "Duplicate removal failed. Exact duplicates remain."
    )


# ============================================================
# 7. REMOVE UNNECESSARY COLUMNS
# ============================================================

print("\n" + "=" * 60)
print("STEP 6: REMOVE UNNECESSARY COLUMNS")
print("=" * 60)

columns_to_remove = ["Row ID", "Postal Code"]

existing_columns = [
    col for col in columns_to_remove
    if col in df.columns
]

df = df.drop(columns=existing_columns).copy()

print("Removed columns:", existing_columns)
print("Remaining columns:", df.columns.tolist())
print(f"Current rows: {df.shape[0]:,}")
print(f"Current columns: {df.shape[1]}")


# ============================================================
# 8. CHECK MISSING VALUES
# ============================================================

print("\n" + "=" * 60)
print("STEP 7: CHECK MISSING VALUES")
print("=" * 60)

missing_by_column = df.isnull().sum()
missing_by_column = missing_by_column[
    missing_by_column > 0
]

if missing_by_column.empty:
    print("No missing values found.")
else:
    print("Columns with missing values:")
    print(missing_by_column)

print(
    "Total missing cells:",
    int(df.isnull().sum().sum())
)

# Missing values are reported, not automatically deleted.
# This avoids accidentally removing valid sales records.


# ============================================================
# 9. VALIDATE NUMERICAL VALUES
# ============================================================

print("\n" + "=" * 60)
print("STEP 8: VALIDATE NUMERICAL VALUES")
print("=" * 60)

numerical_columns = [
    "Sales",
    "Quantity",
    "Discount",
    "Profit"
]

for col in numerical_columns:

    if col not in df.columns:
        continue

    print(f"\n{col}:")

    print(
        "Negative values:",
        int((df[col] < 0).sum())
    )

    print(
        "Zero values:",
        int((df[col] == 0).sum())
    )

if "Discount" in df.columns:
    print(
        "\nDiscount values greater than 1:",
        int((df["Discount"] > 1).sum())
    )


# ============================================================
# 10. VALIDATE ORDER AND SHIPPING DATES
# ============================================================

print("\n" + "=" * 60)
print("STEP 9: VALIDATE DATES")
print("=" * 60)

if "Order Date" in df.columns:
    print(
        "Missing order dates:",
        int(df["Order Date"].isna().sum())
    )

if "Ship Date" in df.columns:
    print(
        "Missing shipping dates:",
        int(df["Ship Date"].isna().sum())
    )

if (
    "Order Date" in df.columns
    and "Ship Date" in df.columns
):
    orders_after_shipping = (
        df["Order Date"] > df["Ship Date"]
    )

    print(
        "Orders placed after shipping:",
        int(orders_after_shipping.sum())
    )


# ============================================================
# 11. VALIDATE CATEGORICAL VALUES
# ============================================================

print("\n" + "=" * 60)
print("STEP 10: VALIDATE CATEGORICAL VALUES")
print("=" * 60)

categorical_columns = [
    "Ship Mode",
    "Segment",
    "Country",
    "Region",
    "Category",
    "Sub-Category"
]

for col in categorical_columns:

    if col not in df.columns:
        continue

    print(f"\n{col}")
    print("Unique values:", df[col].nunique())
    print(sorted(df[col].dropna().unique()))


# ============================================================
# 12. VALIDATE DATA TYPES
# ============================================================

print("\n" + "=" * 60)
print("STEP 11: VALIDATE DATA TYPES")
print("=" * 60)

expected_types = {
    "Order Date": "datetime",
    "Ship Date": "datetime",
    "Sales": "numeric",
    "Quantity": "numeric",
    "Discount": "numeric",
    "Profit": "numeric"
}

for col, expected_type in expected_types.items():

    if col not in df.columns:
        continue

    if expected_type == "datetime":
        valid = pd.api.types.is_datetime64_any_dtype(
            df[col]
        )
    else:
        valid = pd.api.types.is_numeric_dtype(
            df[col]
        )

    print(
        f"{col}: {df[col].dtype} | Valid: {valid}"
    )


# ============================================================
# 13. SAVE THE CLEANED DATASET
# ============================================================

print("\n" + "=" * 60)
print("STEP 13: SAVE CLEANED DATASET")
print("=" * 60)

DATA_DIR.mkdir(parents=True, exist_ok=True)

# Check for exact duplicates immediately before saving.
duplicates_before_save = int(df.duplicated().sum())

print(
    "Exact duplicates before saving:",
    duplicates_before_save
)

if duplicates_before_save > 0:
    print("\nInspecting duplicate rows:")
    print(df[df.duplicated(keep=False)])

    df = df.drop_duplicates(keep="first").copy()

    print(
        "Duplicates after removal:",
        int(df.duplicated().sum())
    )

# Save the cleaned DataFrame.
df.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8"
)

print("\nCleaned dataset saved successfully.")
print(f"File location: {OUTPUT_FILE}")
print(f"Rows saved: {len(df):,}")
print(f"Columns saved: {df.shape[1]}")


# ============================================================
# 14. VERIFY THE SAVED DATASET
# ============================================================

print("\n" + "=" * 60)
print("STEP 14: VERIFY SAVED DATASET")
print("=" * 60)

saved_df = pd.read_csv(
    OUTPUT_FILE,
    encoding="utf-8"
)

saved_duplicates = int(saved_df.duplicated().sum())

print(f"Verified rows: {saved_df.shape[0]:,}")
print(f"Verified columns: {saved_df.shape[1]}")
print(f"Exact duplicate rows: {saved_duplicates}")

if saved_duplicates == 0:
    print("\nSUCCESS: Saved dataset contains zero exact duplicates.")
else:
    print("\nWARNING: Duplicate rows remain in the saved dataset.")

print("\nData cleaning and saving completed.")
