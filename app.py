import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import altair as alt
import datetime

# ---------- Page Config ----------
st.set_page_config(
    layout="wide",
    initial_sidebar_state="expanded"
)
# ---------- Theme Toggle in Header ----------
# ---------- Theme Toggle in Header ----------
if "theme" not in st.session_state:
    st.session_state.theme = "light"

# Header with title + toggle button
col1, col2 = st.columns([9,1])  # 9:1 ratio pushes toggle to right
with col1:
    st.markdown("<h1>📊 SmartDash — Small Biz Dashboard</h1>", unsafe_allow_html=True)
with col2:
    if st.button("🌗 Theme"):
        st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"

# Apply styles
if st.session_state.theme == "light":
    st.markdown("""
    <style>
    .stApp {
        background: #ffffff;
        color: #000000 !important;
        font-weight: bold;
    }
    .card {
        background: #ffffff;
        color: #000000;
    }
    .footer {
        background: #f0f0f0;
        color: #000000;
    }
    </style>
    """, unsafe_allow_html=True)

else:  # dark mode
    st.markdown("""
    <style>
    .stApp {
        background: #000000;
        color: #ffffff !important;
    }
    .card {
        background: #1c1c1c;
        color: #ffffff;
    }
    .footer {
        background: #111111;
        color: #ffffff;
    }
    </style>
    """, unsafe_allow_html=True)

# ---------- Modern CSS ----------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(to bottom right, #e9f5ff, #f9fcff);
    font-family: 'Segoe UI', sans-serif;
}
.card {
    background: rgba(255, 255, 255, 0.75);
    padding: 20px;
    border-radius: 14px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.05);
    backdrop-filter: blur(10px);
}
.kpi-value {
    font-size: 1.6rem;
    font-weight: bold;
}
.kpi-label {
    color: #6b7280;
    font-size: 0.9rem;
}
.footer {
    margin-top: 50px;
    padding: 20px;
    border-top: 1px solid #e5e7eb;
    background: rgba(255, 255, 255, 0.5);
}
</style>
""", unsafe_allow_html=True)

st.write("A modern, simple, and mobile-friendly dashboard for small business sales analysis.")

# ---------- File Upload ----------
uploaded_file = st.file_uploader("📂 Upload your sales data (CSV only)", type=["csv"])

if uploaded_file is None:
    st.info("👆 Please upload a CSV file to get started.")
    
    # Show sample data info or instructions
    st.subheader("📋 Sample Data Format")
    st.write("Your CSV should contain columns like:")
    sample_cols = ["Date", "Product", "Category", "Region", "Sales Amount", "Quantity", "Unit Price", "Sales Rep"]
    st.write("• " + "\n• ".join(sample_cols))
    
else:
    with st.spinner("Reading file..."):
        try:
            df = pd.read_csv(uploaded_file)
        except Exception as e:
            st.error(f"Error reading file: {e}")
            df = None
    
    if df is not None:
        # ---------- Column Detection ----------
        df_columns_lower = {c.lower().strip(): c for c in df.columns}
        
        def find_first(cols_candidates):
            for cand in cols_candidates:
                for lower, orig in df_columns_lower.items():
                    if cand in lower:
                        return orig
            return None
        
        # Auto-detect
        sale_date_col = find_first(["sale_date", "date", "order_date", "transaction_date"])
        product_col = find_first(["product_name", "product", "product_id", "item"])
        category_col = find_first(["category", "product_category"])
        region_col = find_first(["region", "state", "location"])
        sales_amount_col = find_first(["sales_amount", "total", "amount", "sales"])
        quantity_col = find_first(["quantity", "qty", "units", "items"])
        unit_price_col = find_first(["unit_price", "price", "item price"])
        unit_cost_col = find_first(["unit_cost", "cost"])
        sales_rep_col = find_first(["sales_rep", "salesperson", "rep"])
        
        # ---------- Session-state for user selections ----------
        if "cols" not in st.session_state:
            st.session_state.cols = {
                "date": sale_date_col or "None",
                "product": product_col or "None",
                "category": category_col or "None",
                "region": region_col or "None",
                "qty": quantity_col or "None",
                "price": unit_price_col or "None",
                "sales": sales_amount_col or "None",
                "rep": sales_rep_col or "None",
            }

        with st.sidebar:
            st.header("⚙️ Column Mapping")
            st.caption("Auto-detected where possible. Adjust if needed.")
            all_cols = ["None"] + list(df.columns)

            st.session_state.cols["date"] = st.selectbox("Date column", all_cols, index=all_cols.index(st.session_state.cols["date"]) if st.session_state.cols["date"] in all_cols else 0)
            st.session_state.cols["product"] = st.selectbox("Product column", all_cols, index=all_cols.index(st.session_state.cols["product"]) if st.session_state.cols["product"] in all_cols else 0)
            st.session_state.cols["category"] = st.selectbox("Category column", all_cols, index=all_cols.index(st.session_state.cols["category"]) if st.session_state.cols["category"] in all_cols else 0)
            st.session_state.cols["region"] = st.selectbox("Region column", all_cols, index=all_cols.index(st.session_state.cols["region"]) if st.session_state.cols["region"] in all_cols else 0)
            st.session_state.cols["qty"] = st.selectbox("Quantity column", all_cols, index=all_cols.index(st.session_state.cols["qty"]) if st.session_state.cols["qty"] in all_cols else 0)
            st.session_state.cols["price"] = st.selectbox("Unit price column", all_cols, index=all_cols.index(st.session_state.cols["price"]) if st.session_state.cols["price"] in all_cols else 0)
            st.session_state.cols["sales"] = st.selectbox("Sales amount column", all_cols, index=all_cols.index(st.session_state.cols["sales"]) if st.session_state.cols["sales"] in all_cols else 0)
            st.session_state.cols["rep"] = st.selectbox("Sales rep column", all_cols, index=all_cols.index(st.session_state.cols["rep"]) if st.session_state.cols["rep"] in all_cols else 0)

        # Shorthand vars
        date_col = st.session_state.cols["date"]
        prod_col = st.session_state.cols["product"]
        cat_col = st.session_state.cols["category"]
        reg_col = st.session_state.cols["region"]
        qty_col = st.session_state.cols["qty"]
        price_col = st.session_state.cols["price"]
        sales_col = st.session_state.cols["sales"]
        rep_col = st.session_state.cols["rep"]

        # ---------- Parse date & numerics ----------
        if date_col != "None":
            # try robust parse (dayfirst often used in India)
            df[date_col] = pd.to_datetime(df[date_col], errors="coerce", dayfirst=True, infer_datetime_format=True)

        for col_ in [qty_col, price_col, sales_col]:
            if col_ != "None":
                df[col_] = pd.to_numeric(df[col_], errors="coerce")

        # ---------- Filters ----------
        with st.sidebar:
            st.header("🔎 Filters")
            chosen_categories = st.multiselect("Category", sorted(df[cat_col].dropna().unique())) if cat_col != "None" else []
            chosen_regions = st.multiselect("Region", sorted(df[reg_col].dropna().unique())) if reg_col != "None" else []
            chosen_reps = st.multiselect("Sales Rep", sorted(df[rep_col].dropna().unique())) if rep_col != "None" else []
            show_preview = st.checkbox("Show full preview table", value=False)

        # Apply filters
        df_filtered = df.copy()
        if cat_col != "None" and chosen_categories:
            df_filtered = df_filtered[df_filtered[cat_col].isin(chosen_categories)]
        if reg_col != "None" and chosen_regions:
            df_filtered = df_filtered[df_filtered[reg_col].isin(chosen_regions)]
        if rep_col != "None" and chosen_reps:
            df_filtered = df_filtered[df_filtered[rep_col].isin(chosen_reps)]

        # ---------- Revenue column ----------
        revenue_col = None
        if sales_col != "None":
            df_filtered[sales_col] = pd.to_numeric(df_filtered[sales_col], errors="coerce").fillna(0)
            revenue_col = sales_col
        elif qty_col != "None" and price_col != "None":
            df_filtered[qty_col] = pd.to_numeric(df_filtered[qty_col], errors="coerce").fillna(0)
            df_filtered[price_col] = pd.to_numeric(df_filtered[price_col], errors="coerce").fillna(0)
            df_filtered["__Revenue__"] = (df_filtered[qty_col] * df_filtered[price_col]).fillna(0)
            revenue_col = "__Revenue__"

        # ---------- KPI calculations ----------
        num_orders = len(df_filtered)
        total_revenue = float(df_filtered[revenue_col].sum()) if revenue_col else 0.0
        total_units = float(df_filtered[qty_col].sum()) if qty_col != "None" else 0.0
        avg_order_value = (total_revenue / num_orders) if num_orders > 0 else 0.0

        # Helpers for safe groupby
        def safe_group_idxmax(frame, by_col, val_col):
            if by_col == "None" or val_col is None or by_col not in frame.columns or val_col not in frame.columns:
                return "—"
            s = frame.groupby(by_col, dropna=True)[val_col].sum()
            return s.idxmax() if not s.empty else "—"

        top_product = safe_group_idxmax(df_filtered, prod_col, revenue_col)
        top_region = safe_group_idxmax(df_filtered, reg_col, revenue_col)
        best_sales_rep = safe_group_idxmax(df_filtered, rep_col, revenue_col)

        # ---------- KPI display ----------
        k1, k2, k3, k4, k5 = st.columns(5)
        with k1:
            st.markdown(f"<div class='card'><div class='kpi-value'>₹{total_revenue:,.0f}</div><div class='kpi-label'>Total Revenue</div></div>", unsafe_allow_html=True)
        with k2:
            st.markdown(f"<div class='card'><div class='kpi-value'>{int(total_units):,}</div><div class='kpi-label'>Units Sold</div></div>", unsafe_allow_html=True)
        with k3:
            st.markdown(f"<div class='card'><div class='kpi-value'>₹{avg_order_value:,.2f}</div><div class='kpi-label'>Avg Order Value</div></div>", unsafe_allow_html=True)
        with k4:
            st.markdown(f"<div class='card'><div class='kpi-value'>{top_product}</div><div class='kpi-label'>Top Product</div></div>", unsafe_allow_html=True)
        with k5:
            st.markdown(f"<div class='card'><div class='kpi-value'>{top_region}</div><div class='kpi-label'>Top Region</div></div>", unsafe_allow_html=True)
        
        # ---------- Data Preview ----------
        st.subheader("📋 Data Preview")
        if show_preview:
            st.dataframe(df_filtered, use_container_width=True, height=400)
        else:
            st.dataframe(df_filtered.head(10), use_container_width=True, height=250)

        # ---------- Charts ----------
        st.subheader("📈 Sales Trend")
        if revenue_col and date_col != "None":
            monthly_rev = df_filtered.set_index(date_col).resample("M")[revenue_col].sum().reset_index()
            chart = alt.Chart(monthly_rev).mark_line(point=True).encode(
                x=alt.X(date_col, title="Month"),
                y=alt.Y(revenue_col, title="Revenue"),
                tooltip=[date_col, revenue_col]
            ).properties(width="container")
            st.altair_chart(chart, use_container_width=True)
        else:
            st.info("Sales trend requires a date column and revenue.")

        st.subheader("🏆 Top Products")
        if prod_col != "None" and revenue_col:
            top5 = df_filtered.groupby(prod_col)[revenue_col].sum().sort_values(ascending=False).head(5).reset_index()
            prod_chart = alt.Chart(top5).mark_bar().encode(
                x=alt.X(prod_col, sort='-y'),
                y=alt.Y(revenue_col),
                tooltip=[prod_col, revenue_col]
            ).properties(width="container")
            st.altair_chart(prod_chart, use_container_width=True)

        st.subheader("🌍 Revenue by Region")
        if reg_col != "None" and revenue_col:
            reg_rev = df_filtered.groupby(reg_col)[revenue_col].sum().sort_values(ascending=False).reset_index()
            reg_chart = alt.Chart(reg_rev).mark_bar().encode(
                x=alt.X(reg_col, sort='-y'),
                y=alt.Y(revenue_col),
                tooltip=[reg_col, revenue_col]
            ).properties(width="container")
            st.altair_chart(reg_chart, use_container_width=True)

        # ---------- Insights ----------
        st.subheader("💡 Quick Insights")
        insights = []

        # Seasonal best month
        if date_col != "None" and revenue_col:
            month_rev = df_filtered.groupby(df_filtered[date_col].dt.month)[revenue_col].sum()
            if not month_rev.empty:
                best_month = month_rev.idxmax()
                insights.append(f"Best month for sales: **{datetime.date(1900, int(best_month), 1).strftime('%B')}**.")

        # Weekday pattern
            weekday_rev = df_filtered.groupby(df_filtered[date_col].dt.day_name())[revenue_col].sum()
            if not weekday_rev.empty:
                best_day = weekday_rev.idxmax()
                insights.append(f"Highest sales day: **{best_day}**.")

        # Low performing product
        if prod_col != "None" and revenue_col:
            prod_rev = df_filtered.groupby(prod_col)[revenue_col].sum()
            if len(prod_rev) > 1:
                low_product = prod_rev.idxmin()
                insights.append(f"Lowest performing product: **{low_product}**.")

        # Best sales rep
        if rep_col != "None" and revenue_col:
            if best_sales_rep != "—":
                insights.append(f"Best sales rep: **{best_sales_rep}**.")

        # Display insights
        for s in insights:
            st.markdown(f"- {s}")

# ---------- FOOTER SECTION (Always shown) ----------
st.markdown("---")
st.markdown("<div class='footer'>", unsafe_allow_html=True)

if uploaded_file is not None and 'df_filtered' in locals():
    # If data is loaded, show export options
    st.subheader("📥 Export Options")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # ---------- CSV Export ----------
        csv_data = df_filtered.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️ Download Filtered Data (CSV)",
            data=csv_data,
            file_name="filtered_sales.csv",
            mime="text/csv"
        )
    
    with col2:
        # ---------- PDF Export ----------
        def export_pdf():
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            styles = getSampleStyleSheet()
            elements = []

            # Logo placeholder
            elements.append(Paragraph("SmartDash Report", styles['Title']))
            elements.append(Spacer(1, 12))

            # Section: KPIs
            elements.append(Paragraph("Key Metrics", styles['Heading2']))
            kpi_table = [
                ["Total Revenue", f"₹{total_revenue:,.0f}"],
                ["Units Sold", f"{int(total_units):,}"],
                ["Avg Order Value", f"₹{avg_order_value:,.2f}"],
                ["Top Product", top_product],
                ["Top Region", top_region]
            ]
            t = Table(kpi_table)
            t.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,0), colors.lightblue),
                                   ("GRID", (0,0), (-1,-1), 0.5, colors.grey)]))
            elements.append(t)
            elements.append(Spacer(1, 12))

            # Section: Insights
            elements.append(Paragraph("Insights", styles['Heading2']))
            for s in insights:
                elements.append(Paragraph(f"- {s}", styles['Normal']))

            # Mention charts
            elements.append(Spacer(1, 12))
            elements.append(Paragraph("Charts included in dashboard:", styles['Heading3']))
            elements.append(Paragraph("• Sales Trend", styles['Normal']))
            elements.append(Paragraph("• Top Products", styles['Normal']))
            elements.append(Paragraph("• Revenue by Region", styles['Normal']))

            doc.build(elements)
            buffer.seek(0)
            return buffer

        pdf_buffer = export_pdf()
        st.download_button(
            label="📄 Download PDF Report",
            data=pdf_buffer,
            file_name="SmartDash_Report.pdf",
            mime="application/pdf"
        )
else:
    # If no data is loaded, show info about the app
    st.subheader("ℹ️ About SmartDash")
    st.write("SmartDash — An AI-powered, interactive sales analytics dashboard for small businesses.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Features:**")
        st.write("• Auto-detects sales columns for quick setup.")
        st.write("• Real-time filters & KPI cards for instant insights.")
        st.write("• Clear, interactive charts for trends & performance.")
        st.write("• Export results as CSV or styled PDF report.")
    
    with col2:
        st.write("**Created by:**")
        st.write("👨‍💻 Akash Gupta")
        st.write("📧 akashguptard8083@gmail.com")
        st.write("🌐 [Portfolio](https://your-portfolio-link.com)")
        st.write("🔗 [LinkedIn](https://linkedin.com/in/itsaakash-gupta )")

st.markdown("</div>", unsafe_allow_html=True)
st.markdown("---")
st.markdown("<center>© 2025 SmartDash. Made with ❤️ for small businesses.</center>", unsafe_allow_html=True)
