import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Load dataset
df = pd.read_csv("ecommerce_data.csv")
df['date_added'] = pd.to_datetime(df['date_added'])
df['year'] = df['date_added'].dt.year
df['month'] = df['date_added'].dt.month
df['year_month'] = df['date_added'].dt.to_period("M")
df['review_score'] = df['ratings'] * np.log1p(df['reviews'])
df['rating_level'] = pd.cut(df['ratings'], bins=[0, 2, 3.5, 4.5, 5], labels=["Poor", "Average", "Good", "Excellent"])

# Sidebar filters
st.sidebar.title(" Filter Products")
category_filter = st.sidebar.selectbox("Select Category", ["All"] + sorted(df['category'].unique().tolist()))
brand_filter = st.sidebar.selectbox("Select Brand", ["All"] + sorted(df['brand'].unique().tolist()))
segment_filter = st.sidebar.selectbox("Select Customer Segment", ["All"] + sorted(df['customer_segment'].unique().tolist()))

filtered_df = df.copy()
if category_filter != "All":
    filtered_df = filtered_df[filtered_df["category"] == category_filter]
if brand_filter != "All":
    filtered_df = filtered_df[filtered_df["brand"] == brand_filter]
if segment_filter != "All":
    filtered_df = filtered_df[filtered_df["customer_segment"] == segment_filter]

st.title(" E-Commerce Price Analysis Dashboard")

# KPIs
col1, col2, col3, col4 = st.columns(4)
col1.metric(" Avg Discount %", f"{filtered_df['discount_pct'].mean():.2f}%")
col2.metric(" Avg Rating", f"{filtered_df['ratings'].mean():.2f}")
col3.metric(" Total Reviews", int(filtered_df['reviews'].sum()))
col4.metric(" Total Products", len(filtered_df))

st.markdown("---")

# Charts
st.subheader(" Monthly Discounted Price Trend")
price_trend = filtered_df.groupby("year_month")["discounted_price"].mean().reset_index()
price_trend["year_month"] = price_trend["year_month"].astype(str)
st.plotly_chart(px.line(price_trend, x="year_month", y="discounted_price", markers=True))

st.subheader(" Average Discount % by Category")
discounts = filtered_df.groupby("category")["discount_pct"].mean().sort_values(ascending=False).reset_index()
st.plotly_chart(px.bar(discounts, x="category", y="discount_pct", color="category"))

st.subheader(" Rating Level Distribution")
rating_counts = filtered_df["rating_level"].value_counts().reset_index()
rating_counts.columns = ["rating_level", "count"]
st.plotly_chart(px.pie(rating_counts, values="count", names="rating_level", title="Rating Distribution"))

st.subheader(" Product Count by Customer Segment")
segment_counts = filtered_df["customer_segment"].value_counts().reset_index()
segment_counts.columns = ["segment", "count"]
st.plotly_chart(px.pie(segment_counts, values="count", names="segment"))

# Recommendations
st.markdown("###  Recommended for You")
top_recos = (
    filtered_df.copy()
    .assign(score=lambda d: d['ratings'] * np.log1p(d['reviews']) * (d['discount_pct'] + 1))
    .sort_values("score", ascending=False)
    .head(3)
)

for i, row in top_recos.iterrows():
    st.markdown(f"""
    <div style='background-color:#f5f5f5;padding:15px;margin-bottom:10px;border-radius:10px'>
    <b> {row['product_name']}</b><br>
     <b>Rating:</b> {row['ratings']} &nbsp;&nbsp;  <b>Reviews:</b> {row['reviews']}<br>
     <b>Discount:</b> {row['discount_pct']}% &nbsp;&nbsp;  <b>Category:</b> {row['category']}<br>
    🏷 <b>Brand:</b> {row['brand']} &nbsp;&nbsp;  <b>Segment:</b> {row['customer_segment']}
    </div>
    """, unsafe_allow_html=True)
