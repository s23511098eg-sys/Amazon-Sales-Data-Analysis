import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# -------------------------------
# Page Configuration
# -------------------------------
st.set_page_config(
    page_title="Amazon Sales Dashboard",
    page_icon="📊",
    layout="wide"
)

# -------------------------------
# Colors
# -------------------------------
PRIMARY = "#1B2A4A"
SECONDARY = "#E8963C"
BACKGROUND = "#F7F3EC"

st.markdown(f"""
<style>

.main {{
    background-color:{BACKGROUND};
}}

h1,h2,h3{{
color:{PRIMARY};
}}

div[data-testid="stMetric"]{{
background:black;
padding:15px;
border-radius:10px;
border-left:6px solid {SECONDARY};
}}

section[data-testid="stSidebar"]{{
background-color:{PRIMARY};
}}

section[data-testid="stSidebar"] *{{
color:white;
}}

</style>
""",unsafe_allow_html=True)

# -------------------------------
# Load Data
# -------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@st.cache_data
def load_data():

    path = os.path.join(BASE_DIR,"Amazon Sales.csv")

    df = pd.read_csv(path)

    df["Date"] = pd.to_datetime(df["Date"],format="%d/%m/%y")

    return df

df = load_data()

# -------------------------------
# Feature Engineering
# -------------------------------

df["Month"] = df["Date"].dt.month_name()

df["Year"] = df["Date"].dt.year

df["Day"] = df["Date"].dt.day_name()

df["Sales Per Item"] = df["Amount"]/df["Qty"]

df["Sales Per Item"] = df["Sales Per Item"].fillna(0)

# -------------------------------
# Sidebar
# -------------------------------

st.sidebar.title("📊 Amazon Dashboard")

page = st.sidebar.radio(

"Navigation",

[
"Home",
"Data Understanding",
"Data Cleaning",
"Feature Engineering",
"EDA",
"Business Analysis"
]

)

st.sidebar.markdown("---")

min_date = df["Date"].min().date()

max_date = df["Date"].max().date()

date_range = st.sidebar.date_input(

"Select Date",

(min_date,max_date)

)

categories = sorted(df["Category"].dropna().unique())

selected_category = st.sidebar.multiselect(

"Category",

categories,

default=categories

)

states = sorted(df["ship-state"].dropna().unique())

selected_state = st.sidebar.multiselect(

"State",

states,

default=states

)

# -------------------------------
# Filters
# -------------------------------

if len(date_range)==2:

    start_date,end_date=date_range

else:

    start_date=min_date
    end_date=max_date

filtered_df=df[

(df["Date"].dt.date>=start_date)&
(df["Date"].dt.date<=end_date)

]

filtered_df=filtered_df[
filtered_df["Category"].isin(selected_category)
]

filtered_df=filtered_df[
filtered_df["ship-state"].isin(selected_state)
]

# ======================================================
# HOME PAGE
# ======================================================

if page == "Home":

    st.title("📦 Amazon Sales Dashboard")

    st.write(
        "This dashboard provides an interactive analysis of Amazon sales data."
    )

    # ---------------- KPIs ---------------- #

    total_orders = filtered_df["Order ID"].nunique()
    total_sales = filtered_df["Amount"].sum()
    total_quantity = filtered_df["Qty"].sum()
    average_sales = filtered_df["Amount"].mean()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Orders", f"{total_orders:,}")

    col2.metric("Total Sales", f"₹ {total_sales:,.2f}")

    col3.metric("Total Quantity", f"{total_quantity:,}")

    col4.metric("Average Sales", f"₹ {average_sales:,.2f}")

    st.markdown("---")

    # =====================================================
    # Monthly Sales
    # =====================================================

    st.subheader("Monthly Sales")

    monthly_sales = (
        filtered_df
        .groupby("Month")["Amount"]
        .sum()
        .reset_index()
    )

    month_order = [
        "January","February","March","April",
        "May","June","July","August",
        "September","October","November","December"
    ]

    monthly_sales["Month"] = pd.Categorical(
        monthly_sales["Month"],
        categories=month_order,
        ordered=True
    )

    monthly_sales = monthly_sales.sort_values("Month")

    fig = px.line(
        monthly_sales,
        x="Month",
        y="Amount",
        markers=True,
        color_discrete_sequence=["#E8963C"]
    )

    st.plotly_chart(fig, use_container_width=True)

    # =====================================================
    # Category Distribution
    # =====================================================

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("Orders by Category")

        category = (
            filtered_df["Category"]
            .value_counts()
            .reset_index()
        )

        category.columns = ["Category", "Orders"]

        fig = px.bar(
            category,
            x="Category",
            y="Orders",
            color="Category"
        )

        st.plotly_chart(fig, use_container_width=True)

    with col2:

        st.subheader("Sales by Category")

        sales_category = (
            filtered_df
            .groupby("Category")["Amount"]
            .sum()
            .reset_index()
        )

        fig = px.pie(
            sales_category,
            names="Category",
            values="Amount",
            hole=0.5
        )

        st.plotly_chart(fig, use_container_width=True)

    # =====================================================
    # Order Status
    # =====================================================

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("Order Status")

        status = (
            filtered_df["Status"]
            .value_counts()
            .reset_index()
        )

        status.columns = ["Status", "Count"]

        fig = px.bar(
            status,
            x="Status",
            y="Count",
            color="Status"
        )

        st.plotly_chart(fig, use_container_width=True)

    with col2:

        st.subheader("Top 10 States")

        state = (
            filtered_df["ship-state"]
            .value_counts()
            .head(10)
            .reset_index()
        )

        state.columns = ["State", "Orders"]

        fig = px.bar(
            state,
            x="Orders",
            y="State",
            orientation="h",
            color="Orders"
        )

        st.plotly_chart(fig, use_container_width=True)
        
# ======================================================
# DATA UNDERSTANDING
# ======================================================

elif page == "Data Understanding":

    st.title("📋 Data Understanding")

    st.write(
        "This page provides an overview of the dataset before any analysis."
    )

    st.subheader("Dataset Shape")

    rows, cols = df.shape

    col1, col2 = st.columns(2)

    col1.metric("Rows", rows)

    col2.metric("Columns", cols)

    st.markdown("---")

    st.subheader("Columns")

    st.dataframe(pd.DataFrame(df.columns, columns=["Column Name"]))

    st.markdown("---")

    st.subheader("Data Types")

    datatype = pd.DataFrame(df.dtypes, columns=["Data Type"])

    st.dataframe(datatype)

    st.markdown("---")

    st.subheader("Missing Values")

    missing = pd.DataFrame(
        df.isnull().sum(),
        columns=["Missing Values"]
    )

    st.dataframe(missing)

    st.markdown("---")

    st.subheader("First Five Rows")

    st.dataframe(df.head())

    st.markdown("---")

    st.subheader("Statistical Summary")

    st.dataframe(df.describe())


# ======================================================
# DATA CLEANING
# ======================================================

elif page == "Data Cleaning":

    st.title("🧹 Data Cleaning")

    st.write(
        "This page shows the cleaning process applied to the dataset."
    )

    st.subheader("Missing Values Before Cleaning")

    before = pd.DataFrame(
        df.isnull().sum(),
        columns=["Missing Values"]
    )

    st.dataframe(before)

    st.markdown("---")

    clean_df = df.copy()

    clean_df = clean_df.dropna()

    clean_df = clean_df.drop_duplicates()

    st.success("Missing values and duplicate rows removed successfully.")

    st.subheader("Missing Values After Cleaning")

    after = pd.DataFrame(
        clean_df.isnull().sum(),
        columns=["Missing Values"]
    )

    st.dataframe(after)

    st.markdown("---")

    st.subheader("Duplicate Rows")

    st.write("Duplicates:", clean_df.duplicated().sum())

    st.markdown("---")

    st.subheader("Clean Dataset Preview")

    st.dataframe(clean_df.head())


# ======================================================
# FEATURE ENGINEERING
# ======================================================

elif page == "Feature Engineering":

    st.title("⚙️ Feature Engineering")

    st.write(
        "New features were created from the Date and Amount columns."
    )

    feature_df = df.copy()

    feature_df["Month"] = feature_df["Date"].dt.month_name()

    feature_df["Year"] = feature_df["Date"].dt.year

    feature_df["Day"] = feature_df["Date"].dt.day_name()

    feature_df["Sales Per Item"] = (
        feature_df["Amount"] /
        feature_df["Qty"]
    )

    feature_df["Sales Per Item"] = feature_df["Sales Per Item"].fillna(0)

    st.subheader("New Features")

    st.dataframe(
        feature_df[
            [
                "Date",
                "Month",
                "Year",
                "Day",
                "Qty",
                "Amount",
                "Sales Per Item"
            ]
        ].head(10)
    )

    st.markdown("---")

    st.subheader("Month Distribution")

    fig = px.histogram(
        feature_df,
        x="Month",
        color="Month"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.markdown("---")

    st.subheader("Sales Per Item Distribution")

    fig = px.histogram(
        feature_df,
        x="Sales Per Item",
        nbins=40
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )
    
# ======================================================
# EXPLORATORY DATA ANALYSIS (EDA)
# ======================================================

elif page == "EDA":

    st.title("📈 Exploratory Data Analysis")

    st.write("Explore the Amazon Sales dataset using interactive charts.")

    # -------------------------------------------------
    # Sales by Category
    # -------------------------------------------------

    st.subheader("Sales by Category")

    sales_category = (
        filtered_df.groupby("Category")["Amount"]
        .sum()
        .reset_index()
        .sort_values("Amount", ascending=False)
    )

    fig = px.bar(
        sales_category,
        x="Category",
        y="Amount",
        color="Category"
    )

    st.plotly_chart(fig, use_container_width=True)

    # -------------------------------------------------
    # Sales by State
    # -------------------------------------------------

    st.subheader("Top 10 States by Sales")

    state_sales = (
        filtered_df.groupby("ship-state")["Amount"]
        .sum()
        .nlargest(10)
        .reset_index()
    )

    fig = px.bar(
        state_sales,
        x="ship-state",
        y="Amount",
        color="Amount"
    )

    st.plotly_chart(fig, use_container_width=True)

    # -------------------------------------------------
    # Monthly Sales
    # -------------------------------------------------

    st.subheader("Monthly Sales")

    monthly = (
        filtered_df.groupby("Month")["Amount"]
        .sum()
        .reset_index()
    )

    month_order = [
        "January","February","March","April",
        "May","June","July","August",
        "September","October","November","December"
    ]

    monthly["Month"] = pd.Categorical(
        monthly["Month"],
        categories=month_order,
        ordered=True
    )

    monthly = monthly.sort_values("Month")

    fig = px.line(
        monthly,
        x="Month",
        y="Amount",
        markers=True
    )

    st.plotly_chart(fig, use_container_width=True)

    # -------------------------------------------------
    # Order Status
    # -------------------------------------------------

    st.subheader("Order Status")

    status = (
        filtered_df["Status"]
        .value_counts()
        .reset_index()
    )

    status.columns = ["Status","Orders"]

    fig = px.pie(
        status,
        names="Status",
        values="Orders"
    )

    st.plotly_chart(fig, use_container_width=True)

    # -------------------------------------------------
    # Quantity Distribution
    # -------------------------------------------------

    st.subheader("Quantity Distribution")

    fig = px.histogram(
        filtered_df,
        x="Qty",
        nbins=20
    )

    st.plotly_chart(fig, use_container_width=True)

    # -------------------------------------------------
    # Correlation
    # -------------------------------------------------

    st.subheader("Correlation")

    corr = filtered_df[["Qty","Amount"]].corr()

    fig = px.imshow(
        corr,
        text_auto=True,
        color_continuous_scale="Blues"
    )

    st.plotly_chart(fig, use_container_width=True)


# ======================================================
# BUSINESS ANALYSIS
# ======================================================

elif page == "Business Analysis":

    st.title("💼 Business Analysis")

    st.write("Business insights extracted from the dataset.")

    # ------------------------------------------

    st.subheader("Top 10 Products")

    top_products = (
        filtered_df.groupby("Category")["Amount"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
        .head(10)
    )

    fig = px.bar(
        top_products,
        x="Category",
        y="Amount",
        color="Amount"
    )

    st.plotly_chart(fig, use_container_width=True)

    # ------------------------------------------

    st.subheader("Sales by Fulfilment")

    fulfilment = (
        filtered_df.groupby("Fulfilment")["Amount"]
        .sum()
        .reset_index()
    )

    fig = px.pie(
        fulfilment,
        names="Fulfilment",
        values="Amount"
    )

    st.plotly_chart(fig, use_container_width=True)

    # ------------------------------------------

    st.subheader("Sales by Courier Status")

    courier = (
        filtered_df.groupby("Courier Status")["Amount"]
        .sum()
        .reset_index()
    )

    fig = px.bar(
        courier,
        x="Courier Status",
        y="Amount",
        color="Courier Status"
    )

    st.plotly_chart(fig, use_container_width=True)

    # ------------------------------------------

    st.subheader("Sales by Size")

    size = (
        filtered_df.groupby("Size")["Amount"]
        .sum()
        .reset_index()
    )

    fig = px.bar(
        size,
        x="Size",
        y="Amount",
        color="Size"
    )

    st.plotly_chart(fig, use_container_width=True)

    # ------------------------------------------

    st.subheader("B2B Orders")

    b2b = (
        filtered_df["B2B"]
        .value_counts()
        .reset_index()
    )

    b2b.columns = ["B2B","Orders"]

    fig = px.pie(
        b2b,
        names="B2B",
        values="Orders"
    )

    st.plotly_chart(fig, use_container_width=True)

    # ------------------------------------------

    st.subheader("Summary")

    st.success(f"✔ Total Sales : ₹ {filtered_df['Amount'].sum():,.2f}")

    st.success(f"✔ Total Orders : {filtered_df['Order ID'].nunique():,}")

    st.success(f"✔ Average Order Value : ₹ {filtered_df['Amount'].mean():,.2f}")

    st.success(f"✔ Best Category : {filtered_df['Category'].mode()[0]}")

    st.success(f"✔ Highest Sales State : {filtered_df.groupby('ship-state')['Amount'].sum().idxmax()}")