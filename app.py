"""
Streamlit Inventory Management App
Features:
  - KPI metric cards
  - Plotly gauge charts per product
  - Reorder alerts table with CSV export
  - Supply distribution bar + pie charts
"""

import io
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Inventory Dashboard",
    page_icon="📦",
    layout="wide",
)

# ── Data layer ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_data(uploaded_file=None) -> pd.DataFrame:
    """Return inventory DataFrame from upload or built-in sample."""
    if uploaded_file is not None:
        return pd.read_csv(uploaded_file)

    # Sample data — replace with your real source
    return pd.DataFrame(
        {
            "Product":     ["Widget A", "Widget B", "Gadget X", "Gadget Y",
                            "Part Z",   "Part W",   "Tool M",   "Tool N"],
            "Category":    ["Widgets", "Widgets", "Gadgets", "Gadgets",
                            "Parts",   "Parts",   "Tools",   "Tools"],
            "Stock":       [120, 8, 0, 45, 15, 200, 3, 60],
            "Reorder_At":  [50, 20, 10, 30, 25, 100, 10, 40],
            "Unit_Price":  [9.99, 14.99, 29.99, 24.99, 4.99, 2.49, 39.99, 19.99],
        }
    )


def to_csv_bytes(df: pd.DataFrame) -> bytes:
    """Serialize a DataFrame to UTF-8 CSV bytes."""
    buf = io.StringIO()
    df.to_csv(buf, index=False)
    return buf.getvalue().encode("utf-8")


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Controls")
    uploaded = st.file_uploader("Upload CSV", type="csv")
    df = load_data(uploaded)

    categories = ["All"] + sorted(df["Category"].unique().tolist())
    selected_cat = st.selectbox("Category", categories)

    threshold = st.slider(
        "Reorder threshold override",
        min_value=0,
        max_value=int(df["Stock"].max()),
        value=0,
        help="0 = use each product's own Reorder_At value",
    )

st.title("📦 Inventory Dashboard")
st.caption("Real-time stock health, reorder alerts, and supply distribution.")

# ── Apply filters ──────────────────────────────────────────────────────────────
filtered = df.copy() if selected_cat == "All" else df[df["Category"] == selected_cat].copy()

# Effective reorder point: use override if > 0
filtered["Effective_Reorder"] = filtered["Reorder_At"].where(threshold == 0, threshold)
filtered["Status"] = pd.cut(
    filtered["Stock"],
    bins=[-1, 0, filtered["Effective_Reorder"].max(), float("inf")],
    labels=["Out of Stock", "Low Stock", "OK"],
)

alerts = filtered[filtered["Stock"] <= filtered["Effective_Reorder"]].copy()

# ── KPI row ────────────────────────────────────────────────────────────────────
total_products  = len(filtered)
low_stock_count = int((filtered["Stock"] < filtered["Effective_Reorder"]).sum())
out_of_stock    = int((filtered["Stock"] == 0).sum())
total_value     = (filtered["Stock"] * filtered["Unit_Price"]).sum()

k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Products",  total_products)
k2.metric("⚠️ Low Stock",    low_stock_count, delta=f"-{low_stock_count}" if low_stock_count else None, delta_color="inverse")
k3.metric("🚨 Out of Stock", out_of_stock,    delta=f"-{out_of_stock}"    if out_of_stock    else None, delta_color="inverse")
k4.metric("💰 Stock Value",  f"${total_value:,.2f}")

st.divider()

# ── Gauge charts ───────────────────────────────────────────────────────────────
st.subheader("📊 Stock Level Gauges")
st.caption("Each gauge shows current stock relative to its reorder point (red) and a healthy buffer (green).")

gauge_items = filtered.head(6)          # cap at 6 to keep the row readable
cols = st.columns(len(gauge_items))

for col, (_, row) in zip(cols, gauge_items.iterrows()):
    healthy = int(row["Effective_Reorder"] * 2)
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=row["Stock"],
            title={"text": row["Product"], "font": {"size": 13}},
            gauge={
                "axis":  {"range": [0, max(healthy, row["Stock"] + 10)]},
                "bar":   {"color": "#1f77b4"},
                "steps": [
                    {"range": [0,                     row["Effective_Reorder"]], "color": "#ff4b4b"},
                    {"range": [row["Effective_Reorder"], healthy],               "color": "#ffa500"},
                    {"range": [healthy,               max(healthy, row["Stock"] + 10)], "color": "#2ca02c"},
                ],
                "threshold": {
                    "line":  {"color": "red", "width": 3},
                    "thickness": 0.75,
                    "value": row["Effective_Reorder"],
                },
            },
        )
    )
    fig.update_layout(height=220, margin=dict(t=40, b=10, l=10, r=10))
    col.plotly_chart(fig, use_container_width=True)

st.divider()

# ── Reorder alerts + CSV export ────────────────────────────────────────────────
st.subheader("🚨 Reorder Alerts")

if alerts.empty:
    st.success("All products are above their reorder points. ✅")
else:
    st.warning(f"{len(alerts)} product(s) need restocking.")

    display_cols = ["Product", "Category", "Stock", "Reorder_At", "Unit_Price"]
    st.dataframe(
        alerts[display_cols].style.applymap(
            lambda v: "background-color: #ff4b4b; color: white;" if v == 0 else "",
            subset=["Stock"],
        ),
        use_container_width=True,
        hide_index=True,
    )

    st.download_button(
        label="⬇️ Download Reorder Alerts as CSV",
        data=to_csv_bytes(alerts[display_cols]),
        file_name="reorder_alerts.csv",
        mime="text/csv",
        type="primary",
    )

st.divider()

# ── Supply distribution ────────────────────────────────────────────────────────
st.subheader("📦 Supply Distribution")

chart_col, pie_col = st.columns([2, 1])

with chart_col:
    bar_fig = px.bar(
        filtered.sort_values("Stock"),
        x="Product",
        y="Stock",
        color="Category",
        text="Stock",
        title="Stock by Product",
        labels={"Stock": "Units in Stock"},
    )
    bar_fig.update_traces(textposition="outside")
    bar_fig.update_layout(xaxis_tickangle=-35, height=380)
    st.plotly_chart(bar_fig, use_container_width=True)

with pie_col:
    cat_totals = filtered.groupby("Category", as_index=False)["Stock"].sum()
    pie_fig = px.pie(
        cat_totals,
        names="Category",
        values="Stock",
        title="Stock Share by Category",
        hole=0.4,
    )
    pie_fig.update_traces(textposition="inside", textinfo="percent+label")
    pie_fig.update_layout(height=380, showlegend=False)
    st.plotly_chart(pie_fig, use_container_width=True)