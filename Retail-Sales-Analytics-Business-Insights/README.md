# Retail Sales Analytics & Business Insights Dashboard

## 📌 Project Overview

An interactive, multi-page dashboard built using Python and Streamlit to analyze retail sales, profitability, product performance, and regional trends.

The project follows a data analytics workflow, starting with raw data cleaning and preparation, followed by exploratory analysis and interactive visualization to generate meaningful business insights.

## 🎯 Objectives

- Clean and prepare raw retail sales data for analysis.
- Analyze yearly and monthly sales trends.
- Compare sales and profit across product categories.
- Evaluate regional and geographical performance.
- Identify high-performing and loss-making product sub-categories.
- Present business insights through interactive visualizations.

## 📊 Dataset

The project uses a Superstore retail sales dataset containing order details, customer information, shipping details, product categories, sales, discounts, and profits.

| Attribute | Details |
|---|---|
| Original dataset | 9,994 rows and 21 columns |
| Cleaned dataset | 9,993 rows and 19 columns |
| Time period | January 2011 – December 2014 |
| Missing values in cleaned data | 0 |
| Duplicate rows in cleaned data | 0 |

## 🛠️ Technologies Used

- **Python** — Main programming language.
- **Pandas** — Data cleaning, manipulation, and analysis.
- **NumPy** — Numerical operations.
- **Matplotlib and Seaborn** — Data visualization.
- **Plotly** — Interactive charts and visualizations.
- **Streamlit** — Interactive, multi-page dashboard development.
- **pathlib** — File and folder path management using Python's standard library.

## 🔄 Project Workflow

### Step 1: Data Cleaning and Preparation

- Loaded and examined the original Superstore dataset using Pandas.
- Removed unnecessary columns, including `Row ID` and `Postal Code`.
- Identified and removed one duplicate record based on the retained columns.
- Validated date fields and checked data quality.
- Saved the cleaned dataset as `cleaned_superstore_sales.csv`.

The original dataset contained 9,994 rows and 21 columns. After removing two columns and one duplicate record, the cleaned dataset contained 9,993 rows and 19 columns.

### Step 2: Data Analysis

- Analyzed sales and profit across years and months.
- Compared product category and sub-category performance.
- Evaluated regional sales and profitability.
- Explored geographical sales patterns.
- Examined differences between sales revenue and profit.

### Step 3: Dashboard Development

Developed a multi-page Streamlit dashboard with interactive visualizations to explore retail sales data and present business insights.

## 📈 Dashboard Features

1. **Sales by Year** — Explore annual sales performance.
2. **Sales by Month** — Analyze monthly sales trends.
3. **Category Analysis** — Compare sales and profitability across product categories.
4. **Regional Analysis** — Evaluate sales and profit across different regions.
5. **Product Analysis** — Examine product and sub-category performance.
6. **Geographical Analysis** — Explore location-based sales patterns.
7. **View Dataset** — Browse and inspect the original and cleaned datasets.

## 🔍 Key Business Insights

The following findings were calculated from the cleaned dataset.

- **Overall Sales:** Approximately $2.30 million in total sales.
- **Overall Profit:** Approximately $286,409 in total profit.
- **Top Category:** Technology recorded the highest sales and profit among the three product categories.
- **Top Region:** The West region generated the highest sales and profit.
- **Profitability Concern:** Tables recorded a loss of approximately $17,725, making this sub-category a useful area for further investigation.

These findings demonstrate why businesses should evaluate profitability alongside sales revenue.

## 📁 Project Structure

```text
Retail-Sales-Analytics-Business-Insights/
├── app.py
├── main.py
├── README.md
├── data/
│   ├── Superstore_Sales_Data.csv
│   └── cleaned_superstore_sales.csv
└── pages/
    ├── 1_Sales_by_Year.py
    ├── 2_Sales_by_Month.py
    ├── 3_Category_Analysis.py
    ├── 4_Regional_Analysis.py
    ├── 5_Product_Analysis.py
    ├── 6_Geographical_Analysis.py
    └── 7_View_Dataset.py
```

## ⚙️ Installation and Usage

### Prerequisites

- Python 3.10 or a compatible version.
- Git.

### 1. Clone the Repository

```bash
git clone https://github.com/manognaabhagavatula-dev/Data-Analyst-Portfolio.git
```

### 2. Navigate to the Project Folder

```bash
cd Data-Analyst-Portfolio/Retail-Sales-Analytics-Business-Insights
```

### 3. Create and Activate a Virtual Environment (Recommended)

Create the environment:

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\Activate.ps1
```

### 4. Install Dependencies

```bash
pip install pandas numpy matplotlib seaborn plotly streamlit
```

### 5. Run the Dashboard

```bash
streamlit run app.py
```

Once the application starts, open the local URL displayed in your terminal to access the dashboard.

## 🚀 Future Improvements

- Add more interactive filters and key performance indicators.
- Expand discount and profitability analysis.
- Improve geographical visualizations.
- Deploy the dashboard online.
- Add dashboard screenshots to the project documentation.

## 🎓 Skills Demonstrated

- Python programming
- Data cleaning and preprocessing
- Data manipulation using Pandas
- Exploratory data analysis
- Sales and profitability analysis
- Data visualization
- Interactive dashboard development
- Business insight communication

## 📝 Conclusion

The Retail Sales Analytics & Business Insights Dashboard demonstrates how raw retail data can be cleaned, analyzed, and transformed into an interactive dashboard.

The project combines data preparation, exploratory analysis, and visualization to explore sales performance and profitability across products, categories, and regions.