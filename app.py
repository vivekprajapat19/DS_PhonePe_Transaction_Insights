import streamlit as st

st.set_page_config(page_title="PhonePe Insights", layout="wide")

st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Home", "Business Case Study"])

if page == "Home":
    from home import home_page
    home_page()

elif page == "Business Case Study":
    from case_study import case_study_page
    case_study_page()
