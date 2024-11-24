import streamlit as st
import plotly.express as px
import pandas as pd
import os
import warnings

# Suppress warnings
warnings.filterwarnings('ignore')

# Set Streamlit page configuration
st.set_page_config(page_title="Sangam Store Analytics", 
                   page_icon=":bar_chart:", 
                   layout="wide")

# Custom CSS for background theme
custom_css = """
<style>
/* Background color */
[data-testid="stAppViewContainer"] {
    background-color: #1e1e2f;
    color: #ffffff;
}

/* Sidebar styling */
[data-testid="stSidebar"] {
    background-color: #2c2c54;
    color: #ffffff;
}

/* Modify headings and text */
h1, h2, h3, h4, h5, h6, p, label {
    color: #ffffff;
}

/* Input box styling */
[data-testid="stFileUploadDropzone"], [data-testid="stDateInput"] {
    background-color: #35354f;
    color: #ffffff;
    border: 1px solid #8888aa;
}

/* Table styling */
table {
    background-color: #3c3c6c;
    color: #ffffff;
    border-collapse: collapse;
}

th {
    background-color: #48487e;
    color: #ffffff;
}

td {
    border: 1px solid #8888aa;
}

/* Button styling */
button {
    background-color: #48487e;
    color: #ffffff;
    border-radius: 10px;
}

button:hover {
    background-color: #6262a5;
}
</style>
"""

# Inject the CSS
st.markdown(custom_css, unsafe_allow_html=True)

# Page Title
st.title(":bar_chart: Sangam SuperMart Dashboard 🛒")

# Directory for fallback files
FALLBACK_DIR = r"C:\Users\J.N.PATHAK\Desktop\streamlit"

# Function to Load Data
@st.cache_data
def load_data(file):
    """Load data from uploaded file or fallback to local dataset."""
    try:
        if file is not None:
            ext = file.name.split('.')[-1]
            if ext in ["csv", "txt"]:
                return pd.read_csv(file, encoding="ISO-8859-1")
            elif ext in ["xlsx", "xls"]:
                return pd.read_excel(file)
        else:
            # Fallback to default file in the specified directory
            fallback_file = os.path.join(FALLBACK_DIR, "Sample - Superstore.xlsx")
            if fallback_file.endswith(".csv"):
                return pd.read_csv(fallback_file, encoding="ISO-8859-1")
            else:
                return pd.read_excel(fallback_file)
    except Exception as e:
        st.error(f"Error loading file: {e}")
        return pd.DataFrame()  # Return an empty DataFrame on failure

# File Upload Section
file = st.file_uploader(":file_folder: Upload a dataset", type=["csv", "txt", "xlsx", "xls"])
df = load_data(file)

# Convert "Order Date" to datetime and handle date range
if not df.empty:
    df["Order Date"] = pd.to_datetime(df["Order Date"], errors='coerce')
    start_date, end_date = df["Order Date"].min(), df["Order Date"].max()
else:
    st.error("No data available. Please upload a valid file.")

col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("Start Date", start_date if not df.empty else None)
with col2:
    end_date = st.date_input("End Date", end_date if not df.empty else None)

if not df.empty:
    df = df[(df["Order Date"] >= pd.to_datetime(start_date)) & (df["Order Date"] <= pd.to_datetime(end_date))]

# Sidebar Filters
st.sidebar.header("Filters")
def apply_filter(column, label):
    """Apply filter for sidebar multiselect."""
    options = st.sidebar.multiselect(label, df[column].unique()) if not df.empty else []
    return options if options else (df[column].unique() if not df.empty else [])

if not df.empty:
    region_filter = apply_filter("Region", "Select Region(s):")
    state_filter = apply_filter("State", "Select State(s):")
    city_filter = apply_filter("City", "Select City(s):")

    # Apply all filters
    filtered_df = df[(df["Region"].isin(region_filter)) & 
                     (df["State"].isin(state_filter)) & 
                     (df["City"].isin(city_filter))]
else:
    filtered_df = pd.DataFrame()

# Grouped Data
if not filtered_df.empty:
    category_sales = filtered_df.groupby("Category", as_index=False)["Sales"].sum()
    region_sales = filtered_df.groupby("Region", as_index=False)["Sales"].sum()

    # Visualizations
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Category-wise Sales")
        fig1 = px.bar(category_sales, x="Category", y="Sales", text_auto=True, template="plotly_dark")
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        st.subheader("Region-wise Sales")
        fig2 = px.pie(region_sales, values="Sales", names="Region", hole=0.4)
        st.plotly_chart(fig2, use_container_width=True)

    # Time-Series Analysis
    filtered_df["Month-Year"] = filtered_df["Order Date"].dt.to_period("M")
    time_series = filtered_df.groupby("Month-Year")["Sales"].sum().reset_index()
    time_series["Month-Year"] = time_series["Month-Year"].astype(str)

    st.subheader("Time Series Analysis")
    fig3 = px.line(time_series, x="Month-Year", y="Sales", labels={"Sales": "Amount"}, template="plotly_dark")
    st.plotly_chart(fig3, use_container_width=True)

    # Treemap Visualization
    st.subheader("Hierarchical Sales Analysis")
    fig4 = px.treemap(filtered_df, path=["Region", "Category", "Sub-Category"], values="Sales", color="Sub-Category")
    st.plotly_chart(fig4, use_container_width=True)

    # Segment Sales
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Segment-wise Sales")
        segment_sales = filtered_df.groupby("Segment", as_index=False)["Sales"].sum()
        fig5 = px.pie(segment_sales, values="Sales", names="Segment", template="plotly_dark")
        st.plotly_chart(fig5, use_container_width=True)

    with col2:
        st.subheader("Sales by Category")
        fig6 = px.pie(category_sales, values="Sales", names="Category", template="plotly")
        st.plotly_chart(fig6, use_container_width=True)

    # Scatter Plot
    st.subheader("Sales vs. Profit")
    fig7 = px.scatter(filtered_df, x="Sales", y="Profit", size="Quantity", color="Category", hover_data=["Sub-Category"])
    st.plotly_chart(fig7, use_container_width=True)

    # Download Processed Data
    csv = filtered_df.to_csv(index=False).encode("utf-8")
    st.download_button("Download Filtered Data", csv, "Filtered_Data.csv", "text/csv")

    # Additional Interactive Table
    st.subheader("Summary Table")
    sample_table = filtered_df[["Region", "State", "City", "Category", "Sales", "Profit", "Quantity"]].head(10)
    st.dataframe(sample_table.style.background_gradient(cmap="Blues"))
else:
    st.error("No data to display.")
