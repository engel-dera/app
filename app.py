import os 
import pandas as pd 
import streamlit as st 
from sqlalchemy import create_engine, text 
 
st.set_page_config( 
    page_title="RiskWatch", 
    layout="wide", 
    page_icon="🛡️" 
) 
 

DB_URL = os.environ.get("RISKWATCH_DB_URL")

if not DB_URL:
    raise RuntimeError("RISKWATCH_DB_URL is not configured.")
 
 
@st.cache_resource 
def get_engine(): 
    return create_engine(DB_URL) 
 
 
def run_query(sql, params=None): 
    with get_engine().connect() as conn: 
        return pd.read_sql(text(sql), conn, params=params or {}) 
 
 
def dashboard(): 
    st.title("🛡️ RiskWatch") 
    st.caption( 
        "Portfolio prototype — 100% synthetic data. " 
        "Not a production AML/compliance system." 
    ) 
 
    col1, col2, col3, col4 = st.columns(4) 
 
    open_alerts = run_query( 
        "SELECT COUNT(*) AS n FROM transaction_alerts " 
        "WHERE alert_status='open'" 
    ).iloc[0]["n"] 
 
    critical = run_query( 
        "SELECT COUNT(*) AS n FROM risk_scores " 
        "WHERE risk_band='critical'" 
    ).iloc[0]["n"] 
 
    customers = run_query( 
        "SELECT COUNT(*) AS n FROM customers" 
    ).iloc[0]["n"] 
 
    txns = run_query( 
        "SELECT COUNT(*) AS n FROM transactions" 
    ).iloc[0]["n"] 
 
    col1.metric("Open Alerts", int(open_alerts)) 
    col2.metric("Critical Alerts", int(critical)) 
    col3.metric("Customers", int(customers)) 
    col4.metric("Transactions", int(txns)) 
 
    st.divider() 
 
    st.subheader("Alert volume by risk band") 
 
    band_df = run_query( 
        "SELECT risk_band, COUNT(*) AS alerts " 
        "FROM risk_scores GROUP BY risk_band" 
    ) 
 
    st.bar_chart(band_df.set_index("risk_band")) 
 
 
# ----------------------------- 
# Streamlit navigation 
# ----------------------------- 
 
dashboard_page = st.Page( 
    dashboard, 
    title="Dashboard", 
    icon="🏠" 
) 
 
alert_queue_page = st.Page( 
    "alert_queue.py", 
    title="Alert Queue", 
    icon="🚨" 
) 
 
customers_page = st.Page( 
    "customers.py", 
    title="Customers", 
    icon="👥" 
) 
 
analytics_page = st.Page( 
    "analytics.py", 
    title="Analytics", 
    icon="📊" 
) 
 
pg = st.navigation( 
    { 
        "RiskWatch": [ 
            dashboard_page, 
            alert_queue_page, 
            customers_page, 
            analytics_page, 
        ] 
    } 
) 
 
pg.run()