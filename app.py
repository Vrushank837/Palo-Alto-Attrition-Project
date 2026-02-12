import streamlit as st
import pandas as pd
import plotly.express as px

# Page Config
st.set_page_config(page_title="Palo Alto Networks | HR Intelligence", layout="wide")

# Load Data
@st.cache_data
def load_data():
    return pd.read_csv('data/Employee_Risk_Scores.csv')

try:
    df = load_data()
except FileNotFoundError:
    st.error("Please run 'data_processing.py' first to generate the risk scores!")
    st.stop()

# --- SIDEBAR FILTERS ---
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/7/73/Palo_Alto_Networks_logo.svg/1024px-Palo_Alto_Networks_logo.svg.png", width=200)
st.sidebar.title("Filter Panel")

selected_dept = st.sidebar.multiselect("Select Department", df['Department'].unique(), default=df['Department'].unique())
selected_risk = st.sidebar.multiselect("Risk Category", ['High Risk', 'Medium Risk', 'Low Risk'], default=['High Risk', 'Medium Risk'])

# Filter Logic
mask = (df['Department'].isin(selected_dept)) & (df['Risk_Category'].isin(selected_risk))
filtered_df = df[mask]

# --- MAIN DASHBOARD ---
st.title("🛡️ Employee Attrition Risk Dashboard")
st.markdown("Predictive Intelligence for proactive workforce retention.")

# KPIs
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Employees", len(df))
c2.metric("High Risk Count", len(df[df['Risk_Category'] == 'High Risk']))
c3.metric("Avg Risk Score", f"{df['Attrition_Probability'].mean():.1%}")
c4.metric("Potential Exits", len(filtered_df))

# Visuals
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Risk Distribution")
    fig_pie = px.pie(df, names='Risk_Category', hole=0.4, 
                     color='Risk_Category',
                     color_discrete_map={'High Risk':'#EF553B', 'Medium Risk':'#FECB52', 'Low Risk':'#00CC96'})
    st.plotly_chart(fig_pie, use_container_width=True)

with col_right:
    st.subheader("Monthly Income vs Attrition Risk")
    fig_scatter = px.scatter(filtered_df, x="MonthlyIncome", y="Attrition_Probability", 
                             color="Risk_Category", hover_data=['JobRole'],
                             color_discrete_map={'High Risk':'#EF553B', 'Medium Risk':'#FECB52'})
    st.plotly_chart(fig_scatter, use_container_width=True)

# --- INDIVIDUAL LOOKUP ---
st.divider()
st.subheader("🔍 Employee Deep-Dive")
emp_idx = st.selectbox("Select Employee by ID", filtered_df.index)

if emp_idx is not None:
    details = df.loc[emp_idx]
    detail_col1, detail_col2 = st.columns(2)
    
    with detail_col1:
        st.write(f"**Role:** {details['JobRole']}")
        st.write(f"**Years at Company:** {details['YearsAtCompany']}")
        st.write(f"**Current Status:** {details['Risk_Category']}")
        st.progress(float(details['Attrition_Probability']))
    
    with detail_col2:
        st.info(f"**Risk Score:** {details['Attrition_Probability']:.2%}")
        if details['OverTime'] == 1:
            st.warning("⚠️ Critical Factor: Working Overtime")
        if details['YearsSinceLastPromotion'] > 3:
            st.warning("⚠️ Critical Factor: Promotion Stagnation")

st.dataframe(filtered_df)