import streamlit as st
import pandas as pd
import json
import plotly.express as px
from sqlalchemy import create_engine
from db_config import db_connection


def home_page():
    st.title("PhonePe Transactions in India")

    # Load GeoJSON for India Map
    with open("C:/Users/v212p/Downloads/PhonePe_Streamlit/env/Scripts/india_states.geojson", "r", encoding="utf-8") as f:
        geojson_data = json.load(f)

    # Map state names between GeoJSON and DB
    state_name_mapping = {
        "Andaman and Nicobar": "andaman-&-nicobar-islands",
        "Andhra Pradesh": "andhra-pradesh",
        "Arunachal Pradesh": "arunachal-pradesh",
        "Assam": "assam",
        "Bihar": "bihar",
        "Chandigarh": "chandigarh",
        "Chhattisgarh": "chhattisgarh",
        "Dadra and Nagar Haveli and Daman and Diu": "dadra-&-nagar-haveli-&-daman-&-diu",
        "Delhi": "delhi",
        "Goa": "goa",
        "Gujarat": "gujarat",
        "Haryana": "haryana",
        "Himachal Pradesh": "himachal-pradesh",
        "Jammu and Kashmir": "jammu-&-kashmir",
        "Jharkhand": "jharkhand",
        "Karnataka": "karnataka",
        "Kerala": "kerala",
        "Ladakh": "ladakh",
        "Lakshadweep": "lakshadweep",
        "Madhya Pradesh": "madhya-pradesh",
        "Maharashtra": "maharashtra",
        "Manipur": "manipur",
        "Meghalaya": "meghalaya",
        "Mizoram": "mizoram",
        "Nagaland": "nagaland",
        "Odisha": "odisha",
        "Puducherry": "puducherry",
        "Punjab": "punjab",
        "Rajasthan": "rajasthan",
        "Sikkim": "sikkim",
        "Tamil Nadu": "tamil-nadu",
        "Telangana": "telangana",
        "Tripura": "tripura",
        "Uttar Pradesh": "uttar-pradesh",
        "Uttarakhand": "uttarakhand",
        "West Bengal": "west-bengal"
    }

    engine = db_connection()

    # --- Sidebar Filters ---
    st.sidebar.header("Filters")
    transaction_type = st.sidebar.selectbox("Select Transaction Type", [
        "peer-to-peer payments",
        "recharge & bill payments",
        "financial services",
        "others"
    ])
    year = st.sidebar.selectbox("Select Year", list(range(2018, 2025)))
    quarter = st.sidebar.selectbox("Select Quarter", [1, 2, 3, 4])

    # --- Geo Map ---
    query_map = f"""
        SELECT state, SUM(transaction_count) AS total_transactions, 
               SUM(transaction_amount) AS total_amount
        FROM agg_trans
        WHERE year={year} AND quarter={quarter} AND transaction_type='{transaction_type}'
        GROUP BY state
    """
    df_map = pd.read_sql(query_map, con=engine)
    df_map["state"] = df_map["state"].str.lower()

    for feature in geojson_data["features"]:
        name = feature["properties"]["NAME_1"]
        feature["properties"]["state_key"] = state_name_mapping.get(name)

    fig = px.choropleth_mapbox(
        df_map,
        geojson=geojson_data,
        featureidkey="properties.state_key",
        locations="state",
        color="total_amount",
        color_continuous_scale="Viridis",
        mapbox_style="carto-positron",
        center={"lat": 22.5937, "lon": 78.9629},
        zoom=3.5,
        opacity=0.6,
        hover_name="state",
        hover_data={"total_transactions": True, "total_amount": True}
    )
    st.plotly_chart(fig, use_container_width=True)

    # --- Category-wise Total Transactions ---
    st.subheader("Transactions")
    cat_query = f"""
        SELECT transaction_type, SUM(transaction_count) AS total_count
        FROM agg_trans
        WHERE year={year} AND quarter={quarter}
        GROUP BY transaction_type
    """
    df_cat = pd.read_sql(cat_query, con=engine)
    for idx, row in df_cat.iterrows():
        st.markdown(f"**{row['transaction_type'].title()}**: `{'{:,.0f}'.format(row['total_count'])}`")

    st.markdown("---")

    # --- Top 10 Buttons ---
    view_type = st.radio("Select View", ["States", "Districts", "Postal Codes"], horizontal=True)

    if view_type == "States":
        top_query = f"""
            SELECT state AS name, SUM(transaction_amount) AS total_amount
            FROM agg_trans
            WHERE year={year} AND quarter={quarter}
            GROUP BY state
            ORDER BY total_amount DESC
            LIMIT 10
        """
    elif view_type == "Districts":
        top_query = f"""
            SELECT transaction_type AS name, SUM(transaction_amount) AS total_amount
            FROM map_trans
            WHERE year={year} AND quarter={quarter}
            GROUP BY transaction_type
            ORDER BY total_amount DESC
            LIMIT 10
        """
    else:
        top_query = f"""
            SELECT location AS name, SUM(transaction_amount) AS total_amount
            FROM top_trans
            WHERE year={year} AND quarter={quarter}
            GROUP BY location
            ORDER BY total_amount DESC
            LIMIT 10
        """

    df_top = pd.read_sql(top_query, con=engine)

    st.subheader(f" Top 10 {view_type}")
    for idx, row in df_top.iterrows():
        amount_cr = row['total_amount'] / 1e7  # Convert to Cr
        st.markdown(f"**{idx+1}. {row['name']}** — `{amount_cr:.2f} Cr`")
