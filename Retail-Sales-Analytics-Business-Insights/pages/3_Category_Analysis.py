import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Category Analysis",
    page_icon="🛍️",
    layout="wide"
)

# --------------------------------------------------
# PAGE DESIGN
# --------------------------------------------------

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #f5f3ff, #ecfeff);
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
}

div[data-testid="stMetric"] {
    background: white;
    padding: 18px;
    border-radius: 15px;
    border: 1px solid #ddd6fe;
    box-shadow: 0 4px 12px rgba(91, 33, 182, 0.08);
}

div[data-testid="stMetricValue"] {
    color: #6d28d9;
}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

file_path = (
    Path(__file__).parent.parent
    / "data"
    / "cleaned_superstore_sales.csv"
)

if not file_path.exists():
    st.error("Dataset not found. Please run main.py first.")
    st.stop()

df = pd.read_csv(file_path)

# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.title("🛍️ Category Performance Analysis")

st.write(
    "Explore category sales, profit contribution, "
    "and overall business performance."
)

st.markdown("""
<div style="
    background: linear-gradient(120deg, #581c87, #7c3aed, #db2777);
    padding: 25px;
    border-radius: 18px;
    margin-bottom: 20px;
">
    <h2 style="color:white;">Understand Your Product Categories</h2>
    <p style="color:#f5f3ff;">
        Discover your strongest sales categories, compare profitability,
        and find opportunities to improve business performance.
    </p>
</div>
""", unsafe_allow_html=True)

# --------------------------------------------------
# CATEGORY SUMMARY
# --------------------------------------------------

category_summary = (
    df.groupby("Category", as_index=False)
    .agg(
        Sales=("Sales", "sum"),
        Profit=("Profit", "sum"),
        Quantity=("Quantity", "sum")
    )
)

category_summary["Profit Margin (%)"] = (
    category_summary["Profit"]
    / category_summary["Sales"]
    * 100
)

# --------------------------------------------------
# INTERACTIVE CATEGORY FILTER
# --------------------------------------------------

st.subheader("🔎 Explore Categories")

categories = category_summary["Category"].tolist()

selected_categories = st.multiselect(
    "Select categories to compare",
    options=categories,
    default=categories
)

if not selected_categories:
    st.warning("Please select at least one category.")
    st.stop()

filtered_summary = category_summary[
    category_summary["Category"].isin(selected_categories)
].copy()

st.divider()

# --------------------------------------------------
# KPI CARDS
# --------------------------------------------------

total_sales = filtered_summary["Sales"].sum()
total_profit = filtered_summary["Profit"].sum()
total_quantity = filtered_summary["Quantity"].sum()

best_sales_category = filtered_summary.loc[
    filtered_summary["Sales"].idxmax(), "Category"
]

best_profit_category = filtered_summary.loc[
    filtered_summary["Profit"].idxmax(), "Category"
]

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "💰 Total Sales",
    f"${total_sales:,.2f}"
)

col2.metric(
    "📈 Total Profit",
    f"${total_profit:,.2f}"
)

col3.metric(
    "🏆 Top Sales Category",
    best_sales_category
)

col4.metric(
    "💎 Top Profit Category",
    best_profit_category
)

st.divider()

# --------------------------------------------------
# CHART 1: SALES BY CATEGORY
# --------------------------------------------------

st.subheader("📊 1. Sales by Category")

st.caption(
    "Business question: Which category generates the highest sales?"
)

category_colors = {
    "Furniture": "#8b5cf6",
    "Office Supplies": "#14b8a6",
    "Technology": "#f97316"
}

sales_fig = px.bar(
    filtered_summary.sort_values("Sales", ascending=False),
    x="Category",
    y="Sales",
    color="Category",
    color_discrete_map=category_colors,
    text="Sales",
    title="Total Sales Across Product Categories"
)

sales_fig.update_traces(
    texttemplate="$%{text:,.0f}",
    textposition="outside",
    hovertemplate=(
        "<b>%{x}</b><br>"
        "Sales: $%{y:,.2f}<extra></extra>"
    )
)

sales_fig.update_layout(
    height=430,
    showlegend=False,
    xaxis_title="Product Category",
    yaxis_title="Total Sales ($)",
    yaxis=dict(rangemode="tozero"),
    margin=dict(t=75, b=30, l=20, r=30)
)

st.plotly_chart(sales_fig, use_container_width=True)

st.divider()

# --------------------------------------------------
# CHART 2: PROFIT SHARE BY CATEGORY
# --------------------------------------------------

st.subheader("🍩 2. Profit Share by Category")

st.caption(
    "Business question: What percentage of total profit comes "
    "from each category?"
)

profit_fig = px.pie(
    filtered_summary,
    names="Category",
    values="Profit",
    hole=0.58,
    color="Category",
    color_discrete_map=category_colors,
    title="Contribution to Total Profit"
)

profit_fig.update_traces(
    textposition="inside",
    textinfo="label+percent",
    hovertemplate=(
        "<b>%{label}</b><br>"
        "Profit: $%{value:,.2f}<br>"
        "Profit share: %{percent}<extra></extra>"
    )
)

profit_fig.update_layout(
    height=450,
    margin=dict(t=70, b=20, l=20, r=20),
    legend_title_text="Category"
)

st.plotly_chart(profit_fig, use_container_width=True)

st.divider()

# --------------------------------------------------
# CHART 3: SALES VS PROFIT
# --------------------------------------------------

st.subheader("📈 3. Sales vs. Profit by Category")

st.caption(
    "Business question: How do sales and profit compare "
    "for each category?"
)

comparison_data = filtered_summary.melt(
    id_vars="Category",
    value_vars=["Sales", "Profit"],
    var_name="Metric",
    value_name="Amount"
)

comparison_fig = px.bar(
    comparison_data,
    x="Category",
    y="Amount",
    color="Metric",
    barmode="group",
    text="Amount",
    color_discrete_map={
        "Sales": "#6366f1",
        "Profit": "#f59e0b"
    },
    title="Sales and Profit Comparison"
)

comparison_fig.update_traces(
    texttemplate="$%{text:,.0f}",
    textposition="outside",
    cliponaxis=False,
    hovertemplate=(
        "Category: %{x}<br>"
        "Metric: %{fullData.name}<br>"
        "Amount: $%{y:,.2f}<extra></extra>"
    )
)

comparison_fig.update_layout(
    height=480,
    barmode="group",
    xaxis_title="Product Category",
    yaxis_title="Amount ($)",
    yaxis=dict(rangemode="tozero"),
    legend_title_text="Measure",
    margin=dict(t=75, b=30, l=20, r=30)
)

st.plotly_chart(comparison_fig, use_container_width=True)

st.divider()

# --------------------------------------------------
# CATEGORY PERFORMANCE TABLE
# --------------------------------------------------

st.subheader("📋 Category Performance Details")

display_summary = filtered_summary.copy()

display_summary["Sales"] = display_summary["Sales"].round(2)
display_summary["Profit"] = display_summary["Profit"].round(2)
display_summary["Profit Margin (%)"] = (
    display_summary["Profit Margin (%)"].round(2)
)

st.dataframe(
    display_summary,
    use_container_width=True,
    hide_index=True
)

# --------------------------------------------------
# BUSINESS INSIGHTS
# --------------------------------------------------

st.subheader("💡 Business Insights")

st.markdown(f"""
- **Highest sales category:** {best_sales_category}.
- **Highest profit category:** {best_profit_category}.
- **Total sales for selected categories:** ${total_sales:,.2f}.
- **Total profit for selected categories:** ${total_profit:,.2f}.
- **Total quantity sold:** {total_quantity:,} units.
""")

st.info(
    "Remember: a category can generate high sales without generating "
    "the highest profit. Compare both measures when evaluating "
    "business performance."
)
