import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Geographical Sales Analysis",
    page_icon="🗺️",
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

.section-description {
    color: #64748b;
    margin-top: -8px;
    margin-bottom: 18px;
}

div[data-testid="stPlotlyChart"] {
    margin-bottom: 12px;
}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# PAGE HEADER — MATCHES REGIONAL SALES ANALYSIS
# --------------------------------------------------

st.title("🗺️ Geographical Sales Analysis")

st.write(
    "Explore sales and profitability across different states and cities."
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
        Discover Geographical Performance
    </h2>
    <p style="color:#eef2ff; margin-bottom:0 !important;">
        Compare state and city sales, understand profit contribution,
        and identify the strongest and weakest-performing locations.
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
    df = pd.read_csv(path)

    required_columns = [
        "Country", "City", "State", "Region",
        "Sales", "Profit", "Order ID", "Quantity"
    ]

    missing_columns = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            "Missing required columns: " + ", ".join(missing_columns)
        )

    for col in ["Sales", "Profit", "Quantity"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    for col in ["Country", "City", "State", "Region"]:
        df[col] = df[col].astype("string").str.strip()

    df = df.dropna(subset=required_columns)
    return df


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
# US STATE ABBREVIATIONS
# --------------------------------------------------

state_abbreviations = {
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ",
    "Arkansas": "AR", "California": "CA", "Colorado": "CO",
    "Connecticut": "CT", "Delaware": "DE",
    "District of Columbia": "DC", "Florida": "FL",
    "Georgia": "GA", "Hawaii": "HI", "Idaho": "ID",
    "Illinois": "IL", "Indiana": "IN", "Iowa": "IA",
    "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA",
    "Maine": "ME", "Maryland": "MD", "Massachusetts": "MA",
    "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS",
    "Missouri": "MO", "Montana": "MT", "Nebraska": "NE",
    "Nevada": "NV", "New Hampshire": "NH", "New Jersey": "NJ",
    "New Mexico": "NM", "New York": "NY",
    "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH",
    "Oklahoma": "OK", "Oregon": "OR", "Pennsylvania": "PA",
    "Rhode Island": "RI", "South Carolina": "SC",
    "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX",
    "Utah": "UT", "Vermont": "VT", "Virginia": "VA",
    "Washington": "WA", "West Virginia": "WV",
    "Wisconsin": "WI", "Wyoming": "WY"
}

# --------------------------------------------------
# INTERACTIVE FILTERS
# --------------------------------------------------

st.subheader("🎛️ Explore Geographic Data")

filter1, filter2 = st.columns(2)

with filter1:
    region_options = ["All"] + sorted(
        df["Region"].dropna().unique().tolist()
    )

    selected_region = st.selectbox(
        "Select Region",
        options=region_options,
        index=0,
        key="geo_region_filter"
    )

with filter2:
    if selected_region != "All":
        available_states = sorted(
            df.loc[
                df["Region"] == selected_region,
                "State"
            ].dropna().unique().tolist()
        )
    else:
        available_states = sorted(
            df["State"].dropna().unique().tolist()
        )

    state_options = ["All"] + available_states

    # Reset the state selection if it is not available
    # in the currently selected region.
    if st.session_state.get("geo_state_filter") not in state_options:
        st.session_state["geo_state_filter"] = "All"

    selected_state = st.selectbox(
        "Select State",
        options=state_options,
        index=state_options.index(
            st.session_state.get("geo_state_filter", "All")
        ),
        key="geo_state_filter"
    )

# --------------------------------------------------
# APPLY FILTERS
# --------------------------------------------------

filtered_df = df.copy()

if selected_region != "All":
    filtered_df = filtered_df[
        filtered_df["Region"] == selected_region
    ]

if selected_state != "All":
    filtered_df = filtered_df[
        filtered_df["State"] == selected_state
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
cities_covered = filtered_df["City"].nunique()
profit_margin = total_profit / total_sales * 100 if total_sales else 0

# --------------------------------------------------
# KPI CARDS — NATIVE METRICS
# --------------------------------------------------

st.subheader("📊 Geographic Performance Overview")

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.metric("💰 Total Sales", f"${total_sales:,.2f}")
with kpi2:
    st.metric("📈 Total Profit", f"${total_profit:,.2f}")
with kpi3:
    st.metric("🛒 Total Orders", f"{total_orders:,}")
with kpi4:
    st.metric("🏙️ Cities Covered", f"{cities_covered:,}")

st.caption(f"Profit margin for the selected data: {profit_margin:.2f}%")
st.divider()

# --------------------------------------------------
# STATE SUMMARY
# --------------------------------------------------

state_summary = (
    filtered_df.groupby("State", as_index=False)
    .agg(
        Sales=("Sales", "sum"),
        Profit=("Profit", "sum"),
        Orders=("Order ID", "nunique"),
        Quantity=("Quantity", "sum"),
        Cities=("City", "nunique")
    )
)

state_summary["Profit Margin (%)"] = (
    state_summary["Profit"]
    / state_summary["Sales"].replace(0, float("nan"))
    * 100
)

state_summary["State Code"] = state_summary["State"].map(
    state_abbreviations
)

# --------------------------------------------------
# US STATE SALES MAP
# --------------------------------------------------

st.subheader("🇺🇸 Sales Distribution Across US States")

st.markdown(
    '<p class="section-description">Darker states represent higher sales. '
    'Hover over a state to inspect its sales, profit, orders, and cities.</p>',
    unsafe_allow_html=True
)

mapped_states = state_summary.dropna(subset=["State Code"]).copy()

if not mapped_states.empty:
    fig_map = px.choropleth(
        mapped_states,
        locations="State Code",
        locationmode="USA-states",
        scope="usa",
        color="Sales",
        hover_name="State",
        hover_data={
            "State Code": False,
            "Sales": ":$,.2f",
            "Profit": ":$,.2f",
            "Orders": ":,",
            "Cities": ":,"
        },
        color_continuous_scale="Blues",
        labels={
            "Sales": "Sales",
            "Profit": "Profit",
            "Orders": "Orders",
            "Cities": "Cities"
        }
    )

    fig_map.update_layout(
        height=570,
        margin=dict(l=5, r=5, t=20, b=5),
        geo=dict(
            bgcolor="rgba(0,0,0,0)",
            lakecolor="white",
            showlakes=True
        ),
        coloraxis_colorbar=dict(
            title="Sales ($)",
            tickprefix="$",
            separatethousands=True
        )
    )

    st.plotly_chart(fig_map, use_container_width=True)
else:
    st.info(
        "No recognized US state names are available for the state map "
        "under the current filters."
    )

st.divider()

# --------------------------------------------------
# STATE SALES AND PROFIT COMPARISON
# --------------------------------------------------

st.subheader("📍 State Performance Comparison")

chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    sales_chart_data = state_summary.sort_values(
        "Sales", ascending=True
    )

    fig_state_sales = px.bar(
        sales_chart_data,
        x="Sales",
        y="State",
        orientation="h",
        title="Sales by State",
        color="Sales",
        color_continuous_scale="Blues",
        hover_data=["Profit", "Orders", "Cities"]
    )

    fig_state_sales.update_layout(
        height=max(420, len(sales_chart_data) * 22),
        margin=dict(l=10, r=10, t=60, b=20),
        xaxis_title="Total Sales ($)",
        yaxis_title="",
        coloraxis_showscale=False
    )

    fig_state_sales.update_xaxes(
        tickprefix="$",
        separatethousands=True
    )

    st.plotly_chart(fig_state_sales, use_container_width=True)

with chart_col2:
    profit_chart_data = state_summary.sort_values(
        "Profit", ascending=True
    )

    fig_state_profit = px.bar(
        profit_chart_data,
        x="Profit",
        y="State",
        orientation="h",
        title="Profit by State",
        color="Profit",
        color_continuous_scale="RdYlGn",
        hover_data=["Sales", "Orders", "Cities"]
    )

    fig_state_profit.update_layout(
        height=max(420, len(profit_chart_data) * 22),
        margin=dict(l=10, r=10, t=60, b=20),
        xaxis_title="Total Profit ($)",
        yaxis_title="",
        coloraxis_showscale=False
    )

    fig_state_profit.update_xaxes(
        tickprefix="$",
        separatethousands=True
    )

    st.plotly_chart(fig_state_profit, use_container_width=True)

st.divider()

# --------------------------------------------------
# CITY-LEVEL ANALYSIS
# Automatically follows the selected region and state.
# --------------------------------------------------

st.subheader("🏙️ City-Level Performance")

if selected_state != "All":
    city_description = (
        f"Explore sales and profitability for cities in {selected_state}."
    )
elif selected_region != "All":
    city_description = (
        f"Explore sales and profitability for cities in the "
        f"{selected_region} region."
    )
else:
    city_description = (
        "Explore sales and profitability for cities across all regions."
    )

st.markdown(
    f'<p class="section-description">{city_description}</p>',
    unsafe_allow_html=True
)

# Use filtered_df so city analysis follows the selected filters.
city_summary = (
    filtered_df.groupby(["City", "State"], as_index=False)
    .agg(
        Sales=("Sales", "sum"),
        Profit=("Profit", "sum"),
        Orders=("Order ID", "nunique"),
        Quantity=("Quantity", "sum")
    )
)

city_summary["Profit Margin (%)"] = (
    city_summary["Profit"]
    / city_summary["Sales"].replace(0, float("nan"))
    * 100
)

# Include state in the chart label to distinguish cities
# with the same name in different states.
city_summary["City Label"] = (
    city_summary["City"].astype(str)
    + ", "
    + city_summary["State"].astype(str)
)

city_col1, city_col2 = st.columns(2)

with city_col1:
    top_cities_sales = (
        city_summary.nlargest(10, "Sales")
        .sort_values("Sales", ascending=True)
    )

    fig_city_sales = px.bar(
        top_cities_sales,
        x="Sales",
        y="City Label",
        orientation="h",
        color="Sales",
        color_continuous_scale="Teal",
        hover_data={
            "City": True,
            "State": True,
            "Profit": ":$,.2f",
            "Orders": ":,",
            "City Label": False
        },
        title="Top 10 Cities by Sales"
    )

    fig_city_sales.update_layout(
        height=460,
        margin=dict(l=10, r=10, t=60, b=20),
        xaxis_title="Total Sales ($)",
        yaxis_title="",
        coloraxis_showscale=False
    )

    fig_city_sales.update_xaxes(
        tickprefix="$",
        separatethousands=True
    )

    st.plotly_chart(fig_city_sales, use_container_width=True)

with city_col2:
    top_cities_profit = (
        city_summary.nlargest(10, "Profit")
        .sort_values("Profit", ascending=True)
    )

    fig_city_profit = px.bar(
        top_cities_profit,
        x="Profit",
        y="City Label",
        orientation="h",
        color="Profit",
        color_continuous_scale="Greens",
        hover_data={
            "City": True,
            "State": True,
            "Sales": ":$,.2f",
            "Orders": ":,",
            "City Label": False
        },
        title="Top 10 Cities by Profit"
    )

    fig_city_profit.update_layout(
        height=460,
        margin=dict(l=10, r=10, t=60, b=20),
        xaxis_title="Total Profit ($)",
        yaxis_title="",
        coloraxis_showscale=False
    )

    fig_city_profit.update_xaxes(
        tickprefix="$",
        separatethousands=True
    )

    st.plotly_chart(fig_city_profit, use_container_width=True)

st.divider()

# --------------------------------------------------
# STATE PERFORMANCE TABLE
# --------------------------------------------------

st.subheader("📋 State Performance Details")

display_states = state_summary.sort_values(
    "Sales", ascending=False
).copy()

display_states = display_states.rename(
    columns={
        "Sales": "Total Sales ($)",
        "Profit": "Total Profit ($)",
        "Orders": "Unique Orders",
        "Quantity": "Quantity Sold",
        "Cities": "Cities Covered"
    }
)

display_states["Total Sales ($)"] = display_states[
    "Total Sales ($)"
].map(lambda value: f"${value:,.2f}")

display_states["Total Profit ($)"] = display_states[
    "Total Profit ($)"
].map(lambda value: f"${value:,.2f}")

display_states["Profit Margin (%)"] = display_states[
    "Profit Margin (%)"
].map(
    lambda value: f"{value:.2f}%" if pd.notna(value) else "N/A"
)

st.dataframe(
    display_states[
        [
            "State",
            "Total Sales ($)",
            "Total Profit ($)",
            "Profit Margin (%)",
            "Unique Orders",
            "Quantity Sold",
            "Cities Covered"
        ]
    ],
    use_container_width=True,
    hide_index=True
)

st.divider()

# --------------------------------------------------
# BUSINESS INSIGHTS
# --------------------------------------------------

st.subheader("💡 Business Insights")

best_sales_state = state_summary.loc[
    state_summary["Sales"].idxmax()
]

best_profit_state = state_summary.loc[
    state_summary["Profit"].idxmax()
]

lowest_profit_state = state_summary.loc[
    state_summary["Profit"].idxmin()
]

best_sales_city = city_summary.loc[
    city_summary["Sales"].idxmax()
]

best_profit_city = city_summary.loc[
    city_summary["Profit"].idxmax()
]

insights = [
    f"🗺️ **States included:** {len(state_summary):,}",
    f"🏙️ **Cities included:** {cities_covered:,}",
    f"💰 **Total sales:** ${total_sales:,.2f}",
    f"📈 **Total profit:** ${total_profit:,.2f}",
    f"🏆 **Highest-sales state:** {best_sales_state['State']} (${best_sales_state['Sales']:,.2f})",
    f"💵 **Highest-profit state:** {best_profit_state['State']} (${best_profit_state['Profit']:,.2f})",
    f"⚠️ **Lowest-profit state:** {lowest_profit_state['State']} (${lowest_profit_state['Profit']:,.2f})",
    f"🏙️ **Highest-sales city:** {best_sales_city['City']}, {best_sales_city['State']} (${best_sales_city['Sales']:,.2f})",
    f"🌟 **Highest-profit city:** {best_profit_city['City']}, {best_profit_city['State']} (${best_profit_city['Profit']:,.2f})",
    f"📊 **Profit margin:** {profit_margin:.2f}%"
]

for insight in insights:
    st.markdown(f"- {insight}")

st.info(
    "💡 Use the region and state filters at the top to update the KPI cards, "
    "map, charts, table, and business insights."
)
