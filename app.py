import pandas as pd
import streamlit as st

# Set Streamlit page configuration
st.set_page_config(
    page_title="Raw Material Procurement Forecaster",
    page_icon="📦",
    layout="wide",
)

st.title("📦 Raw Material Procurement Forecaster")
st.markdown(
    "Real-time supply chain inventory forecasting and reorder alert system."
)


# Generate Mock Inventory Data
@st.cache_data
def load_data():
    data = {
        "item_id": [
            "RM-001",
            "RM-002",
            "RM-003",
            "RM-004",
            "RM-005",
            "RM-006",
            "RM-007",
            "RM-008",
            "RM-009",
            "RM-010",
        ],
        "item_name": [
            "Whole Milk (L)",
            "Espresso Beans (kg)",
            "Oat Milk (L)",
            "Vanilla Syrup (L)",
            "Paper Cups (12oz)",
            "Coffee Filters",
            "Sugar Bags (kg)",
            "Matcha Powder (kg)",
            "Napkins (pack)",
            "Chocolate Sauce (L)",
        ],
        "stock_level": [50.0, 12.0, 8.0, 25.0, 1500.0, 0.0, 45.0, 2.0, 300.0, 15.0],
        "avg_daily_usage": [
            15.0,
            2.5,
            4.0,
            1.2,
            200.0,
            0.0,
            3.0,
            0.5,
            50.0,
            1.0,
        ],
        "lead_time_days": [3, 5, 3, 7, 4, 2, 6, 10, 3, 5],
    }
    return pd.DataFrame(data)


df = load_data().copy()

# Safe calculation of 'Days of Stock Remaining' to handle zero division
df["days_remaining"] = df.apply(
    lambda row: round(row["stock_level"] / row["avg_daily_usage"], 1)
    if row["avg_daily_usage"] > 0
    else (0.0 if row["stock_level"] == 0 else float("inf")),
    axis=1,
)

# Flag items requiring immediate reorder (days remaining < lead time)
df["reorder_required"] = df["days_remaining"] < df["lead_time_days"]

# Summary Metrics
total_items = len(df)
reorder_count = int(df["reorder_required"].sum())
out_of_stock_count = int((df["stock_level"] == 0).sum())

col1, col2, col3 = st.columns(3)
col1.metric("Total Tracked Items", total_items)
col2.metric(
    "Reorder Alerts", reorder_count, delta_color="inverse"
)
col3.metric("Out of Stock", out_of_stock_count, delta_color="inverse")

st.markdown("---")
st.subheader("Inventory Status Matrix")


# Styling function to highlight rows requiring reorder
def highlight_reorder(row):
    if row["reorder_required"]:
        return ["background-color: #ffcccc; color: #900c3f; font-weight: bold;"] * len(
            row
        )
    return [""] * len(row)


# Display styled DataFrame
styled_df = df.style.apply(highlight_reorder, axis=1).format(
    {"stock_level": "{:.1f}", "avg_daily_usage": "{:.1f}", "days_remaining": "{}"}
)

st.dataframe(styled_df, use_container_width=True)

# Alerts Section
if reorder_count > 0:
    st.error(
        f"🚨 **Attention Required:** {reorder_count} item(s) are below their reorder lead time threshold!"
    )
    reorder_items = df[df["reorder_required"]][
        ["item_id", "item_name", "stock_level", "days_remaining", "lead_time_days"]
    ]
    st.table(reorder_items)
else:
    st.success("✅ All inventory levels are within safe operating margins.")