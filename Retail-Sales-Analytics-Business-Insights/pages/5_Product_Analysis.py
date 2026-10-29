import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Product Analysis",
    page_icon="🏆",
    layout="wide"
)

# --------------------------------------------------
# CUSTOM DESIGN — MATCHES REGIONAL ANALYSIS
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
# PAGE HEADER
# --------------------------------------------------

st.title("🏆 Product Analysis")

st.write(
    "Explore product performance, profitability, and customer segments."
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
        Discover Product Performance
    </h2>
    <p style="color:#eef2ff; margin-bottom:0 !important;">
        Compare product categories, understand customer segments,
        and identify the products generating the highest sales.
    </p>
</div>
""", unsafe_allow_html=True)

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

DATA_PATH = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "cleaned_superstore_sales.csv"
)


@st.cache_data
def load_data(path):
    data = pd.read_csv(path)

    required_columns = [
        "Sales",
        "Profit",
        "Quantity",
        "Order ID",
        "Category",
        "Segment",
        "Product Name"
    ]

    missing_columns = [
        column for column in required_columns
        if column not in data.columns
    ]

    if missing_columns:
        raise ValueError(
            "Missing required columns: "
            + ", ".join(missing_columns)
        )

    for column in ["Sales", "Profit", "Quantity"]:
        data[column] = pd.to_numeric(
            data[column],
            errors="coerce"
        )

    for column in ["Category", "Segment", "Product Name"]:
        data[column] = data[column].astype("string").str.strip()

    data = data.dropna(subset=required_columns)

    return data


try:
    df = load_data(str(DATA_PATH))

except FileNotFoundError:
    st.error(f"Dataset not found: {DATA_PATH}")
    st.stop()

except ValueError as error:
    st.error(str(error))
    st.stop()

except Exception as error:
    st.error(f"Unable to load the dataset: {error}")
    st.stop()

# --------------------------------------------------
# INTERACTIVE FILTERS
# --------------------------------------------------

st.subheader("🎛️ Explore Product Data")

filter1, filter2 = st.columns(2)

with filter1:
    segment_options = ["All"] + sorted(
        df["Segment"].dropna().unique().tolist()
    )

    selected_segment = st.selectbox(
        "Select Customer Segment",
        options=segment_options,
        index=0,
        key="product_segment_filter"
    )

with filter2:
    category_options = ["All"] + sorted(
        df["Category"].dropna().unique().tolist()
    )

    selected_category = st.selectbox(
        "Select Category",
        options=category_options,
        index=0,
        key="product_category_filter"
    )

# --------------------------------------------------
# APPLY FILTERS
# --------------------------------------------------

filtered_df = df.copy()

if selected_segment != "All":
    filtered_df = filtered_df[
        filtered_df["Segment"] == selected_segment
    ]

if selected_category != "All":
    filtered_df = filtered_df[
        filtered_df["Category"] == selected_category
    ]

if filtered_df.empty:
    st.warning(
        "No data matches your selected filters. "
        "Please change your selections."
    )
    st.stop()

# --------------------------------------------------
# KPI CALCULATIONS
# --------------------------------------------------

total_sales = filtered_df["Sales"].sum()
total_profit = filtered_df["Profit"].sum()
total_orders = filtered_df["Order ID"].nunique()
total_quantity = filtered_df["Quantity"].sum()

profit_margin = (
    total_profit / total_sales * 100
    if total_sales != 0 else 0
)

# --------------------------------------------------
# KPI CARDS
# --------------------------------------------------

st.subheader("📊 Product Performance Overview")

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.metric("💰 Total Sales", f"${total_sales:,.2f}")

with kpi2:
    st.metric("📈 Total Profit", f"${total_profit:,.2f}")

with kpi3:
    st.metric("🛒 Total Orders", f"{total_orders:,}")

with kpi4:
    st.metric("📦 Quantity Sold", f"{total_quantity:,.0f}")

st.caption(
    f"Profit margin for selected data: {profit_margin:.2f}%"
)

st.divider()

# --------------------------------------------------
# CATEGORY PERFORMANCE
# --------------------------------------------------

st.subheader("🛍️ Category Performance")

category_summary = (
    filtered_df.groupby("Category", as_index=False)
    .agg(
        Sales=("Sales", "sum"),
        Profit=("Profit", "sum"),
        Quantity=("Quantity", "sum"),
        Orders=("Order ID", "nunique")
    )
)

category_summary["Profit Margin (%)"] = (
    category_summary["Profit"]
    / category_summary["Sales"].replace(0, float("nan"))
    * 100
)

chart1, chart2 = st.columns(2)

with chart1:
    fig_category_sales = px.bar(
        category_summary.sort_values("Sales", ascending=False),
        x="Category",
        y="Sales",
        color="Category",
        title="Sales by Category",
        text_auto=".2s",
        color_discrete_sequence=px.colors.qualitative.Set2
    )

    fig_category_sales.update_layout(
        height=380,
        margin=dict(l=10, r=10, t=60, b=20),
        xaxis_title="",
        yaxis_title="Total Sales ($)",
        showlegend=False
    )

    fig_category_sales.update_yaxes(
        tickprefix="$",
        separatethousands=True
    )

    st.plotly_chart(
        fig_category_sales,
        use_container_width=True
    )

with chart2:
    fig_category_profit = px.bar(
        category_summary.sort_values("Profit", ascending=False),
        x="Category",
        y="Profit",
        color="Category",
        title="Profit by Category",
        text_auto=".2s",
        color_discrete_sequence=px.colors.qualitative.Pastel
    )

    fig_category_profit.update_layout(
        height=380,
        margin=dict(l=10, r=10, t=60, b=20),
        xaxis_title="",
        yaxis_title="Total Profit ($)",
        showlegend=False
    )

    fig_category_profit.update_yaxes(
        tickprefix="$",
        separatethousands=True
    )

    st.plotly_chart(
        fig_category_profit,
        use_container_width=True
    )

st.divider()

# --------------------------------------------------
# CUSTOMER SEGMENT ANALYSIS
# --------------------------------------------------

st.subheader("👥 Customer Segment Analysis")

segment_summary = (
    filtered_df.groupby("Segment", as_index=False)
    .agg(
        Sales=("Sales", "sum"),
        Profit=("Profit", "sum"),
        Quantity=("Quantity", "sum"),
        Orders=("Order ID", "nunique")
    )
)

segment_summary["Profit Margin (%)"] = (
    segment_summary["Profit"]
    / segment_summary["Sales"].replace(0, float("nan"))
    * 100
)

segment_col1, segment_col2 = st.columns(2)

with segment_col1:
    fig_segment_sales = px.pie(
        segment_summary,
        names="Segment",
        values="Sales",
        title="Sales Contribution by Segment",
        hole=0.55,
        color="Segment",
        color_discrete_map={
            "Consumer": "#ec4899",
            "Corporate": "#14b8a6",
            "Home Office": "#6366f1"
        }
    )

    fig_segment_sales.update_traces(
        textposition="inside",
        textinfo="percent+label"
    )

    fig_segment_sales.update_layout(
        height=380,
        margin=dict(l=10, r=10, t=60, b=20)
    )

    st.plotly_chart(
        fig_segment_sales,
        use_container_width=True
    )

with segment_col2:
    fig_segment_profit = px.bar(
        segment_summary.sort_values("Profit", ascending=False),
        x="Segment",
        y="Profit",
        color="Segment",
        title="Profit by Customer Segment",
        text_auto=".2s",
        color_discrete_map={
            "Consumer": "#ec4899",
            "Corporate": "#14b8a6",
            "Home Office": "#6366f1"
        }
    )

    fig_segment_profit.update_layout(
        height=380,
        margin=dict(l=10, r=10, t=60, b=20),
        xaxis_title="",
        yaxis_title="Total Profit ($)",
        showlegend=False
    )

    fig_segment_profit.update_yaxes(
        tickprefix="$",
        separatethousands=True
    )

    st.plotly_chart(
        fig_segment_profit,
        use_container_width=True
    )

st.divider()

# --------------------------------------------------
# TOP 10 PRODUCTS
# --------------------------------------------------

st.subheader("🏆 Top 10 Products by Sales")

product_summary = (
    filtered_df.groupby("Product Name", as_index=False)
    .agg(
        Sales=("Sales", "sum"),
        Profit=("Profit", "sum"),
        Quantity=("Quantity", "sum"),
        Orders=("Order ID", "nunique")
    )
)

product_summary["Profit Margin (%)"] = (
    product_summary["Profit"]
    / product_summary["Sales"].replace(0, float("nan"))
    * 100
)

top_products = product_summary.nlargest(
    10, "Sales"
).sort_values("Sales", ascending=True)

fig_top_products = px.bar(
    top_products,
    x="Sales",
    y="Product Name",
    orientation="h",
    color="Sales",
    color_continuous_scale="Viridis",
    hover_data=["Profit", "Quantity", "Orders"],
    title="Highest-Selling Products"
)

fig_top_products.update_layout(
    height=480,
    margin=dict(l=10, r=10, t=60, b=20),
    xaxis_title="Total Sales ($)",
    yaxis_title="",
    coloraxis_showscale=False
)

fig_top_products.update_xaxes(
    tickprefix="$",
    separatethousands=True
)

st.plotly_chart(
    fig_top_products,
    use_container_width=True
)

st.divider()

# --------------------------------------------------
# PRODUCT PERFORMANCE TABLE
# --------------------------------------------------

st.subheader("📋 Product Performance Details")

display_products = product_summary.sort_values(
    "Sales",
    ascending=False
).copy()

display_products["Sales"] = display_products["Sales"].map(
    lambda value: f"${value:,.2f}"
)

display_products["Profit"] = display_products["Profit"].map(
    lambda value: f"${value:,.2f}"
)

display_products["Profit Margin (%)"] = (
    display_products["Profit Margin (%)"].map(
        lambda value: f"{value:.2f}%"
        if pd.notna(value) else "N/A"
    )
)

display_products["Quantity"] = display_products["Quantity"].map(
    lambda value: f"{value:,.0f}"
)

st.dataframe(
    display_products.rename(
        columns={
            "Sales": "Total Sales",
            "Profit": "Total Profit",
            "Quantity": "Quantity Sold",
            "Orders": "Unique Orders"
        }
    ),
    use_container_width=True,
    hide_index=True
)

st.divider()

# --------------------------------------------------
# BUSINESS INSIGHTS
# --------------------------------------------------

st.subheader("💡 Business Insights")

best_category = category_summary.loc[
    category_summary["Sales"].idxmax()
]

best_profit_category = category_summary.loc[
    category_summary["Profit"].idxmax()
]

best_segment = segment_summary.loc[
    segment_summary["Sales"].idxmax()
]

best_product = product_summary.loc[
    product_summary["Sales"].idxmax()
]

loss_count = int(
    (product_summary["Profit"] < 0).sum()
)

insights = [
    (
        f"🛍️ **Highest-sales category:** "
        f"{best_category['Category']} "
        f"(${best_category['Sales']:,.2f})"
    ),
    (
        f"💰 **Highest-profit category:** "
        f"{best_profit_category['Category']} "
        f"(${best_profit_category['Profit']:,.2f})"
    ),
    (
        f"👥 **Highest-sales customer segment:** "
        f"{best_segment['Segment']} "
        f"(${best_segment['Sales']:,.2f})"
    ),
    (
        f"🏆 **Top product by sales:** "
        f"{best_product['Product Name']} "
        f"(${best_product['Sales']:,.2f})"
    ),
    f"📉 **Loss-making products:** {loss_count}",
    f"📊 **Overall profit margin:** {profit_margin:.2f}%"
]

for insight in insights:
    st.markdown(f"- {insight}")

st.info(
    "💡 Use the Customer Segment and Category filters to update "
    "the KPIs, charts, product table, and business insights."
)
