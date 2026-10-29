import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Monthly Sales Analysis",
    page_icon="📈",
    layout="wide"
)

# --------------------------------------------------
# CUSTOM DESIGN
# --------------------------------------------------

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #f5f3ff, #ecfeff);
}

/* Main page spacing */
.block-container {
    padding-top: 2rem !important;
    padding-bottom: 3rem !important;
}

/* Main heading spacing */
h1 {
    margin-top: 0.2rem !important;
    margin-bottom: 0.4rem !important;
}

/* Subheading spacing */
h2, h3 {
    margin-top: 0.5rem !important;
    margin-bottom: 0.4rem !important;
}

/* KPI cards */
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

/* Reduce unnecessary vertical space around Markdown */
div[data-testid="stMarkdownContainer"] p {
    margin-bottom: 0.35rem;
}

/* Business Insights list spacing */
div[data-testid="stMarkdownContainer"] ul {
    margin-top: 0.2rem !important;
    margin-bottom: 0.4rem !important;
    padding-left: 1.5rem !important;
}

div[data-testid="stMarkdownContainer"] li {
    margin-bottom: 0.15rem !important;
    padding-bottom: 0 !important;
}

/* Keep the information message compact */
div[data-testid="stAlert"] {
    margin-top: 0.4rem;
    margin-bottom: 0.4rem;
}

/* Reduce extra space after dividers */
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
    "Order Date",
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

df["Order Date"] = pd.to_datetime(
    df["Order Date"],
    errors="coerce"
)

df["Sales"] = pd.to_numeric(
    df["Sales"], errors="coerce"
)

df["Profit"] = pd.to_numeric(
    df["Profit"], errors="coerce"
)

df["Quantity"] = pd.to_numeric(
    df["Quantity"], errors="coerce"
)

df = df.dropna(
    subset=["Order Date", "Sales", "Profit"]
).copy()

if df.empty:
    st.error("No valid sales records were found in the dataset.")
    st.stop()

# --------------------------------------------------
# PAGE HEADER
# --------------------------------------------------

st.title("📈 Monthly Sales Analysis")

st.write(
    "Explore monthly sales performance by selecting a year."
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
        Explore Sales by Year
    </h2>
    <p style="color:#eef2ff; margin-bottom:0 !important;">
        Choose a year to view monthly sales performance,
        identify the best-performing month, analyze profits,
        and understand business trends.
    </p>
</div>
""", unsafe_allow_html=True)

# --------------------------------------------------
# YEAR SELECTOR
# --------------------------------------------------

available_years = sorted(
    df["Order Date"].dt.year.unique().astype(int).tolist()
)

if not available_years:
    st.warning("No valid years were found in the dataset.")
    st.stop()

selected_year = st.selectbox(
    "📅 Choose a Year",
    available_years,
    index=len(available_years) - 1
)

year_df = df[
    df["Order Date"].dt.year == selected_year
].copy()

st.divider()

st.subheader(f"📊 Sales Overview — {selected_year}")

# --------------------------------------------------
# MONTHLY SALES AND PROFIT CALCULATIONS
# --------------------------------------------------

year_df["Month_Number"] = year_df["Order Date"].dt.month

month_names = [
    "Jan", "Feb", "Mar", "Apr",
    "May", "Jun", "Jul", "Aug",
    "Sep", "Oct", "Nov", "Dec"
]

monthly_summary = (
    year_df.groupby("Month_Number")
    .agg(
        Sales=("Sales", "sum"),
        Profit=("Profit", "sum")
    )
    .reindex(range(1, 13), fill_value=0)
)

chart_data = pd.DataFrame({
    "Month": month_names,
    "Sales": monthly_summary["Sales"].to_numpy(),
    "Profit": monthly_summary["Profit"].to_numpy()
})

month_colors = {
    "Jan": "#6366f1",
    "Feb": "#ec4899",
    "Mar": "#14b8a6",
    "Apr": "#f59e0b",
    "May": "#8b5cf6",
    "Jun": "#06b6d4",
    "Jul": "#f97316",
    "Aug": "#22c55e",
    "Sep": "#ef4444",
    "Oct": "#3b82f6",
    "Nov": "#a855f7",
    "Dec": "#eab308"
}

# --------------------------------------------------
# KPI CALCULATIONS
# --------------------------------------------------

total_sales = year_df["Sales"].sum()
total_profit = year_df["Profit"].sum()
total_orders = year_df["Order ID"].nunique()
total_quantity = year_df["Quantity"].sum()

active_months = chart_data[chart_data["Sales"] > 0]

if not active_months.empty:

    best_month_row = active_months.loc[
        active_months["Sales"].idxmax()
    ]

    best_month = best_month_row["Month"]

    highest_monthly_sales = float(
        best_month_row["Sales"]
    )

    average_monthly_sales = float(
        active_months["Sales"].mean()
    )

else:
    best_month = "N/A"
    highest_monthly_sales = 0
    average_monthly_sales = 0

# --------------------------------------------------
# KPI CARDS
# --------------------------------------------------

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "💰 Total Sales",
    f"${total_sales:,.2f}"
)

col2.metric(
    "🛒 Total Orders",
    f"{total_orders:,}"
)

col3.metric(
    "🏆 Best Sales Month",
    str(best_month)
)

col4.metric(
    "📈 Highest Monthly Sales",
    f"${highest_monthly_sales:,.2f}"
)

st.divider()

# --------------------------------------------------
# CHART 1: COLOURFUL MONTHLY SALES COMPARISON
# --------------------------------------------------

st.subheader(
    f"🌈 Monthly Sales Comparison — {selected_year}"
)

st.caption(
    "Compare sales across the 12 months and identify "
    "the highest- and lowest-performing months."
)

sales_fig = px.bar(
    chart_data,
    x="Month",
    y="Sales",
    color="Month",
    color_discrete_map=month_colors,
    category_orders={"Month": month_names},
    text="Sales"
)

sales_fig.update_traces(
    texttemplate="$%{text:,.0f}",
    textposition="outside",
    cliponaxis=False,
    hovertemplate=(
        "<b>Month:</b> %{x}<br>"
        "<b>Sales:</b> $%{y:,.2f}"
        "<extra></extra>"
    )
)

sales_fig.update_layout(
    showlegend=False,
    height=450,
    plot_bgcolor="rgba(255,255,255,0.85)",
    paper_bgcolor="rgba(255,255,255,0)",
    font=dict(family="Arial", color="#334155"),
    xaxis_title="Month",
    yaxis_title="Sales ($)",
    xaxis=dict(
        categoryorder="array",
        categoryarray=month_names
    ),
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
# CHART 2: MONTHLY PROFIT ANALYSIS
# --------------------------------------------------

st.subheader(
    f"📊 Monthly Profit Analysis — {selected_year}"
)

st.caption(
    "Identify profitable months and months where the business "
    "recorded a loss. Green indicates positive profit; red indicates loss."
)

profit_colors = [
    "#10b981" if profit >= 0 else "#ef4444"
    for profit in chart_data["Profit"]
]

profit_fig = px.bar(
    chart_data,
    x="Month",
    y="Profit",
    text="Profit",
    category_orders={"Month": month_names}
)

profit_fig.update_traces(
    marker_color=profit_colors,
    texttemplate="$%{text:,.0f}",
    textposition="outside",
    cliponaxis=False,
    hovertemplate=(
        "<b>Month:</b> %{x}<br>"
        "<b>Profit:</b> $%{y:,.2f}"
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
    xaxis_title="Month",
    yaxis_title="Profit ($)",
    xaxis=dict(
        categoryorder="array",
        categoryarray=month_names
    ),
    yaxis=dict(
        tickprefix="$",
        tickformat=",.0f",
        gridcolor="#e2e8f0",
        zeroline=True
    ),
    margin=dict(l=20, r=20, t=30, b=20)
)

st.plotly_chart(
    profit_fig,
    use_container_width=True
)

st.divider()

# --------------------------------------------------
# CHART 3: MONTHLY SALES SHARE
# --------------------------------------------------

st.subheader(
    f"🍩 Monthly Sales Share — {selected_year}"
)

st.caption(
    "Understand how much each month contributes to the year's total sales."
)

share_data = chart_data[
    chart_data["Sales"] > 0
].copy()

if not share_data.empty:

    donut_fig = px.pie(
        share_data,
        names="Month",
        values="Sales",
        hole=0.55,
        color="Month",
        color_discrete_map=month_colors,
        category_orders={"Month": month_names}
    )

    donut_fig.update_traces(
        textposition="inside",
        textinfo="percent",
        hovertemplate=(
            "<b>Month:</b> %{label}<br>"
            "<b>Sales:</b> $%{value:,.2f}<br>"
            "<b>Share:</b> %{percent}"
            "<extra></extra>"
        )
    )

    donut_fig.update_layout(
        height=450,
        paper_bgcolor="rgba(255,255,255,0)",
        font=dict(family="Arial", color="#334155"),
        legend_title_text="Month",
        margin=dict(l=20, r=20, t=30, b=20)
    )

    st.plotly_chart(
        donut_fig,
        use_container_width=True
    )

else:
    st.info("There are no monthly sales values to display.")

st.divider()

# --------------------------------------------------
# MONTHLY SALES TABLE
# --------------------------------------------------

st.subheader("📋 Monthly Sales Details")

monthly_table = pd.DataFrame({
    "Month": month_names,
    "Total Sales ($)": chart_data["Sales"].to_numpy()
})

monthly_table["Total Sales ($)"] = (
    monthly_table["Total Sales ($)"].round(2)
)

st.dataframe(
    monthly_table,
    use_container_width=True,
    hide_index=True
)

# --------------------------------------------------
# BUSINESS INSIGHTS
# --------------------------------------------------

st.divider()

st.subheader("💡 Business Insights")

st.markdown(f"""
- 🗓️ **Selected year:** {selected_year}
- 💰 **Total sales:** ${total_sales:,.2f}
- 💵 **Total profit:** ${total_profit:,.2f}
- 🛒 **Total unique orders:** {total_orders:,}
- 📦 **Total quantity sold:** {total_quantity:,.0f}
- 🏆 **Best-performing sales month:** {best_month}
- 🚀 **Highest monthly sales:** ${highest_monthly_sales:,.2f}
- 📊 **Average sales per active month:** ${average_monthly_sales:,.2f}
""")

st.info(
    "💡 Use the year selector at the top to switch between "
    "the available years. The KPI cards, all three charts, "
    "the table, and the insights will update automatically."
)
