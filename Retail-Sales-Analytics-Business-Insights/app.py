import streamlit as st
import pandas as pd
from pathlib import Path

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------
st.set_page_config(
    page_title="Retail Sales Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

BASE_DIR = Path(__file__).parent
DATA_PATH = BASE_DIR / "data" / "cleaned_superstore_sales.csv"


# --------------------------------------------------
# CUSTOM DESIGN
# --------------------------------------------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #f4f7ff, #eaf1ff);
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #101b3f, #243b70);
}

[data-testid="stSidebar"] * {
    color: white;
}

.hero {
    background: linear-gradient(120deg, #172554, #2563eb, #6d28d9);
    padding: 30px;
    border-radius: 20px;
    color: white;
    margin: 18px 0 26px 0;
    box-shadow: 0 8px 22px rgba(37, 99, 235, 0.18);
}

.hero h2 {
    color: white;
    margin-bottom: 12px;
}

.hero p {
    color: #eef2ff;
    font-size: 17px;
    line-height: 1.7;
    margin-bottom: 0;
}

.section-intro {
    color: #475569;
    font-size: 15px;
    margin-top: -8px;
    margin-bottom: 18px;
}

div[data-testid="stMetric"] {
    background: white;
    border: 1px solid #dbeafe;
    padding: 18px 14px;
    border-radius: 16px;
    box-shadow: 0 4px 12px rgba(30, 64, 175, 0.08);
    min-width: 0;
}

div[data-testid="stMetricLabel"] {
    font-size: 13px;
}

div[data-testid="stMetricValue"] {
    color: #1d4ed8;
    font-size: clamp(16px, 1.5vw, 25px);
}

div.stButton > button {
    width: 100%;
    min-height: 48px;
    border-radius: 12px;
    background: white;
    color: #1e3a8a;
    border: 1px solid #c7d2fe;
    font-weight: 600;
    transition: 0.2s ease;
}

div.stButton > button:hover {
    background: #dbeafe;
    color: #1d4ed8;
    border-color: #3b82f6;
}

.insight-box {
    background: linear-gradient(120deg, #ffffff, #eef2ff);
    border-left: 5px solid #6366f1;
    border-radius: 12px;
    padding: 18px 22px;
    margin: 12px 0 24px 0;
    color: #1e293b;
    box-shadow: 0 4px 12px rgba(30, 64, 175, 0.06);
}

.analysis-card {
    background: rgba(255, 255, 255, 0.92);
    border: 1px solid #dbeafe;
    border-radius: 16px;
    padding: 20px;
    min-height: 155px;
    margin-bottom: 10px;
    box-shadow: 0 4px 12px rgba(30, 64, 175, 0.05);
}

.analysis-card h4 {
    color: #1e3a8a;
    margin-top: 0;
    margin-bottom: 8px;
}

.analysis-card p {
    color: #475569;
    font-size: 14px;
    min-height: 38px;
}

.footer {
    text-align: center;
    color: #64748b;
    font-size: 13px;
    padding: 24px 0 10px 0;
}
</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------
@st.cache_data
def load_data():
    if not DATA_PATH.exists():
        return None

    data = pd.read_csv(DATA_PATH)

    required_columns = [
        "Order Date",
        "Sales",
        "Profit",
        "Order ID",
        "Quantity"
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

    data["Order Date"] = pd.to_datetime(
        data["Order Date"],
        errors="coerce"
    )

    for column in ["Sales", "Profit", "Quantity"]:
        data[column] = pd.to_numeric(
            data[column],
            errors="coerce"
        )

    data = data.dropna(
        subset=[
            "Order Date",
            "Sales",
            "Profit",
            "Order ID",
            "Quantity"
        ]
    )

    return data


# --------------------------------------------------
# HOME PAGE
# --------------------------------------------------
def home_page():

    st.title("📊 Retail Sales Analytics & Business Insights Dashboard")

    st.markdown(
        '<p class="section-intro">'
        'A simple overview of sales performance and business insights.'
        '</p>',
        unsafe_allow_html=True
    )

    # WELCOME BANNER
    st.markdown("""
    <div class="hero">
        <h2>👋 Welcome to Your Business Intelligence Dashboard</h2>
        <p>
            Discover business performance, understand sales results,
            and explore product and regional trends through interactive
            analytics. Choose an analysis below to investigate the data
            in more detail.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # LOAD DATA SAFELY
    try:
        df = load_data()
    except Exception as error:
        st.error(f"Unable to load the dataset: {error}")
        st.stop()

    if df is None:
        st.error(
            "Cleaned dataset not found. "
            "Please run main.py and check the data folder."
        )
        st.stop()

    if df.empty:
        st.warning("The cleaned dataset contains no usable records.")
        st.stop()

    # --------------------------------------------------
    # BUSINESS OVERVIEW
    # --------------------------------------------------
    st.subheader("📌 Business Overview")

    st.markdown(
        '<p class="section-intro">'
        'Key performance indicators from the complete sales dataset.'
        '</p>',
        unsafe_allow_html=True
    )

    total_sales = df["Sales"].sum()
    total_profit = df["Profit"].sum()
    total_orders = df["Order ID"].nunique()
    total_quantity = df["Quantity"].sum()

    total_margin = (
        (total_profit / total_sales) * 100
        if total_sales != 0
        else 0
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "💰 Total Sales",
            f"${total_sales:,.0f}"
        )

    with col2:
        st.metric(
            "📈 Total Profit",
            f"${total_profit:,.0f}"
        )

    with col3:
        st.metric(
            "🛒 Total Orders",
            f"{total_orders:,}"
        )

    with col4:
        st.metric(
            "📦 Quantity Sold",
            f"{total_quantity:,.0f}"
        )

    st.divider()

    # --------------------------------------------------
    # KEY BUSINESS TAKEAWAY
    # --------------------------------------------------
    st.subheader("💡 Key Business Takeaway")

    st.markdown(f"""
    <div class="insight-box">
        <strong>📊 Overall Performance</strong><br><br>
        The business generated <strong>${total_sales:,.2f}</strong>
        in sales and <strong>${total_profit:,.2f}</strong> in profit
        across <strong>{total_orders:,}</strong> unique orders.
        The overall profit margin is
        <strong>{total_margin:.2f}%</strong>.
        <br><br>
        🎯 <strong>What this means:</strong>
        Explore the category, product, regional, and time-based analysis
        pages to identify where sales are strongest and where profitability
        could be improved.
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # --------------------------------------------------
    # INTERACTIVE ANALYSIS NAVIGATION
    # --------------------------------------------------
    st.subheader("🧭 Explore Your Analysis")

    st.markdown(
        '<p class="section-intro">'
        'Select a section to explore a specific aspect of business performance.'
        '</p>',
        unsafe_allow_html=True
    )

    # ROW 1
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="analysis-card">
            <h4>📅 Sales by Year</h4>
            <p>Compare annual sales, yearly growth, and performance over time.</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button(
            "Explore Yearly Sales →",
            key="year_btn",
            use_container_width=True
        ):
            st.switch_page("pages/1_Sales_by_Year.py")

    with col2:
        st.markdown("""
        <div class="analysis-card">
            <h4>📈 Sales by Month</h4>
            <p>Explore monthly sales, profit, and seasonal patterns.</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button(
            "Explore Monthly Sales →",
            key="month_btn",
            use_container_width=True
        ):
            st.switch_page("pages/2_Sales_by_Month.py")

    with col3:
        st.markdown("""
        <div class="analysis-card">
            <h4>🛍️ Category Analysis</h4>
            <p>Compare product categories by sales and profitability.</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button(
            "Explore Categories →",
            key="category_btn",
            use_container_width=True
        ):
            st.switch_page("pages/3_Category_Analysis.py")

    # ROW 2
    col4, col5, col6 = st.columns(3)

    with col4:
        st.markdown("""
        <div class="analysis-card">
            <h4>🌍 Regional Analysis</h4>
            <p>Discover regional sales performance and profit differences.</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button(
            "Explore Regions →",
            key="region_btn",
            use_container_width=True
        ):
            st.switch_page("pages/4_Regional_Analysis.py")

    with col5:
        st.markdown("""
        <div class="analysis-card">
            <h4>🏆 Product Analysis</h4>
            <p>Identify top-performing products and sales opportunities.</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button(
            "Explore Products →",
            key="product_btn",
            use_container_width=True
        ):
            st.switch_page("pages/5_Product_Analysis.py")

    with col6:
        st.markdown("""
        <div class="analysis-card">
            <h4>🗺️ Geographical Analysis</h4>
            <p>Explore sales and profitability across states and cities.</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button(
            "Explore Geography →",
            key="geo_btn",
            use_container_width=True
        ):
            st.switch_page("pages/6_Geographical_Analysis.py")

    # FOOTER
    st.markdown("""
    <div class="footer">
        Built with Python, Pandas, and Streamlit
        <br>
        Retail Sales Analytics Portfolio Project
    </div>
    """, unsafe_allow_html=True)


# --------------------------------------------------
# SIDEBAR BRANDING
# --------------------------------------------------
st.sidebar.title("📊 Retail Insights")
st.sidebar.caption("SALES ANALYTICS PLATFORM")
st.sidebar.divider()

st.sidebar.write(
    "Explore sales, profit, and business performance."
)

st.sidebar.divider()
st.sidebar.caption("Built with Python and Streamlit")


# --------------------------------------------------
# MULTIPAGE NAVIGATION
# --------------------------------------------------
home = st.Page(
    home_page,
    title="Home",
    icon="🏠",
    default=True
)

sales_year = st.Page(
    "pages/1_Sales_by_Year.py",
    title="Sales by Year",
    icon="📅"
)

sales_month = st.Page(
    "pages/2_Sales_by_Month.py",
    title="Sales by Month",
    icon="📈"
)

category_analysis = st.Page(
    "pages/3_Category_Analysis.py",
    title="Category Analysis",
    icon="🛍️"
)

regional_analysis = st.Page(
    "pages/4_Regional_Analysis.py",
    title="Regional Analysis",
    icon="🌍"
)

product_analysis = st.Page(
    "pages/5_Product_Analysis.py",
    title="Product Analysis",
    icon="🏆"
)

geo_analysis = st.Page(
    "pages/6_Geographical_Analysis.py",
    title="Geographical Analysis",
    icon="🗺️"
)

view_dataset = st.Page(
    "pages/7_View_Dataset.py",
    title="View Dataset",
    icon="📋"
)

navigation = st.navigation({
    "Overview": [
        home
    ],
    "Sales Analysis": [
        sales_year,
        sales_month,
        category_analysis,
        regional_analysis,
        product_analysis,
        geo_analysis,
        view_dataset
    ]
})

navigation.run()
