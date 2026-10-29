import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Regional Sales Analysis",
    page_icon="🌍",
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

div[data-testid="stMarkdownContainer"] ul {
    margin-top: 0.2rem !important;
    margin-bottom: 0.4rem !important;
}

div[data-testid="stMarkdownContainer"] li {
    margin-bottom: 0.15rem !important;
}

div[data-testid="stAlert"] {
    margin-top: 0.4rem;
    margin-bottom: 0.4rem;
}

hr {
    margin-top: 0.8rem !important;
    margin-bottom: 0.8rem !important;
}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# LOAD DATASET
# --------------------------------------------------

file_path = (
    Path(__file__).parent.parent
    / "data"
    / "cleaned_superstore_sales.csv"
)

if not file_path.exists():
    st.error(
        "Cleaned dataset not found. "
        "Please run main.py first."
    )
    st.stop()

df = pd.read_csv(file_path)

required_columns = [
    "Region",
    "Sales",
    "Profit",
    "Order ID",
    "Quantity"
]

missing_columns = [
    column for column in required_columns
    if column not in df.columns
]

if missing_columns:
    st.error(
        f"Missing required columns: {', '.join(missing_columns)}"
    )
    st.stop()

# --------------------------------------------------
# DATA CLEANING
# --------------------------------------------------

df["Sales"] = pd.to_numeric(
    df["Sales"], errors="coerce"
)

df["Profit"] = pd.to_numeric(
    df["Profit"], errors="coerce"
)

df["Quantity"] = pd.to_numeric(
    df["Quantity"], errors="coerce"
)

df["Region"] = (
    df["Region"]
    .astype("string")
    .str.strip()
)

df = df.dropna(
    subset=["Region", "Sales", "Profit"]
).copy()

df = df[df["Region"] != ""]

if df.empty:
    st.error("No valid regional sales records were found.")
    st.stop()

# --------------------------------------------------
# PAGE HEADER
# --------------------------------------------------

st.title("🌍 Regional Sales Analysis")

st.write(
    "Explore sales and profitability across different regions."
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
        Discover Regional Performance
    </h2>
    <p style="color:#eef2ff; margin-bottom:0 !important;">
        Compare regional sales, understand profit contribution,
        and identify the strongest and weakest-performing regions.
    </p>
</div>
""", unsafe_allow_html=True)

# --------------------------------------------------
# REGION SELECTOR
# --------------------------------------------------

available_regions = sorted(
    df["Region"].unique().tolist()
)

selected_regions = st.multiselect(
    "🌎 Choose Regions to Analyze",
    options=available_regions,
    default=available_regions
)

if not selected_regions:
    st.warning("Please select at least one region to continue.")
    st.stop()

region_df = df[
    df["Region"].isin(selected_regions)
].copy()

if region_df.empty:
    st.warning("No data is available for the selected regions.")
    st.stop()

# --------------------------------------------------
# REGIONAL SUMMARY
# --------------------------------------------------

regional_summary = (
    region_df.groupby("Region")
    .agg(
        Sales=("Sales", "sum"),
        Profit=("Profit", "sum"),
        Quantity=("Quantity", "sum"),
        Orders=("Order ID", "nunique")
    )
    .reset_index()
    .sort_values("Sales", ascending=False)
)

regional_summary["Profit Margin (%)"] = (
    regional_summary["Profit"]
    .div(regional_summary["Sales"].replace(0, float("nan")))
    .mul(100)
    .fillna(0)
)

total_sales = region_df["Sales"].sum()
total_profit = region_df["Profit"].sum()
total_orders = region_df["Order ID"].nunique()
total_quantity = region_df["Quantity"].sum()

best_region_row = regional_summary.loc[
    regional_summary["Sales"].idxmax()
]

best_region = best_region_row["Region"]

best_profit_region = regional_summary.loc[
    regional_summary["Profit"].idxmax(),
    "Region"
]

lowest_profit_region = regional_summary.loc[
    regional_summary["Profit"].idxmin(),
    "Region"
]

overall_profit_margin = (
    (total_profit / total_sales) * 100
    if total_sales != 0
    else 0
)

# --------------------------------------------------
# KPI CARDS
# --------------------------------------------------

st.subheader("📊 Regional Overview")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "💰 Total Sales",
    f"${total_sales:,.2f}"
)

col2.metric(
    "💵 Total Profit",
    f"${total_profit:,.2f}"
)

col3.metric(
    "🏆 Top Sales Region",
    str(best_region)
)

col4.metric(
    "📈 Profit Margin",
    f"{overall_profit_margin:.2f}%"
)

st.divider()

# --------------------------------------------------
# CHART 1: REGIONAL SALES COMPARISON
# --------------------------------------------------

st.subheader("🌈 Regional Sales Comparison")

st.caption(
    "Compare total sales across the selected regions."
)

region_colors = {
    "West": "#6366f1",
    "East": "#ec4899",
    "Central": "#14b8a6",
    "South": "#f59e0b"
}

sales_fig = px.bar(
    regional_summary,
    x="Region",
    y="Sales",
    color="Region",
    color_discrete_map=region_colors,
    text="Sales",
    category_orders={
        "Region": regional_summary["Region"].tolist()
    }
)

sales_fig.update_traces(
    texttemplate="$%{text:,.0f}",
    textposition="outside",
    cliponaxis=False,
    hovertemplate=(
        "<b>Region:</b> %{x}<br>"
        "<b>Total Sales:</b> $%{y:,.2f}"
        "<extra></extra>"
    )
)

sales_fig.update_layout(
    showlegend=False,
    height=430,
    plot_bgcolor="rgba(255,255,255,0.85)",
    paper_bgcolor="rgba(255,255,255,0)",
    font=dict(family="Arial", color="#334155"),
    xaxis_title="Region",
    yaxis_title="Sales ($)",
    yaxis=dict(
        tickprefix="$",
        tickformat=",.0f",
        gridcolor="#e2e8f0",
        rangemode="tozero"
    ),
    margin=dict(l=20, r=20, t=30, b=20)
)

st.plotly_chart(
    sales_fig,
    use_container_width=True
)

st.divider()

# --------------------------------------------------
# CHART 2: REGIONAL PROFIT ANALYSIS
# --------------------------------------------------

st.subheader("💵 Regional Profit Analysis")

st.caption(
    "Compare regional profits and identify regions "
    "with the strongest and weakest profitability."
)

profit_fig = px.bar(
    regional_summary,
    x="Region",
    y="Profit",
    color="Profit",
    color_continuous_scale=["#ef4444", "#fbbf24", "#10b981"],
    text="Profit"
)

profit_fig.update_traces(
    texttemplate="$%{text:,.0f}",
    textposition="outside",
    cliponaxis=False,
    hovertemplate=(
        "<b>Region:</b> %{x}<br>"
        "<b>Total Profit:</b> $%{y:,.2f}"
        "<extra></extra>"
    )
)

profit_fig.add_hline(
    y=0,
    line_dash="dash",
    line_color="#64748b"
)

profit_fig.update_layout(
    showlegend=False,
    height=430,
    plot_bgcolor="rgba(255,255,255,0.85)",
    paper_bgcolor="rgba(255,255,255,0)",
    font=dict(family="Arial", color="#334155"),
    xaxis_title="Region",
    yaxis_title="Profit ($)",
    yaxis=dict(
        tickprefix="$",
        tickformat=",.0f",
        gridcolor="#e2e8f0",
        zeroline=True
    ),
    coloraxis_showscale=False,
    margin=dict(l=20, r=20, t=30, b=20)
)

st.plotly_chart(
    profit_fig,
    use_container_width=True
)

st.divider()

# --------------------------------------------------
# CHART 3: REGIONAL SALES CONTRIBUTION
# --------------------------------------------------

st.subheader("🍩 Regional Sales Contribution")

st.caption(
    "Understand the percentage of total selected-region sales "
    "contributed by each region."
)

share_data = regional_summary[
    regional_summary["Sales"] > 0
].copy()

if not share_data.empty:

    donut_fig = px.pie(
        share_data,
        names="Region",
        values="Sales",
        hole=0.55,
        color="Region",
        color_discrete_map=region_colors
    )

    donut_fig.update_traces(
        textposition="inside",
        textinfo="percent",
        hovertemplate=(
            "<b>Region:</b> %{label}<br>"
            "<b>Sales:</b> $%{value:,.2f}<br>"
            "<b>Share:</b> %{percent}"
            "<extra></extra>"
        )
    )

    donut_fig.update_layout(
        height=450,
        paper_bgcolor="rgba(255,255,255,0)",
        font=dict(family="Arial", color="#334155"),
        legend_title_text="Region",
        margin=dict(l=20, r=20, t=30, b=20)
    )

    st.plotly_chart(
        donut_fig,
        use_container_width=True
    )

else:
    st.info("There are no positive sales values to display.")

st.divider()

# --------------------------------------------------
# REGIONAL SALES TABLE
# --------------------------------------------------

st.subheader("📋 Regional Sales Details")

regional_table = regional_summary[
    [
        "Region",
        "Sales",
        "Profit",
        "Orders",
        "Quantity",
        "Profit Margin (%)"
    ]
].copy()

regional_table = regional_table.rename(
    columns={
        "Sales": "Total Sales ($)",
        "Profit": "Total Profit ($)",
        "Orders": "Unique Orders",
        "Quantity": "Quantity Sold"
    }
)

regional_table["Total Sales ($)"] = (
    regional_table["Total Sales ($)"].round(2)
)

regional_table["Total Profit ($)"] = (
    regional_table["Total Profit ($)"].round(2)
)

regional_table["Profit Margin (%)"] = (
    regional_table["Profit Margin (%)"].round(2)
)

st.dataframe(
    regional_table,
    use_container_width=True,
    hide_index=True
)

# --------------------------------------------------
# BUSINESS INSIGHTS
# --------------------------------------------------

st.divider()

st.subheader("💡 Business Insights")

st.markdown(f"""
- 🌍 **Regions selected:** {len(selected_regions)}
- 💰 **Total sales:** ${total_sales:,.2f}
- 💵 **Total profit:** ${total_profit:,.2f}
- 🛒 **Total unique orders:** {total_orders:,}
- 📦 **Total quantity sold:** {total_quantity:,.0f}
- 🏆 **Highest sales region:** {best_region}
- 📈 **Most profitable region:** {best_profit_region}
- 📉 **Lowest profit region:** {lowest_profit_region}
- 📊 **Overall profit margin:** {overall_profit_margin:.2f}%
""")

st.info(
    "💡 Use the region selector at the top to choose which regions "
    "to compare. The KPI cards, all three charts, the table, "
    "and Business Insights will update automatically."
)
