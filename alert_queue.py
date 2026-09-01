"""RiskWatch — Alert Queue page. Sort by risk score, open an alert, record a decision."""

import os
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text
from tracking import track_event


ANALYST_ID = "analyst_demo"  # single-analyst prototype


st.set_page_config(page_title="Alert Queue", layout="wide")


# Database connection
DB_URL = os.environ.get("RISKWATCH_DB_URL")

if not DB_URL:
    st.error("Set the RISKWATCH_DB_URL environment variable before running.")
    st.stop()

engine = create_engine(DB_URL)


def q(sql, params=None):
    with engine.connect() as conn:
        return pd.read_sql(text(sql), conn, params=params or {})


st.title("Alert Queue")


# Sort options
sort_choice = st.radio(
    "Sort by",
    ["Risk score (high to low)", "Created (newest first)"],
    horizontal=True
)

order_clause = (
    "rs.total_score DESC"
    if sort_choice.startswith("Risk")
    else "ta.alert_created_at DESC"
)


# Load alert queue
queue = q(f"""
    SELECT
        ta.alert_id,
        c.full_name,
        c.customer_id,
        dr.rule_name,
        rs.total_score,
        rs.risk_band,
        ta.alert_status,
        ta.alert_created_at
    FROM transaction_alerts ta
    JOIN customers c
        ON c.customer_id = ta.customer_id
    JOIN detection_rules dr
        ON dr.rule_id = ta.rule_id
    LEFT JOIN risk_scores rs
        ON rs.alert_id = ta.alert_id
        AND rs.model_version = 'model3'
    WHERE ta.alert_status IN ('open', 'in_review')
    ORDER BY {order_clause}
    LIMIT 100
""")


st.dataframe(
    queue,
    use_container_width=True,
    hide_index=True
)


st.divider()
st.subheader("Open an alert")


# Alert selector
alert_id = st.selectbox(
    "Alert ID",
    queue["alert_id"] if not queue.empty else []
)


if alert_id:

    # Track alert view only once per selected alert
    if st.session_state.get("last_viewed_alert") != alert_id:

        track_event(
            ANALYST_ID,
            "alert_viewed",
            {
                "alert_id": int(alert_id)
            }
        )

        st.session_state["last_viewed_alert"] = alert_id


    # Load alert details
    detail = q(
        """
        SELECT
            ta.*,
            c.full_name,
            c.customer_risk_rating,
            c.pep_status,
            c.sanctions_screening_status,
            dr.rule_name,
            dr.rule_description,
            rs.total_score,
            rs.risk_band,
            t.amount,
            t.transaction_timestamp,
            t.counterparty_country
        FROM transaction_alerts ta
        JOIN customers c
            ON c.customer_id = ta.customer_id
        JOIN detection_rules dr
            ON dr.rule_id = ta.rule_id
        LEFT JOIN risk_scores rs
            ON rs.alert_id = ta.alert_id
            AND rs.model_version = 'model3'
        JOIN transactions t
            ON t.transaction_id = ta.transaction_id
        WHERE ta.alert_id = :aid
        """,
        {"aid": int(alert_id)}
    ).iloc[0]


    # Open alert details
    if st.button("Open alert details"):

        track_event(
            ANALYST_ID,
            "alert_opened",
            {
                "alert_id": int(alert_id),
                "risk_band": detail["risk_band"]
            }
        )


    # Alert information
    c1, c2 = st.columns(2)


    with c1:

        st.metric(
            "Risk Score",
            (
                f"{detail['total_score']} ({detail['risk_band']})"
                if pd.notna(detail["total_score"])
                else "n/a"
            )
        )

        st.write(
            f"**Rule triggered:** {detail['rule_name']}"
        )

        st.write(
            detail["rule_description"]
        )


    with c2:

        st.write(
            f"**Customer:** {detail['full_name']} "
            f"(risk rating: {detail['customer_risk_rating']})"
        )

        st.write(
            f"**PEP:** {detail['pep_status']} | "
            f"**Sanctions:** {detail['sanctions_screening_status']}"
        )

        st.write(
            f"**Transaction:** ${detail['amount']:,.2f} "
            f"to {detail['counterparty_country']} "
            f"on {detail['transaction_timestamp']}"
        )


    st.divider()
    st.subheader("Record decision")


    # Decision form
    with st.form("decision_form"):

        decision = st.radio(
            "Decision",
            ["escalate", "clear", "restrict"]
        )

        notes = st.text_area("Notes")

        submitted = st.form_submit_button(
            "Submit decision"
        )


        if submitted:

            # Save decision to database
            with engine.begin() as conn:

                conn.execute(
                    text(
                        """
                        INSERT INTO alert_actions
                            (alert_id, analyst_id, decision, notes)
                        VALUES
                            (:aid, :analyst, :decision, :notes)
                        """
                    ),
                    {
                        "aid": int(alert_id),
                        "analyst": ANALYST_ID,
                        "decision": decision,
                        "notes": notes
                    }
                )


                # Update alert status
                new_status = {
                    "escalate": "escalated",
                    "clear": "cleared",
                    "restrict": "restricted"
                }[decision]


                conn.execute(
                    text(
                        """
                        UPDATE transaction_alerts
                        SET alert_status = :s
                        WHERE alert_id = :aid
                        """
                    ),
                    {
                        "s": new_status,
                        "aid": int(alert_id)
                    }
                )


            # Track completed decision in Mixpanel
            track_event(
                ANALYST_ID,
                "decision_completed",
                {
                    "alert_id": int(alert_id),
                    "decision_type": decision,
                    "risk_band": detail["risk_band"],
                }
            )


            st.success(
                f"Decision recorded: {decision}"
            )