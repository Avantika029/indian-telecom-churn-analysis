"""
A/B Test Layer: Retention Offer Campaign
-----------------------------------------
Scenario: Marketing team wants to test whether sending a 10% recharge
discount voucher to HIGH-CHURN-RISK customers reduces 30-day churn.

We:
1. Score each customer's churn risk using observable pre-experiment features.
2. Filter to "high-risk" customers (top ~30% by risk).
3. Randomly assign to Treatment (received offer) vs Control (no offer).
4. Simulate a treatment effect: the offer reduces churn probability by
   ~4-6 percentage points (absolute), with some heterogeneity.
5. Output an experiment dataset ready for power analysis + significance testing.
"""

import numpy as np
import pandas as pd

np.random.seed(123)

df = pd.read_csv("/home/claude/indian_telecom_churn.csv")

# ----------------------------------------------------------------------
# 1. Recompute a risk score from observable pre-experiment features
# ----------------------------------------------------------------------
operator_churn_base = {"Jio": 0.04, "Airtel": 0.05, "Vi": 0.14, "BSNL": 0.16}
base_churn = df["operator"].map(operator_churn_base).values

risk_score = base_churn.copy()
risk_score += (df["num_complaints_6m"] >= 2) * 0.10
risk_score += (df["network_rating"] <= 2) * 0.08
risk_score += (df["days_since_last_recharge"] > 45) * 0.12
risk_score += (df["is_active_vlr"] == 0) * 0.20
risk_score += (df["tenure_months"] < 3) * 0.07
risk_score -= (df["tenure_months"] > 36) * 0.04
risk_score -= (df["has_bundle"] == 1) * 0.05
risk_score -= (df["plan_type"] == "Postpaid") * 0.03
risk_score = np.clip(risk_score, 0.01, 0.95)

df["risk_score"] = risk_score.round(3)

# ----------------------------------------------------------------------
# 2. Define eligible population: high-risk customers (top ~30%)
# ----------------------------------------------------------------------
risk_threshold = df["risk_score"].quantile(0.70)
eligible = df[df["risk_score"] >= risk_threshold].copy()

print(f"Total customers: {len(df)}")
print(f"High-risk threshold (70th pct): {risk_threshold:.3f}")
print(f"Eligible (high-risk) customers: {len(eligible)} ({len(eligible)/len(df):.1%})")

# ----------------------------------------------------------------------
# 3. Random assignment - Treatment (offer) vs Control, 50/50 split
# ----------------------------------------------------------------------
eligible = eligible.reset_index(drop=True)
eligible["group"] = np.random.choice(["Treatment", "Control"], size=len(eligible), p=[0.5, 0.5])

# ----------------------------------------------------------------------
# 4. Simulate experiment outcome: churned_30d
# ----------------------------------------------------------------------
baseline_30d_prob = eligible["risk_score"] * 0.35  # scale to a 30-day window

treatment_effect = np.where(
    eligible["group"] == "Treatment",
    np.where(
        eligible["num_complaints_6m"] >= 2,
        -0.07,    # offer works well for complaint-driven churners
        np.where(eligible["is_active_vlr"] == 0, -0.01,  # barely helps dormant users
                 -0.05)  # average effect
    ),
    0.0  # no effect for control
)

noise = np.random.normal(0, 0.01, size=len(eligible))
final_prob = np.clip(baseline_30d_prob + treatment_effect + noise, 0.01, 0.95)

eligible["churned_30d"] = (np.random.rand(len(eligible)) < final_prob).astype(int)

# Voucher redemption (Treatment only, ~60% redemption rate)
eligible["voucher_redeemed"] = np.where(
    eligible["group"] == "Treatment",
    np.random.choice([1, 0], size=len(eligible), p=[0.60, 0.40]),
    0
)

# Secondary metric: ARPU change (INR) over the 30-day window
arpu_change = np.random.normal(0, 15, size=len(eligible))
arpu_change += np.where(
    (eligible["group"] == "Treatment") & (eligible["churned_30d"] == 0),
    np.random.normal(25, 10, size=len(eligible)),
    0
)
eligible["arpu_change_30d_inr"] = arpu_change.round(2)

# ----------------------------------------------------------------------
# 5. Save experiment dataset
# ----------------------------------------------------------------------
experiment_cols = [
    "customer_id", "operator", "circle", "circle_type", "plan_type",
    "tenure_months", "num_complaints_6m", "network_rating",
    "days_since_last_recharge", "is_active_vlr", "risk_score",
    "group", "voucher_redeemed", "churned_30d", "arpu_change_30d_inr"
]
experiment_df = eligible[experiment_cols]
experiment_df.to_csv("/home/claude/retention_ab_test.csv", index=False)

# ----------------------------------------------------------------------
# 6. Quick summary stats (for sanity check before formal analysis)
# ----------------------------------------------------------------------
summary = experiment_df.groupby("group").agg(
    n=("customer_id", "count"),
    churn_rate_30d=("churned_30d", "mean"),
    avg_arpu_change=("arpu_change_30d_inr", "mean"),
    voucher_redemption=("voucher_redeemed", "mean")
).round(4)

print(f"\nExperiment dataset shape: {experiment_df.shape}")
print(f"\nGroup summary:\n{summary}")

abs_diff = summary.loc["Control", "churn_rate_30d"] - summary.loc["Treatment", "churn_rate_30d"]
print(f"\nAbsolute churn reduction (Control - Treatment): {abs_diff:.2%}")
