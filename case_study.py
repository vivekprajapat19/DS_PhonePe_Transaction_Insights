import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
from db_config import db_connection

# Reusable DB query function
def run_query(query):
    engine = db_connection()
    with engine.connect() as conn:
        return pd.read_sql(query, conn)

# ===========================
# CASE STUDY 1
# ===========================

    # Set style
sns.set(style="whitegrid")

def case_1():
    st.subheader("1. Decoding Transaction Dynamics on PhonePe")
    
    # Replace with your actual SQL query
    query = """
WITH state_trend AS (SELECT state, year, quarter, transaction_type, 
SUM(transaction_count) AS total_transactions,SUM(transaction_amount) AS total_amount,
LAG(SUM(transaction_amount)) OVER (PARTITION BY state, transaction_type ORDER BY year, quarter) AS prev_amount
FROM agg_trans GROUP BY state, year, quarter, transaction_type),
growth_analysis AS (SELECT state, year, quarter, transaction_type, total_transactions, total_amount,
(total_amount - prev_amount) / NULLIF(prev_amount, 0) * 100 AS growth_percentage
FROM state_trend), category_trend AS (SELECT transaction_type, year, quarter, 
SUM(transaction_count) AS total_transactions, SUM(transaction_amount) AS total_amount,
LAG(SUM(transaction_amount)) OVER (PARTITION BY transaction_type ORDER BY year, quarter) AS prev_amount
FROM agg_trans GROUP BY transaction_type, year, quarter), category_growth AS (SELECT 
transaction_type, year, quarter, total_transactions, total_amount,
(total_amount - prev_amount) / NULLIF(prev_amount, 0) * 100 AS growth_percentage
FROM category_trend), final_trends AS (SELECT state, transaction_type, year, quarter, total_transactions, total_amount, growth_percentage,
CASE WHEN growth_percentage > 5 THEN 'Growing'WHEN growth_percentage BETWEEN -5 AND 5 THEN 'Stable'
ELSE 'Declining' END AS trend_status FROM growth_analysis)
SELECT * FROM final_trends ORDER BY year DESC, quarter DESC, growth_percentage DESC;
"""
    df = run_query(query)

    fig1 = px.bar(df, x="transaction_type", y="total_amount", color="trend_status", barmode="group", title="Transaction Amount by Type and Trend")
    st.plotly_chart(fig1, use_container_width=True)

    fig2 = px.line(df, x="quarter", y="growth_percentage", color="transaction_type", line_group="year", title="Quarterly Growth Trend by Type")
    st.plotly_chart(fig2, use_container_width=True)

    fig3 = px.scatter(df, x="state", y="growth_percentage", color="transaction_type", size="total_amount", title="State-wise Growth by Transaction Type")
    st.plotly_chart(fig3, use_container_width=True)



    fig4 = px.box(df, x="trend_status", y="growth_percentage", color="trend_status", title="Growth Distribution by Trend Status")
    st.plotly_chart(fig4, use_container_width=True)

# ===========================
# CASE STUDY 2
# ===========================
def case_2():
    st.subheader("2. Device Dominance and User Engagement Analysis")

    query = """ 
    WITH brand_engagement AS (
        SELECT state, brand, year, quarter, 
        SUM(registered_users) AS total_registered_users, 
        SUM(app_opens) AS total_app_opens,
        (SUM(app_opens) / NULLIF(SUM(registered_users), 0)) * 100 AS engagement_rate,
        LAG(SUM(app_opens)) OVER (PARTITION BY brand ORDER BY year, quarter) AS prev_app_opens
        FROM agg_users 
        WHERE brand IS NOT NULL AND brand <> 'Unknown'  
        GROUP BY state, brand, year, quarter
    ),
    growth_analysis AS (
        SELECT *, 
        ((total_app_opens - prev_app_opens) / NULLIF(prev_app_opens, 0)) * 100 AS growth_percentage 
        FROM brand_engagement
    ) 
    SELECT * FROM growth_analysis
    ORDER BY year DESC, quarter DESC, engagement_rate DESC;
    """ 

    df = run_query(query)

    if df.empty:
        st.warning("No data available for this scenario.")
        return

    # -- Set visual style --
    sns.set(style="whitegrid")
    plt.rcParams["figure.dpi"] = 120

    fig1 = px.treemap(df, path=["brand", "state"], values="total_app_opens", title="App Opens Distribution by Brand and State")
    st.plotly_chart(fig1, use_container_width=True)

    fig2 = px.area(df, x="quarter", y="engagement_rate", color="brand", line_group="year", title="Quarterly Engagement Rate Trend by Brand")
    st.plotly_chart(fig2, use_container_width=True)

    fig3 = px.bar(df, x="brand", y="growth_percentage", color="state", barmode="group", title="Growth Percentage by Brand Across States")
    st.plotly_chart(fig3, use_container_width=True)

    fig4 = px.sunburst(df, path=["brand", "state"], values="engagement_rate", title="User Engagement Rate by Brand and State")
    st.plotly_chart(fig4, use_container_width=True)

# ===========================
# CASE STUDY 3
# ===========================
def case_3():
    st.subheader("3. Insurance Penetration and Growth Potential Analysis")

    query = """ 
    WITH insurance_trend AS (
        SELECT state, year, quarter, insurance_type, 
               SUM(insurance_count) AS total_policies, 
               SUM(insurance_amount) AS total_value,
               LAG(SUM(insurance_amount)) OVER (
                   PARTITION BY state, insurance_type ORDER BY year, quarter
               ) AS prev_value
        FROM map_insur 
        GROUP BY state, year, quarter, insurance_type
    ), 
    penetration_analysis AS (
        SELECT mi.state, mi.year, mi.quarter, mi.insurance_type, 
               (SUM(mi.insurance_count) * 100.0) / NULLIF(SUM(at.transaction_count), 0) AS penetration_rate
        FROM map_insur mi 
        JOIN agg_trans at USING (state, year, quarter)
        GROUP BY mi.state, mi.year, mi.quarter, mi.insurance_type
    )
    SELECT 
        it.state, it.year, it.quarter, it.insurance_type, 
        it.total_policies, it.total_value, 
        (it.total_value - it.prev_value) / NULLIF(it.prev_value, 0) * 100 AS growth_percentage, 
        pa.penetration_rate 
    FROM insurance_trend it 
    JOIN penetration_analysis pa 
    USING (state, year, quarter, insurance_type) 
    ORDER BY growth_percentage DESC, penetration_rate DESC;
    """ 

    df = run_query(query)

    if df.empty:
        st.warning("No data available for this scenario.")
        return

    sns.set(style="whitegrid")

    fig1 = px.bar(df.sort_values("growth_percentage", ascending=False).head(10),
              x="growth_percentage", y="state", color="insurance_type", orientation='h',
              title="Top 10 States by Insurance Growth (%)")
    st.plotly_chart(fig1, use_container_width=True)


    fig2 = px.scatter(df, x="total_policies", y="penetration_rate", color="insurance_type",
                  size="total_value", title="Policies vs Penetration Rate")
    st.plotly_chart(fig2, use_container_width=True)


    fig3 = px.bar(df, x="state", y="penetration_rate", color="insurance_type", barmode="group",
              title="Penetration Rate by Insurance Type and State")
    st.plotly_chart(fig3, use_container_width=True)


    fig4 = px.bar(df, x="state", y="total_value", color="insurance_type", 
              barmode="group", title="Total Insurance Value by Insurance Type and State")
    st.plotly_chart(fig4, use_container_width=True)












# ===========================
# CASE STUDY 4
# ===========================
def case_4():
    st.subheader("4. Transaction Analysis for Market Expansion")

    query = """
    WITH state_growth AS (SELECT state, year, quarter
, SUM(transaction_count) AS total_transactions, 
SUM(transaction_amount) AS total_amount,LAG(SUM(transaction_amount)) 
OVER (PARTITION BY state ORDER BY year, quarter) AS prev_amount FROM agg_trans
GROUP BY state, year, quarter) SELECT state, SUM(total_transactions) AS total_transactions,
SUM(total_amount) AS total_transaction_amount,
ROUND(AVG((total_amount - prev_amount) / NULLIF(prev_amount, 0) * 100), 2) AS avg_growth_rate 
FROM state_growth GROUP BY state ORDER BY avg_growth_rate DESC, total_transaction_amount DESC;
"""

    df = run_query(query)

    fig1 = px.bar(df, x="state", y="total_transactions", title="Top state by total Transactions")
    st.plotly_chart(fig1, use_container_width=True)

    fig2 = px.bar(df.melt(id_vars="state", 
                      value_vars=["total_transaction_amount", "total_transactions"], 
                      var_name="Metric", value_name="Value"),
              x="state", y="Value", color="Metric", barmode="group",
              title="Total Transactions vs Transaction Amount by State")
    st.plotly_chart(fig2, use_container_width=True)


    fig3 = px.scatter(df, x="avg_growth_rate", y="total_transaction_amount",size="total_transactions", color="state",
                      title="Transaction Amount vs Avg Growth Rate by State",
                      labels={"avg_growth_rate": "Avg Growth Rate (%)", "total_transaction_amount": "Total Amount"})
    st.plotly_chart(fig3, use_container_width=True)


    fig4 = px.funnel(df, x="total_transaction_amount", y="state", title="state-wise Transaction Funnel")
    st.plotly_chart(fig4, use_container_width=True)

# ===========================
# CASE STUDY 5
# ===========================
def case_5():
    st.subheader("5. Transaction Analysis Across States and Districts")

    query = """
    WITH state_transaction AS (SELECT state, SUM(transaction_count) AS total_transactions, 
SUM(transaction_amount) AS total_amount FROM agg_trans GROUP BY state), district_transaction AS (
SELECT location AS district, SUM(transaction_count) AS total_transactions, 
SUM(transaction_amount) AS total_amount FROM top_trans GROUP BY location)
SELECT 'State' AS category, state AS name, total_transactions, total_amount
FROM state_transaction UNION ALL SELECT 'District', district, total_transactions, total_amount
FROM district_transaction ORDER BY total_amount DESC;
"""
    df = run_query(query)

    fig1 = px.bar(df, x='name', y='total_amount', color='category',title='Transaction Amount by States and Districts',
              labels={'name': 'Location', 'total_amount': 'Total Amount'},barmode='group')
    fig1.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig1, use_container_width=True)

    fig2 = px.bar(df, x="category", y="total_transactions", title="category vs total_Transactions")
    st.plotly_chart(fig2, use_container_width=True)

    fig3 = px.line(df, x="name", y="total_amount", color="category", markers=True,
               title="Transaction Amount by Location and Category",
               labels={"name": "Location", "total_amount": "Transaction Amount"})
    fig3.update_layout(xaxis_tickangle=45)
    st.plotly_chart(fig3, use_container_width=True)


    fig4 = px.scatter(df, x="name", y="total_amount", size="total_transactions", color="category",
                  title="Transaction Amount vs Location by Category",
                  labels={"name": "Location", "total_amount": "Transaction Amount", "total_transactions": "Total Transactions"})
    fig4.update_traces(marker=dict(opacity=0.7, line=dict(width=1, color='DarkSlateGrey')))
    fig4.update_layout(xaxis_tickangle=45)
    st.plotly_chart(fig4, use_container_width=True)


# ===========================
# MAIN FUNCTION
# ===========================
def business_case_study():
    st.title("📊 Business Case Study Visualizations")

    options = [
        "1. Decoding Transaction Dynamics on PhonePe",
        "2. Device Dominance and User Engagement Analysis",
        "3. Insurance Penetration and Growth Potential Analysis",
        "4. Transaction Analysis for Market Expansion",
        "5. Transaction Analysis Across States and Districts"
    ]

    selection = st.selectbox("Choose a Case Study", options)

    if "1." in selection:
        case_1()
    elif "2." in selection:
        case_2()
    elif "3." in selection:
        case_3()
    elif "4." in selection:
        case_4()
    elif "5." in selection:
        case_5()

def case_study_page():
    business_case_study()
