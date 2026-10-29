
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------
st.set_page_config(
    page_title="Sales by Year",
    page_icon="📅",
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

.block-container {
    padding-top: 1.8rem;
    padding-bottom: 3rem;
}

.hero {
    background: linear-gradient(120deg, #581c87, #7c3aed, #2563eb);
    padding: 26px 30px;
    border-radius: 18px;
    margin: 18px 0 25px 0;
    box-shadow: 0 6px 18px rgba(91, 33, 182, 0.15);
}

.hero h2 {
    color: white;
    margin: 0 0 10px 0;
}

.hero p {
    color: #f5f3ff;
    font-size: 16px;
    margin: 0;
    line-height: 1.6;
}

.section-heading {
    color: #312e81;
    font-size: 23px;
    font-weight: 700;
    margin-top: 12px;
    margin-bottom: 5px;
}

.section-description {
    color: #64748b;
    font-size: 14px;
    margin-bottom: 16px;
}

div[data-testid="stMetric"] {
    background: rgba(255, 255, 255, 0.95);
    padding: 17px 15px;
    border-radius: 15px;
    border: 1px solid #ddd6fe;
    box-shadow: 0 4px 12px rgba(91, 33, 182, 0.07);
    min-width: 0;
}

div[data-testid="stMetricLabel"] {
    color: #475569;
    font-size: 13px;
}

div[data-testid="stMetricValue"] {
    color: #6d28d9;
    font-size: clamp(17px, 1.5vw, 26px);
}

div[data-testid="stDataFrame"] {
    border: 1px solid #ddd6fe;
    border-radius: 12px;
    overflow: hidden;
}

.insight-list {
    color: #334155;
    font-size: 15px;
    line-height: 1.9;
}

hr {
    border-color: #ddd6fe;
    margin-top: 25px;
    margin-bottom: 25px;
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
    st.error("Cleaned dataset not found. Please run main.py first.")
    st.stop()

try:
    df = pd.read_csv(file_path)
except Exception as error:
    st.error(f"Unable to read the dataset: {error}")
    st.stop()

required_columns = ["Order Date", "Sales"]

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
    df["Sales"],
    errors="coerce"
)

df = df.dropna(subset=["Order Date", "Sales"])

if df.empty:
    st.warning("No valid sales records were found.")
    st.stop()

df["Year"] = df["Order Date"].dt.year


# --------------------------------------------------
# YEARLY ANALYSIS
# --------------------------------------------------
yearly_sales = (
    df.groupby("Year")["Sales"]
    .sum()
    .sort_index()
)

if yearly_sales.empty:
    st.warning("No yearly sales data is available.")
    st.stop()

yearly_growth = yearly_sales.pct_change() * 100

total_sales = float(yearly_sales.sum())
best_year = int(yearly_sales.idxmax())
best_sales = float(yearly_sales.max())
average_sales = float(yearly_sales.mean())

first_year = int(yearly_sales.index.min())
latest_year = int(yearly_sales.index.max())

first_year_sales = float(yearly_sales.iloc[0])
latest_year_sales = float(yearly_sales.iloc[-1])

if first_year_sales != 0:
    overall_change = (
        (latest_year_sales - first_year_sales)
        / abs(first_year_sales)
    ) * 100
else:
    overall_change = None

# Prepare chart data
sales_chart_data = yearly_sales.rename("Sales").reset_index()
sales_chart_data.columns = ["Year", "Sales"]
sales_chart_data["Year"] = sales_chart_data["Year"].astype(str)

growth_data = pd.DataFrame({
    "Year": yearly_growth.index.astype(str),
    "Growth": yearly_growth.values
}).dropna()

# Color palette
year_colors = [
    "#6366f1",
    "#14b8a6",
    "#f59e0b",
    "#ec4899",
    "#8b5cf6",
    "#06b6d4",
    "#22c55e",
    "#f97316"
]

color_map = {
    str(year): year_colors[index % len(year_colors)]
    for index, year in enumerate(yearly_sales.index)
}

# Highlight the best year
color_map[str(best_year)] = "#f97316"


# --------------------------------------------------
# HEADER
# --------------------------------------------------
st.title("📅 Sales by Year")

st.markdown("""
<div class="hero">
    <h2>Explore Your Yearly Sales Performance 📊</h2>
    <p>
        Understand annual sales trends, compare year-over-year growth,
        and discover how each year contributes to overall business sales.
    </p>
</div>
""", unsafe_allow_html=True)


# --------------------------------------------------
# KPI CARDS
# --------------------------------------------------
st.markdown(
    '<div class="section-heading">📌 Yearly Performance Overview</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-description">'
    'A quick summary of sales performance across all available years.'
    '</div>',
    unsafe_allow_html=True
)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "💰 Total Sales",
        f"${total_sales:,.0f}"
    )

with col2:
    st.metric(
        "🏆 Best Sales Year",
        str(best_year)
    )

with col3:
    st.metric(
        "📈 Highest Annual Sales",
        f"${best_sales:,.0f}"
    )

with col4:
    st.metric(
        "📊 Average Annual Sales",
        f"${average_sales:,.0f}"
    )


st.divider()


# --------------------------------------------------
# CHART 1: ANNUAL SALES COMPARISON
# --------------------------------------------------
st.markdown(
    '<div class="section-heading">💵 Annual Sales Comparison</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-description">'
    'Compare annual sales. The best-performing year is highlighted in orange.'
    '</div>',
    unsafe_allow_html=True
)

sales_fig = px.bar(
    sales_chart_data,
    x="Year",
    y="Sales",
    color="Year",
    color_discrete_map=color_map,
    text="Sales"
)

sales_fig.update_traces(
    texttemplate="$%{text:,.0f}",
    textposition="outside",
    cliponaxis=False,
    marker_line_width=0,
    hovertemplate=(
        "<b>Year:</b> %{x}<br>"
        "<b>Total Sales:</b> $%{y:,.2f}"
        "<extra></extra>"
    )
)

sales_fig.update_layout(
    height=390,
    showlegend=False,
    bargap=0.42,
    plot_bgcolor="rgba(255,255,255,0.85)",
    paper_bgcolor="rgba(255,255,255,0)",
    font=dict(family="Arial", color="#334155"),
    xaxis_title="Year",
    yaxis_title="Total Sales ($)",
    yaxis=dict(
        tickprefix="$",
        tickformat=",.0f",
        gridcolor="#e2e8f0",
        rangemode="tozero"
    ),
    margin=dict(l=20, r=25, t=25, b=25)
)

st.plotly_chart(
    sales_fig,
    use_container_width=True
)


st.divider()


# --------------------------------------------------
# CHART 2: YEAR-OVER-YEAR GROWTH
# --------------------------------------------------
st.markdown(
    '<div class="section-heading">📈 Year-over-Year Sales Growth</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-description">'
    'See how sales changed compared with the previous year. '
    'Green indicates growth; red indicates a decline.'
    '</div>',
    unsafe_allow_html=True
)

if not growth_data.empty:

    growth_colors = [
        "#10b981" if value >= 0 else "#ef4444"
        for value in growth_data["Growth"]
    ]

    growth_fig = go.Figure()

    growth_fig.add_trace(
        go.Bar(
            x=growth_data["Year"],
            y=growth_data["Growth"],
            marker_color=growth_colors,
            text=growth_data["Growth"],
            texttemplate="%{text:.2f}%",
            textposition="outside",
            cliponaxis=False,
            hovertemplate=(
                "<b>Year:</b> %{x}<br>"
                "<b>Sales Growth:</b> %{y:.2f}%"
                "<extra></extra>"
            )
        )
    )

    growth_fig.add_hline(
        y=0,
        line_dash="dash",
        line_color="#64748b",
        line_width=1.5
    )

    growth_fig.update_layout(
        height=340,
        showlegend=False,
        bargap=0.42,
        plot_bgcolor="rgba(255,255,255,0.85)",
        paper_bgcolor="rgba(255,255,255,0)",
        font=dict(family="Arial", color="#334155"),
        xaxis_title="Year",
        yaxis_title="Sales Growth (%)",
        yaxis=dict(
            ticksuffix="%",
            gridcolor="#e2e8f0",
            zeroline=False
        ),
        margin=dict(l=20, r=25, t=25, b=25)
    )

    st.plotly_chart(
        growth_fig,
        use_container_width=True
    )

else:
    st.info(
        "At least two years of data are needed to calculate year-over-year growth."
    )


st.divider()


# --------------------------------------------------
# CHART 3: SHARE OF TOTAL SALES
# --------------------------------------------------
st.markdown(
    '<div class="section-heading">🍩 Share of Total Sales</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-description">'
    'Understand each year’s contribution to total sales.'
    '</div>',
    unsafe_allow_html=True
)

share_fig = px.pie(
    sales_chart_data,
    names="Year",
    values="Sales",
    hole=0.55,
    color="Year",
    color_discrete_map=color_map
)

share_fig.update_traces(
    textposition="inside",
    textinfo="percent+label",
    hovertemplate=(
        "<b>Year:</b> %{label}<br>"
        "<b>Sales:</b> $%{value:,.2f}<br>"
        "<b>Share:</b> %{percent}"
        "<extra></extra>"
    ),
    marker=dict(
        line=dict(color="white", width=2)
    )
)

share_fig.update_layout(
    height=360,
    showlegend=True,
    paper_bgcolor="rgba(255,255,255,0)",
    font=dict(family="Arial", color="#334155"),
    margin=dict(l=20, r=20, t=20, b=20),
    legend_title_text="Year"
)

st.plotly_chart(
    share_fig,
    use_container_width=True
)


st.divider()


# --------------------------------------------------
# YEARLY SALES DETAILS TABLE
# --------------------------------------------------
st.markdown(
    '<div class="section-heading">📋 Yearly Sales Details</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-description">'
    'Review annual sales and the corresponding growth rate.'
    '</div>',
    unsafe_allow_html=True
)

yearly_summary = pd.DataFrame({
    "Year": yearly_sales.index,
    "Total Sales ($)": yearly_sales.values,
    "Sales Growth (%)": yearly_growth.values
})

yearly_summary["Year"] = yearly_summary["Year"].astype(int)

st.dataframe(
    yearly_summary,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Year": st.column_config.NumberColumn(
            "Year",
            format="%d"
        ),
        "Total Sales ($)": st.column_config.NumberColumn(
            "Total Sales ($)",
            format="$%.2f"
        ),
        "Sales Growth (%)": st.column_config.NumberColumn(
            "Sales Growth (%)",
            format="%.2f%%"
        )
    }
)


st.divider()


# --------------------------------------------------
# BUSINESS INSIGHTS
# --------------------------------------------------
st.subheader("💡 Business Insights")

insights = [
    f"🏆 **Best-performing year:** {best_year}, with sales of **${best_sales:,.2f}**.",
    f"📊 **Average annual sales:** ${average_sales:,.2f}."
]

if len(yearly_sales) >= 2:

    latest_growth = yearly_growth.iloc[-1]

    if pd.notna(latest_growth):
        if latest_growth > 0:
            insights.append(
                f"🚀 **Latest annual trend:** Sales grew by "
                f"**{latest_growth:.2f}% in {latest_year}** "
                f"compared with {int(yearly_sales.index[-2])}."
            )

        elif latest_growth < 0:
            insights.append(
                f"📉 **Latest annual trend:** Sales declined by "
                f"**{abs(latest_growth):.2f}% in {latest_year}** "
                f"compared with {int(yearly_sales.index[-2])}."
            )

        else:
            insights.append(
                f"➡️ **Latest annual trend:** Sales remained unchanged "
                f"in {latest_year} compared with the previous year."
            )

    if overall_change is not None:
        if overall_change > 0:
            insights.append(
                f"📈 **Long-term performance:** Sales increased by "
                f"**{overall_change:.2f}%** from {first_year} to {latest_year}."
            )
        elif overall_change < 0:
            insights.append(
                f"📉 **Long-term performance:** Sales decreased by "
                f"**{abs(overall_change):.2f}%** from {first_year} to {latest_year}."
            )
        else:
            insights.append(
                f"➡️ **Long-term performance:** Sales were unchanged "
                f"between {first_year} and {latest_year}."
            )

insights.append(
    "💡 **Business recommendation:** Investigate the factors behind "
    "the strongest growth years to identify strategies that may help "
    "improve future sales and profitability."
)

st.markdown(
    "\n".join(f"- {insight}" for insight in insights)
)
