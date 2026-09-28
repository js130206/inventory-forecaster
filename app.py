import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Raw Material Forecaster", page_icon="📦", layout="wide")

st.title("📦 Raw Material Procurement Forecaster")
st.markdown("Real-time supply chain inventory forecasting powered by interactive controls.")

@st.cache_data
def load_data():
    data = {
        "item_id": ["RM-001", "RM-002", "RM-003", "RM-004", "RM-005", "RM-006", "RM-007", "RM-008", "RM-009", "RM-010"],
        "item_name": ["Whole Milk (L)", "Espresso Beans (kg)", "Oat Milk (L)", "Vanilla Syrup (L)", "Paper Cups (12oz)", "Coffee Filters", "Sugar Bags (kg)", "Matcha Powder (kg)", "Napkins (pack)", "Chocolate Sauce (L)"],
        "category": ["Dairy", "Coffee", "Dairy", "Syrups", "Packaging", "Supplies", "Pantry", "Specialty", "Packaging", "Syrups"],
        "stock_level": [50.0, 12.0, 8.0, 25.0, 1500.0, 0.0, 45.0, 2.0, 300.0, 15.0],
        "avg_daily_usage": [15.0, 2.5, 4.0, 1.2, 200.0, 0.0, 3.0, 0.5, 50.0, 1.0],
        "lead_time_days": [3, 5, 3, 7, 4, 2, 6, 10, 3, 5],
    }
    return pd.DataFrame(data)

df = load_data().copy()

# ---------------- SIDEBAR CONTROLS (INTERACTIVE) ----------------
st.sidebar.header("🕹️ Live Interactive Controls")

# 1. Category Filter
categories = ["All Categories"] + list(df["category"].unique())
selected_cat = st.sidebar.selectbox("Filter by Category", categories)

# 2. Dynamic Threshold Slider
buffer_days = st.sidebar.slider("Safety Buffer Override (Days)", min_value=0, max_value=14, value=0, help="Dynamically increase buffer days to trigger early reorder alerts!")

# Apply Filters
if selected_cat != "All Categories":
    df = df[df["category"] == selected_cat]

# Dynamic Calculations based on slider
df["days_remaining"] = df.apply(
    lambda row: round(row["stock_level"] / row["avg_daily_usage"], 1)
    if row["avg_daily_usage"] > 0
    else (0.0 if row["stock_level"] == 0 else float("inf")),
    axis=1,
)

# Dynamic Reorder Flag (Lead Time + User's Buffer Slider)
df["reorder_required"] = df["days_remaining"] < (df["lead_time_days"] + buffer_days)

# ---------------- METRICS ----------------
col1, col2, col3 = st.columns(3)
col1.metric("Total Items Tracked", len(df))
col2.metric("Active Reorder Alerts", int(df["reorder_required"].sum()), delta_color="inverse")
col3.metric("Out of Stock Items", int((df["stock_level"] == 0).sum()), delta_color="inverse")

st.markdown("---")

# ---------------- PLOTLY INTERACTIVE CHART ----------------
st.subheader("📊 Visual Inventory Health (Hover & Zoom Enabled)")
fig = px.bar(
    df,
    x="item_name",
    y="days_remaining",
    color="reorder_required",
    color_discrete_map={True: "#ff4b4b", False: "#00c853"},
    labels={"days_remaining": "Days of Stock Remaining", "item_name": "Material", "reorder_required": "Reorder Needed"},
    title="Stock Days Remaining vs Reorder Threshold",
)
fig.update_layout(height=400)
st.plotly_chart(fig, use_container_width=True)

# ---------------- INTERACTIVE DATAFRAME & CSV EXPORT ----------------
st.subheader("📋 Inventory Data Matrix")

# CSV Export
csv = df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="📥 Export Current Forecast to CSV",
    data=csv,
    file_name="procurement_forecast.csv",
    mime="text/csv",
)

st.dataframe(df, use_container_width=True)