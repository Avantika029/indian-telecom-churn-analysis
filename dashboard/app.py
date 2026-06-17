import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import joblib

st.set_page_config(page_title="Indian Telecom Churn & Retention Dashboard", layout="wide")

# ---- Load data ----
@st.cache_data
def load_data():
    df = pd.read_csv("../data/raw/indian_telecom_churn.csv")
    ab = pd.read_csv("../data/raw/retention_ab_test.csv")
    preds = pd.read_csv("../data/processed/test_predictions.csv")
    return df, ab, preds

df, ab, preds = load_data()

st.title("📊 Indian Telecom Customer Churn & Retention Analysis")
st.markdown("**Data grounded in TRAI Dec-2025 statistics** | Synthetic dataset calibrated to real market share and active-subscriber patterns")

# ---- Tabs ----
tab1, tab2, tab3 = st.tabs(["Overview & EDA", "Churn Model", "A/B Test Results"])

# ============ TAB 1: EDA ============
with tab1:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Customers", f"{len(df):,}")
    col2.metric("Overall Churn Rate", f"{df['churn'].mean():.1%}")
    col3.metric("Avg Plan Amount", f"₹{df['plan_amount_inr'].mean():.0f}")
    col4.metric("Active (VLR) %", f"{df['is_active_vlr'].mean():.1%}")

    st.subheader("Churn Rate by Operator")
    churn_op = df.groupby("operator")["churn"].mean().sort_values(ascending=False).reset_index()
    fig = px.bar(churn_op, x="operator", y="churn", color="operator",
                  labels={"churn": "Churn Rate"}, title="")
    fig.update_layout(yaxis_tickformat=".0%")
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Churn Rate by VLR (Active Subscriber) Status")
        churn_vlr = df.groupby("is_active_vlr")["churn"].mean().reset_index()
        churn_vlr["is_active_vlr"] = churn_vlr["is_active_vlr"].map({0: "Inactive", 1: "Active"})
        fig = px.bar(churn_vlr, x="is_active_vlr", y="churn", color="is_active_vlr",
                      labels={"churn": "Churn Rate", "is_active_vlr": "Status"})
        fig.update_layout(yaxis_tickformat=".0%")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Churn Rate by Days Since Last Recharge")
        df["recharge_bucket"] = pd.cut(df["days_since_last_recharge"],
            bins=[-1,7,15,30,45,200], labels=["0-7","8-15","16-30","31-45","45+"])
        churn_recency = df.groupby("recharge_bucket")["churn"].mean().reset_index()
        fig = px.bar(churn_recency, x="recharge_bucket", y="churn",
                      labels={"churn": "Churn Rate", "recharge_bucket": "Days Since Recharge"})
        fig.update_layout(yaxis_tickformat=".0%")
        st.plotly_chart(fig, use_container_width=True)

# ============ TAB 2: CHURN MODEL ============
with tab2:
    st.subheader("Model Performance Comparison")
    model_comparison = pd.DataFrame({
        "Model": ["Logistic Regression", "Random Forest", "XGBoost (default)", "XGBoost (tuned)"],
        "Accuracy": [0.712, 0.883, 0.770, 0.712],
        "Precision": [0.204, 0.297, 0.213, 0.203],
        "Recall": [0.627, 0.108, 0.466, 0.623],
        "F1": [0.308, 0.158, 0.292, 0.306],
        "ROC-AUC": [0.757, 0.731, 0.728, 0.748]
    })
    st.dataframe(model_comparison, use_container_width=True, hide_index=True)
    st.caption("Logistic Regression selected as primary model - best ROC-AUC and tied-best F1 despite simplicity.")

    st.subheader("Top Churn Drivers (Logistic Regression Coefficients)")
    coef_data = pd.DataFrame({
        "feature": ["operator_Vi", "has_bundle", "tenure_growing_4_12m", "tenure_loyal_36m_plus",
                     "dormant_45d_flag", "high_complaints_flag", "network_rating",
                     "is_active_vlr", "operator_BSNL"],
        "coefficient": [0.487, -0.353, -0.325, -0.319, 0.311, 0.308, -0.292, -0.271, 0.266]
    }).sort_values("coefficient")
    fig = px.bar(coef_data, x="coefficient", y="feature", orientation="h",
                  color="coefficient", color_continuous_scale="RdBu_r",
                  labels={"coefficient": "Coefficient (scaled)", "feature": ""})
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Risk Score Distribution (Test Set)")
    fig = px.histogram(preds, x="churn_probability", color="actual_churn",
                        nbins=30, barmode="overlay",
                        labels={"churn_probability": "Predicted Churn Probability"},
                        color_discrete_map={0: "lightblue", 1: "salmon"})
    st.plotly_chart(fig, use_container_width=True)

# ============ TAB 3: A/B TEST ============
with tab3:
    col1, col2, col3 = st.columns(3)
    col1.metric("Control Churn Rate", "7.11%")
    col2.metric("Treatment Churn Rate", "3.90%", delta="-3.21pp", delta_color="inverse")
    col3.metric("Relative Reduction", "45.1%")

    st.subheader("Primary Result: 30-Day Churn by Group")
    ab_summary = ab.groupby("group")["churned_30d"].mean().reset_index()
    fig = px.bar(ab_summary, x="group", y="churned_30d", color="group",
                  labels={"churned_30d": "30-Day Churn Rate"})
    fig.update_layout(yaxis_tickformat=".1%")
    st.plotly_chart(fig, use_container_width=True)

    st.info("**Statistical significance**: z=-3.96, p=0.0001. 95% CI for the difference: (1.62pp, 4.79pp). "
            "Achieved power: 97.9% (well-powered).")

    st.subheader("Segment Analysis: Effect by VLR (Active Subscriber) Status")
    segment_data = pd.DataFrame({
        "Segment": ["Active (VLR=1)", "Inactive (VLR=0)"],
        "Churn Reduction (pp)": [4.27, 0.13],
        "p-value": [0.0000, 0.9576],
        "Significant": ["Yes", "No"]
    })
    st.dataframe(segment_data, use_container_width=True, hide_index=True)

    st.success("**Recommendation**: Roll out the retention voucher to VLR-active high-risk customers "
               "(~2,514 customers). Estimated net benefit: **₹1,61,953 over 6 months** after voucher costs. "
               "The offer shows no effect for VLR-inactive customers - a different intervention is needed for this segment.")