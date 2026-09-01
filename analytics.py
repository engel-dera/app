"""RiskWatch — Analytics Dashboard page.
Rule performance, precision proxy (vs synthetic ground truth), risk distribution, time-to-decision.
For Manager/PM. Precision proxy uses is_synthetic_suspicious in aggregate only — never shown per-row.
"""
import os
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text
from datetime import date, timedelta

st.set_page_config(page_title="Analytics Dashboard", layout="wide")
DB_URL = os.environ.get("RISKWATCH_DB_URL")

if not DB_URL:
    raise RuntimeError("RISKWATCH_DB_URL is not configured.")
engine = create_engine(DB_URL)


def q(sql, params=None):
    with engine.connect() as conn:
        return pd.read_sql(text(sql), conn, params=params or {})


st.title("Analytics Dashboard")
st.caption("Rule performance, precision proxy vs. synthetic ground truth, and analyst decision speed.")

# --- Filters ---
rules_df = q("SELECT rule_id, rule_name FROM detection_rules ORDER BY rule_name")
fc1, fc2 = st.columns([2, 3])
with fc1:
    default_start = date.today() - timedelta(days=90)
    date_range = st.date_input("Date range (alert created)", value=(default_start, date.today()))
with fc2:
    selected_rules = st.multiselect(
        "Filter by rule (optional)", rules_df["rule_id"],
        format_func=lambda rid: rules_df.loc[rules_df.rule_id == rid, "rule_name"].iloc[0],
    )

start_date, end_date = (date_range if isinstance(date_range, tuple) and len(date_range) == 2
                         else (default_start, date.today()))
rule_filter_clause = "AND dr.rule_id = ANY(:rule_ids)" if selected_rules else ""
params = {"start": start_date, "end": end_date}
if selected_rules:
    params["rule_ids"] = list(map(int, selected_rules))

# --- Rule performance + precision proxy ---
st.subheader("Rule performance")
rule_perf = q(f"""
    SELECT dr.rule_name,
           dr.threshold_value,
           dr.threshold_unit,
           COUNT(ta.alert_id) AS total_alerts,
           COUNT(*) FILTER (WHERE ta.alert_status = 'escalated') AS escalated,
           COUNT(*) FILTER (WHERE ta.alert_status = 'cleared') AS cleared,
           COUNT(*) FILTER (WHERE ta.alert_status = 'restricted') AS restricted,
           ROUND(100.0 * COUNT(*) FILTER (WHERE t.is_synthetic_suspicious)
                 / NULLIF(COUNT(ta.alert_id), 0), 1) AS precision_proxy_pct
    FROM detection_rules dr
    LEFT JOIN transaction_alerts ta
           ON ta.rule_id = dr.rule_id
          AND ta.alert_created_at BETWEEN :start AND :end
          {rule_filter_clause}
    LEFT JOIN transactions t ON t.transaction_id = ta.transaction_id
    GROUP BY dr.rule_id, dr.rule_name, dr.threshold_value, dr.threshold_unit
    ORDER BY total_alerts DESC
""", params)
st.dataframe(rule_perf, use_container_width=True, hide_index=True)

if not rule_perf.empty:
    ch1, ch2 = st.columns(2)
    with ch1:
        st.caption("Alert volume by rule")
        st.bar_chart(rule_perf.set_index("rule_name")["total_alerts"])
    with ch2:
        st.caption("Precision proxy by rule (% hitting known-suspicious ground truth)")
        st.bar_chart(rule_perf.set_index("rule_name")["precision_proxy_pct"])

st.divider()

# --- Risk band distribution ---
st.subheader("Risk score distribution")
band_dist = q("""
    SELECT rs.risk_band, COUNT(*) AS alerts
    FROM risk_scores rs
    JOIN transaction_alerts ta ON ta.alert_id = rs.alert_id
    WHERE ta.alert_created_at BETWEEN :start AND :end
    GROUP BY rs.risk_band
""", params)
if band_dist.empty:
    st.caption("No scored alerts in this date range.")
else:
    band_order = ["low", "medium", "high", "critical"]
    band_dist["risk_band"] = pd.Categorical(band_dist["risk_band"], categories=band_order, ordered=True)
    band_dist = band_dist.sort_values("risk_band")
    st.bar_chart(band_dist.set_index("risk_band"))

st.divider()

# --- Time-to-decision by risk band (guardrail-relevant, see Phase 12 experiment) ---
st.subheader("Time-to-decision by risk band")
ttd = q("""
    SELECT rs.risk_band,
           COUNT(*) AS decisions,
           ROUND(AVG(EXTRACT(EPOCH FROM (aa.decided_at - ta.alert_created_at))) / 60.0, 1) AS avg_minutes_to_decision
    FROM alert_actions aa
    JOIN transaction_alerts ta ON ta.alert_id = aa.alert_id
    LEFT JOIN risk_scores rs ON rs.alert_id = ta.alert_id
    WHERE aa.decided_at BETWEEN :start AND :end
    GROUP BY rs.risk_band
    ORDER BY rs.risk_band
""", params)
if ttd.empty:
    st.caption("No decisions recorded in this date range yet.")
else:
    tc1, tc2 = st.columns([2, 3])
    tc1.dataframe(ttd, use_container_width=True, hide_index=True)
    tc2.bar_chart(ttd.set_index("risk_band")["avg_minutes_to_decision"])

st.divider()

# --- Decision type trend ---
st.subheader("Decisions over time")
trend = q("""
    SELECT date_trunc('day', aa.decided_at)::date AS day, aa.decision, COUNT(*) AS n
    FROM alert_actions aa
    WHERE aa.decided_at BETWEEN :start AND :end
    GROUP BY 1, 2
    ORDER BY 1
""", params)
if trend.empty:
    st.caption("No decisions recorded in this date range yet.")
else:
    pivot = trend.pivot(index="day", columns="decision", values="n").fillna(0)
    st.line_chart(pivot)