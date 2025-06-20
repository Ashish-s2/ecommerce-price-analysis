import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Load data
df = pd.read_csv("ecommerce_data.csv")
df['date_added'] = pd.to_datetime(df['date_added'])
df['year'] = df['date_added'].dt.year
df['month'] = df['date_added'].dt.month
df['year_month'] = df['date_added'].dt.to_period("M").astype(str)
df['review_score'] = df['ratings'] * np.log1p(df['reviews'])
df['rating_level'] = pd.cut(df['ratings'], bins=[0, 2, 3.5, 4.5, 5], labels=["Poor", "Average", "Good", "Excellent"])
df['is_outlier'] = df['discount_pct'] > 50

st.set_page_config(page_title="E-Commerce Pro Dashboard", layout="wide")

# Sidebar filters
st.sidebar.title("🔍 Filters")
category_filter = st.sidebar.selectbox("Select Category", ["All"] + sorted(df['category'].unique().tolist()))
brand_filter = st.sidebar.selectbox("Select Brand", ["All"] + sorted(df['brand'].unique().tolist()))
segment_filter = st.sidebar.selectbox("Select Customer Segment", ["All"] + sorted(df['customer_segment'].unique().tolist()))
outlier_threshold = st.sidebar.slider("Outlier Discount % Threshold", 10, 90, 50)

# Filtered data
filtered_df = df.copy()
if category_filter != "All":
    filtered_df = filtered_df[filtered_df["category"] == category_filter]
if brand_filter != "All":
    filtered_df = filtered_df[filtered_df["brand"] == brand_filter]
if segment_filter != "All":
    filtered_df = filtered_df[filtered_df["customer_segment"] == segment_filter]

st.title("📈 E-Commerce Price Intelligence Dashboard (Pro Version)")

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Overview", "📈 Trends", "🧍 Segments", "🔥 Outliers", "🎯 Recommendations"])

with tab1:
    st.subheader("Key Metrics")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💸 Avg Discount %", f"{filtered_df['discount_pct'].mean():.2f}%")
    col2.metric("⭐ Avg Rating", f"{filtered_df['ratings'].mean():.2f}")
    col3.metric("🗣️ Total Reviews", int(filtered_df['reviews'].sum()))
    col4.metric("📦 Total Products", len(filtered_df))

    st.subheader("📋 Product Explorer")
    st.dataframe(filtered_df[['product_name', 'category', 'brand', 'discounted_price', 'ratings', 'reviews', 'customer_segment']])

with tab2:
    st.subheader("YOY & MOM Price Trend")
    trend_data = filtered_df.groupby("year_month")["discounted_price"].mean().reset_index()
    st.plotly_chart(px.line(trend_data, x="year_month", y="discounted_price", markers=True, title="Monthly Avg Price"))

    st.subheader("📊 Discount % by Category")
    cat_discount = filtered_df.groupby("category")["discount_pct"].mean().sort_values(ascending=False).reset_index()
    st.plotly_chart(px.bar(cat_discount, x="category", y="discount_pct", color="category"))

with tab3:
    st.subheader("Customer Segment Comparison")
    seg_metrics = filtered_df.groupby("customer_segment").agg({
        "discounted_price": "mean", "ratings": "mean", "reviews": "sum"
    }).reset_index()
    st.plotly_chart(px.bar(seg_metrics, x="customer_segment", y="discounted_price", color="customer_segment", title="Avg Price"))
    st.plotly_chart(px.bar(seg_metrics, x="customer_segment", y="ratings", color="customer_segment", title="Avg Rating"))

with tab4:
    st.subheader(f"🔥 Outliers (Discount > {outlier_threshold}%)")
    outliers = filtered_df[filtered_df['discount_pct'] > outlier_threshold]
    if len(outliers) > 0:
        st.dataframe(outliers[['product_name', 'discount_pct', 'ratings', 'reviews', 'category', 'brand']])
        outlier_hist = outliers.groupby("year_month")["discount_pct"].count().reset_index()
        outlier_hist.columns = ["year_month", "outlier_count"]
        st.plotly_chart(px.bar(outlier_hist, x="year_month", y="outlier_count", title="Outlier Count Over Time"))
    else:
        st.info("No outliers above selected threshold.")

with tab5:
    st.subheader("🧠 Recommended for You")
    top_recos = (
        filtered_df.copy()
        .assign(score=lambda d: d['ratings'] * np.log1p(d['reviews']) * (d['discount_pct'] + 1))
        .sort_values("score", ascending=False)
        .head(3)
    )

    for i, row in top_recos.iterrows():
        st.markdown(f"""
        <div style='background-color:#f8f9fa;padding:15px;margin-bottom:10px;border-radius:10px'>
        <b>📦 {row['product_name']}</b><br>
        ⭐ <b>Rating:</b> {row['ratings']} &nbsp;&nbsp; 💬 <b>Reviews:</b> {row['reviews']}<br>
        💸 <b>Discount:</b> {row['discount_pct']}% &nbsp;&nbsp; 📂 <b>Category:</b> {row['category']}<br>
        🏷️ <b>Brand:</b> {row['brand']} &nbsp;&nbsp; 👥 <b>Segment:</b> {row['customer_segment']}
        </div>
        """, unsafe_allow_html=True)
