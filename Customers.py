"""RiskWatch — Customer Risk Profile page.
KYC fields, expected-vs-actual behaviour (the core differentiator), PEP/sanctions status, past alerts.
"""
import os
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text

try:
    from mixpanel import Mixpanel
    MP_TOKEN = os.environ.get("MIXPANEL_TOKEN")
    mp = Mixpanel(MP_TOKEN) if MP_TOKEN else None
except ImportError:
    mp = None

ANALYST_ID = "analyst_demo"

st.set_page_config(page_title="Customer Risk Profile", layout="wide")
DB_URL = os.environ.get("RISKWATCH_DB_URL")

if not DB_URL:
    raise RuntimeError("RISKWATCH_DB_URL is not configured.")

engine = create_engine(DB_URL)


def q(sql, params=None):
    with engine.connect() as conn:
        return pd.read_sql(text(sql), conn, params=params or {})


def track(event, props=None):
    if mp:
        mp.track(ANALYST_ID, event, props or {})


st.title("Customer Risk Profile")

# --- Customer selection (supports deep-link from Alert Details via ?customer_id=&from_alert_id=) ---
customers = q("SELECT customer_id, full_name, customer_type FROM customers ORDER BY full_name")
if customers.empty:
    st.warning("No customers found. Run the synthetic data generator first.")
    st.stop()

qp = st.query_params
default_cid = qp.get("customer_id")
from_alert_id = qp.get("from_alert_id")

options = customers["customer_id"].tolist()
labels = {row.customer_id: f"{row.full_name} (#{row.customer_id}, {row.customer_type})" for row in customers.itertuples()}
default_index = options.index(int(default_cid)) if default_cid and int(default_cid) in options else 0

customer_id = st.selectbox(
    "Customer", options, index=default_index, format_func=lambda cid: labels[cid]
)

track("customer_profile_viewed", {
    "customer_id": int(customer_id),
    "from_alert_id": int(from_alert_id) if from_alert_id else None,
})

cust = q("""
    SELECT customer_id, customer_type, full_name, country_of_residence, occupation_or_industry,
           account_opening_date, kyc_status, customer_risk_rating, pep_status,
           sanctions_screening_status, adverse_media_flag, high_risk_country_link, created_at
    FROM customers WHERE customer_id = :cid
""", {"cid": int(customer_id)}).iloc[0]

kyc = q("""
    SELECT purpose_of_account, source_of_funds, source_of_wealth,
           expected_monthly_txn_count, expected_monthly_txn_value, expected_txn_countries,
           kyc_last_reviewed_date
    FROM kyc_profiles WHERE customer_id = :cid
""", {"cid": int(customer_id)})

# --- Core identity + risk flags ---
c1, c2, c3 = st.columns(3)
with c1:
    st.write(f"**Name:** {cust['full_name']}")
    st.write(f"**Type:** {cust['customer_type']}")
    st.write(f"**Country of residence:** {cust['country_of_residence']}")
    st.write(f"**Occupation/Industry:** {cust['occupation_or_industry'] or 'n/a'}")
with c2:
    st.write(f"**Account opened:** {cust['account_opening_date']}")
    st.write(f"**KYC status:** {cust['kyc_status']}")
    band_color = {"low": "🟢", "medium": "🟡", "high": "🔴"}.get(cust["customer_risk_rating"], "")
    st.write(f"**Risk rating:** {band_color} {cust['customer_risk_rating']}")
with c3:
    st.write(f"**PEP:** {'⚠️ Yes' if cust['pep_status'] else 'No'}")
    sanctions = cust["sanctions_screening_status"]
    st.write(f"**Sanctions screening:** {'🚨 ' + sanctions if sanctions != 'clear' else sanctions}")
    st.write(f"**Adverse media:** {'⚠️ Yes' if cust['adverse_media_flag'] else 'No'}")
    st.write(f"**High-risk country link:** {'⚠️ Yes' if cust['high_risk_country_link'] else 'No'}")

st.divider()

# --- Business / KYB details, only if applicable ---
if cust["customer_type"] == "business":
    biz = q("""
        SELECT industry_code, incorporation_country, incorporation_date,
               registration_number_synthetic, annual_turnover_expected,
               number_of_employees, cash_intensive_business
        FROM business_profiles WHERE customer_id = :cid
    """, {"cid": int(customer_id)})
    if not biz.empty:
        b = biz.iloc[0]
        st.subheader("Business profile (KYB)")
        bc1, bc2, bc3 = st.columns(3)
        bc1.write(f"**Industry:** {b['industry_code'] or 'n/a'}")
        bc1.write(f"**Incorporation country:** {b['incorporation_country'] or 'n/a'}")
        bc2.write(f"**Incorporation date:** {b['incorporation_date'] or 'n/a'}")
        bc2.write(f"**Registration #:** {b['registration_number_synthetic'] or 'n/a'}")
        bc3.write(f"**Expected annual turnover:** ${b['annual_turnover_expected']:,.2f}" if pd.notna(b['annual_turnover_expected']) else "**Expected annual turnover:** n/a")
        bc3.write(f"**Employees:** {b['number_of_employees'] or 'n/a'}")
        if b["cash_intensive_business"]:
            st.warning("Flagged as a cash-intensive business.")

        owners = q("""
            SELECT owner_name, ownership_percentage, nationality, pep_status
            FROM beneficial_owners WHERE business_customer_id = :cid
            ORDER BY ownership_percentage DESC
        """, {"cid": int(customer_id)})
        if not owners.empty:
            st.caption("Beneficial owners (>25% ownership convention)")
            st.dataframe(owners, use_container_width=True, hide_index=True)
    st.divider()

# --- Expected vs Actual behaviour — the core product differentiator ---
st.subheader("Expected vs. actual behaviour (last 30 days)")

actual = q("""
    SELECT COUNT(*) AS actual_txn_count,
           COALESCE(SUM(t.amount), 0) AS actual_txn_value,
           ARRAY_AGG(DISTINCT t.counterparty_country) FILTER (WHERE t.counterparty_country IS NOT NULL) AS actual_countries
    FROM transactions t
    JOIN accounts a ON a.account_id = t.account_id
    WHERE a.customer_id = :cid
      AND t.transaction_timestamp >= now() - interval '30 days'
""", {"cid": int(customer_id)}).iloc[0]

if not kyc.empty:
    k = kyc.iloc[0]
    ec1, ec2, ec3 = st.columns(3)
    ec1.metric(
        "Monthly txn count",
        int(actual["actual_txn_count"]),
        delta=int(actual["actual_txn_count"]) - int(k["expected_monthly_txn_count"]),
        help=f"Expected: {k['expected_monthly_txn_count']}",
    )
    ec2.metric(
        "Monthly txn value",
        f"${actual['actual_txn_value']:,.0f}",
        delta=f"${float(actual['actual_txn_value']) - float(k['expected_monthly_txn_value']):,.0f}",
        help=f"Expected: ${k['expected_monthly_txn_value']:,.2f}",
    )
    expected_countries = set(k["expected_txn_countries"] or [])
    actual_countries = set(actual["actual_countries"] or [])
    unexpected = actual_countries - expected_countries
    ec3.metric("Unexpected countries (30d)", len(unexpected))
    if unexpected:
        st.warning(f"Transactions seen with countries outside the expected list: {', '.join(sorted(unexpected))}")

    with st.expander("KYC baseline detail"):
        st.write(f"**Purpose of account:** {k['purpose_of_account'] or 'n/a'}")
        st.write(f"**Source of funds:** {k['source_of_funds'] or 'n/a'}")
        st.write(f"**Source of wealth:** {k['source_of_wealth'] or 'n/a'}")
        st.write(f"**Expected countries:** {', '.join(k['expected_txn_countries']) if k['expected_txn_countries'] else 'n/a'}")
        st.write(f"**KYC last reviewed:** {k['kyc_last_reviewed_date'] or 'n/a'}")
else:
    st.info("No KYC profile on file for this customer.")

st.divider()

# --- Past alerts ---
st.subheader("Past alerts")
alerts = q("""
    SELECT ta.alert_id, dr.rule_name, rs.total_score, rs.risk_band, ta.alert_status, ta.alert_created_at
    FROM transaction_alerts ta
    JOIN detection_rules dr ON dr.rule_id = ta.rule_id
    LEFT JOIN risk_scores rs ON rs.alert_id = ta.alert_id
    WHERE ta.customer_id = :cid
    ORDER BY ta.alert_created_at DESC
""", {"cid": int(customer_id)})
if alerts.empty:
    st.caption("No alerts on record for this customer.")
else:
    st.dataframe(alerts, use_container_width=True, hide_index=True)

st.divider()

# --- Transaction history (never expose is_synthetic_suspicious — hidden ground truth) ---
with st.expander("Open transaction history"):
    history = q("""
        SELECT t.transaction_id, t.transaction_type, t.amount, t.currency,
               t.counterparty_country, t.transaction_timestamp
        FROM transactions t
        JOIN accounts a ON a.account_id = t.account_id
        WHERE a.customer_id = :cid
        ORDER BY t.transaction_timestamp DESC
        LIMIT 200
    """, {"cid": int(customer_id)})
    track("transaction_history_viewed", {"customer_id": int(customer_id), "txn_count_shown": len(history)})
    if history.empty:
        st.caption("No transactions on record.")
    else:
        st.dataframe(history, use_container_width=True, hide_index=True)
        st.line_chart(history.set_index("transaction_timestamp")["amount"])