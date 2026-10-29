import streamlit as st
import pandas as pd
from pathlib import Path

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="View Dataset",
    page_icon="📋",
    layout="wide"
)

# --------------------------------------------------
# CUSTOM DESIGN
# --------------------------------------------------

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #f4f7ff, #eaf1ff);
}

.block-container {
    padding-top: 2.5rem !important;
    padding-bottom: 2rem !important;
}

h1 {
    margin-top: 0.2rem !important;
    margin-bottom: 0.4rem !important;
}

h2, h3 {
    margin-top: 0.5rem !important;
    margin-bottom: 0.4rem !important;
}

div[data-testid="stMetric"] {
    background: white;
    border: 1px solid #dbeafe;
    padding: 20px;
    border-radius: 15px;
    box-shadow: 0 4px 12px rgba(30, 64, 175, 0.08);
}

div[data-testid="stMetricValue"] {
    color: #1d4ed8;
}

.section-description {
    color: #64748b;
    margin-top: -8px;
    margin-bottom: 18px;
}

div[data-testid="stAlert"] {
    margin-top: 0.4rem;
    margin-bottom: 0.4rem;
}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# PAGE HEADER
# --------------------------------------------------

st.title("📋 View Dataset")

st.write(
    "Explore, search, filter, and download your retail sales data."
)

st.markdown("""
<div style="
    background: linear-gradient(120deg, #172554, #2563eb, #7c3aed);
    padding: 25px;
    border-radius: 18px;
    color: white;
    margin-bottom: 20px;
">
    <h2 style="color:white; margin-top:0 !important;">
        Explore Your Dataset
    </h2>
    <p style="color:#eef2ff; margin-bottom:0 !important;">
        Switch between the original and cleaned datasets, inspect
        data quality, find specific records, and download your data.
    </p>
</div>
""", unsafe_allow_html=True)

# --------------------------------------------------
# DATASET PATHS
# --------------------------------------------------

DATA_FOLDER = (
    Path(__file__).resolve().parent.parent / "data"
)

ORIGINAL_PATH = DATA_FOLDER / "Superstore_Sales_Data.csv"
CLEANED_PATH = DATA_FOLDER / "cleaned_superstore_sales.csv"

# These columns are intentionally excluded during cleaning.
REMOVED_COLUMNS = ["Row ID", "Postal Code"]

# --------------------------------------------------
# LOAD DATA — HANDLE DIFFERENT CSV ENCODINGS
# --------------------------------------------------

@st.cache_data
def load_dataset(path):
    encodings = [
        "utf-8",
        "utf-8-sig",
        "cp1252",
        "latin1"
    ]

    last_error = None

    for encoding in encodings:
        try:
            return pd.read_csv(path, encoding=encoding)
        except UnicodeDecodeError as error:
            last_error = error

    raise ValueError(
        f"Could not decode the CSV file: {path}. "
        f"Last encoding error: {last_error}"
    )


# --------------------------------------------------
# SELECT DATASET
# --------------------------------------------------

st.divider()
st.subheader("📂 Select Dataset")

dataset_choice = st.radio(
    "Choose which dataset to view:",
    options=["Cleaned Dataset", "Original Dataset"],
    horizontal=True,
    index=0,
    key="dataset_choice"
)

if dataset_choice == "Original Dataset":
    selected_path = ORIGINAL_PATH
    dataset_label = "Original Dataset"
else:
    selected_path = CLEANED_PATH
    dataset_label = "Cleaned Dataset"

# --------------------------------------------------
# CHECK FILE AND LOAD DATA
# --------------------------------------------------

if not selected_path.exists():
    st.error(f"{dataset_label} was not found.")
    st.code(str(selected_path))
    st.info(
        "Make sure both CSV files are inside your project's data folder."
    )
    st.stop()

try:
    df = load_dataset(str(selected_path))

except (ValueError, pd.errors.ParserError) as error:
    st.error(f"Unable to load the dataset: {error}")
    st.stop()

except Exception as error:
    st.error(f"An unexpected error occurred: {error}")
    st.stop()

if df.empty:
    st.warning("The selected dataset contains no rows.")
    st.stop()

st.success(f"Currently viewing: {dataset_label}")

# --------------------------------------------------
# DATASET OVERVIEW
# --------------------------------------------------

st.divider()
st.subheader("📊 Dataset Overview")

total_rows = len(df)
total_columns = len(df.columns)
missing_cells = int(df.isna().sum().sum())

# Count duplicate rows using the columns retained during cleaning.
# Original: exclude Row ID and Postal Code before checking duplicates.
# Cleaned: check all remaining columns.
if dataset_choice == "Original Dataset":
    duplicate_check_df = df.drop(
        columns=REMOVED_COLUMNS,
        errors="ignore"
    )
else:
    duplicate_check_df = df

duplicate_rows = int(
    duplicate_check_df.duplicated().sum()
)

metric1, metric2, metric3, metric4 = st.columns(4)

with metric1:
    st.metric("📄 Total Rows", f"{total_rows:,}")

with metric2:
    st.metric("📊 Total Columns", f"{total_columns:,}")

with metric3:
    st.metric("⚠️ Missing Cells", f"{missing_cells:,}")

with metric4:
    st.metric("🔁 Duplicate Rows", f"{duplicate_rows:,}")

if dataset_choice == "Original Dataset":
    st.caption(
        "Duplicate rows are checked after excluding Row ID and Postal Code, "
        "to match the columns retained during cleaning."
    )
else:
    st.caption(
        "Duplicate rows are checked across all columns in the cleaned dataset."
    )

# --------------------------------------------------
# FILTER DATASET
# --------------------------------------------------

st.divider()
st.subheader("🎛️ Filter Dataset")

filtered_df = df.copy()
filter_columns = st.columns(3)

# Region filter
if "Region" in filtered_df.columns:
    with filter_columns[0]:
        region_values = sorted(
            filtered_df["Region"].dropna().astype(str).unique().tolist()
        )

        selected_region = st.selectbox(
            "Select Region",
            options=["All"] + region_values,
            key="view_dataset_region"
        )

    if selected_region != "All":
        filtered_df = filtered_df[
            filtered_df["Region"].astype(str) == selected_region
        ]

# State filter
if "State" in filtered_df.columns:
    with filter_columns[1]:
        state_values = sorted(
            filtered_df["State"].dropna().astype(str).unique().tolist()
        )

        selected_state = st.selectbox(
            "Select State",
            options=["All"] + state_values,
            key="view_dataset_state"
        )

    if selected_state != "All":
        filtered_df = filtered_df[
            filtered_df["State"].astype(str) == selected_state
        ]

# Category filter
if "Category" in filtered_df.columns:
    with filter_columns[2]:
        category_values = sorted(
            filtered_df["Category"].dropna().astype(str).unique().tolist()
        )

        selected_category = st.selectbox(
            "Select Category",
            options=["All"] + category_values,
            key="view_dataset_category"
        )

    if selected_category != "All":
        filtered_df = filtered_df[
            filtered_df["Category"].astype(str) == selected_category
        ]

# --------------------------------------------------
# SEARCH DATASET
# --------------------------------------------------

st.divider()
st.subheader("🔎 Search Dataset")

search_term = st.text_input(
    "Search across all columns",
    placeholder=(
        "Enter a city, state, product name, "
        "order ID, or keyword..."
    ),
    key="view_dataset_search"
)

if search_term.strip():
    search_mask = filtered_df.astype(str).apply(
        lambda column: column.str.contains(
            search_term.strip(),
            case=False,
            na=False,
            regex=False
        )
    ).any(axis=1)

    filtered_df = filtered_df[search_mask]

# --------------------------------------------------
# DISPLAY DATASET
# --------------------------------------------------

st.divider()
st.subheader("📑 Dataset Records")

st.markdown(
    '<p class="section-description">'
    'The table reflects your selected dataset, filters, and search.'
    '</p>',
    unsafe_allow_html=True
)

st.write(f"**Showing {len(filtered_df):,} of {len(df):,} rows**")

if filtered_df.empty:
    st.warning(
        "No records match your filters or search. "
        "Try changing your selections."
    )
else:
    st.dataframe(
        filtered_df,
        width="stretch",
        hide_index=True,
        height=500
    )

# --------------------------------------------------
# DOWNLOAD DATASET
# --------------------------------------------------

st.divider()
st.subheader("⬇️ Download Dataset")

st.write(
    "Download the filtered records or the complete selected dataset."
)

download_option = st.radio(
    "Choose download content:",
    options=["Filtered Data", "Complete Selected Dataset"],
    horizontal=True,
    key="dataset_download_option"
)

if download_option == "Filtered Data":
    download_df = filtered_df
    filename_prefix = "filtered"
else:
    download_df = df
    filename_prefix = "complete"

csv_data = download_df.to_csv(index=False).encode("utf-8-sig")

download_filename = (
    f"{filename_prefix}_"
    f"{dataset_choice.lower().replace(' ', '_')}.csv"
)

st.download_button(
    label="📥 Download CSV",
    data=csv_data,
    file_name=download_filename,
    mime="text/csv"
)

# --------------------------------------------------
# DATA QUALITY SUMMARY
# --------------------------------------------------

st.divider()
st.subheader("🧹 Data Quality Summary")

quality_df = pd.DataFrame({
    "Column": df.columns,
    "Data Type": [
        str(df[column].dtype) for column in df.columns
    ],
    "Missing Values": [
        int(df[column].isna().sum()) for column in df.columns
    ],
    "Missing (%)": [
        round(df[column].isna().mean() * 100, 2)
        for column in df.columns
    ],
    "Unique Values": [
        int(df[column].nunique(dropna=True))
        for column in df.columns
    ]
})

st.dataframe(
    quality_df,
    width="stretch",
    hide_index=True
)

st.caption(
    "The data quality summary describes the complete selected dataset, "
    "not only the filtered records."
)

# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.info(
    "💡 Switching datasets changes what you see on this page. "
    "It does not overwrite or modify either CSV file."
)
