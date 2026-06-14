"""
Synthetic Indian Telecom Customer Churn Dataset Generator
Calibrated to TRAI December 2025 statistics:
- Operator market share (wireless): Jio 39.31%, Airtel 37.24%, Vi 15.98%, BSNL 7.46%
- Overall tele-density: 88.41%
- Active subscriber (VLR) ratio ~93% nationally, but Vi ~85%, BSNL ~58-61% (much lower)
- Monthly MNP/churn rate baseline ~1.3% (we use an elevated synthetic rate ~6-9%
  to create a richer, modelable churn dataset typical of analyst portfolio projects)
"""

import numpy as np
import pandas as pd
from faker import Faker

np.random.seed(42)
fake = Faker("en_IN")
Faker.seed(42)

N = 10000  # number of customers

# ----------------------------------------------------------------------
# 1. Operator assignment (TRAI Dec-2025 market share)
# ----------------------------------------------------------------------
operators = ["Jio", "Airtel", "Vi", "BSNL"]
operator_probs = [0.3931, 0.3724, 0.1598, 0.0747]
operator = np.random.choice(operators, size=N, p=operator_probs)

# Base churn propensity by operator (Vi & BSNL have lower active-user ratios -> higher churn)
operator_churn_base = {"Jio": 0.04, "Airtel": 0.05, "Vi": 0.14, "BSNL": 0.16}

# ----------------------------------------------------------------------
# 2. Indian circles (telecom regions) - mix of metro, urban, rural
# ----------------------------------------------------------------------
circles = [
    "Delhi", "Mumbai", "Maharashtra", "Karnataka", "Tamil Nadu",
    "Andhra Pradesh & Telangana", "Gujarat", "Rajasthan", "UP East",
    "UP West", "West Bengal", "Punjab", "Kerala", "Madhya Pradesh",
    "Bihar & Jharkhand", "Odisha", "Assam & North East"
]
circle_type_map = {
    "Delhi": "Metro", "Mumbai": "Metro", "Maharashtra": "Urban",
    "Karnataka": "Urban", "Tamil Nadu": "Urban",
    "Andhra Pradesh & Telangana": "Urban", "Gujarat": "Urban",
    "Rajasthan": "Rural", "UP East": "Rural", "UP West": "Rural",
    "West Bengal": "Urban", "Punjab": "Urban", "Kerala": "Urban",
    "Madhya Pradesh": "Rural", "Bihar & Jharkhand": "Rural",
    "Odisha": "Rural", "Assam & North East": "Rural"
}
circle_probs = [0.10, 0.10, 0.08, 0.08, 0.07, 0.06, 0.06, 0.06, 0.07,
                 0.06, 0.06, 0.04, 0.04, 0.05, 0.05, 0.04, 0.03]
circle_probs = np.array(circle_probs) / sum(circle_probs)
circle = np.random.choice(circles, size=N, p=circle_probs)
circle_type = np.array([circle_type_map[c] for c in circle])

# ----------------------------------------------------------------------
# 3. Customer demographics
# ----------------------------------------------------------------------
customer_id = [f"CUST{100000+i}" for i in range(N)]
name = [fake.name() for _ in range(N)]
age = np.clip(np.random.normal(34, 12, N).astype(int), 18, 75)
gender = np.random.choice(["Male", "Female"], size=N, p=[0.58, 0.42])

# ----------------------------------------------------------------------
# 4. Plan & usage attributes
# ----------------------------------------------------------------------
plan_type = np.random.choice(
    ["Prepaid", "Postpaid"], size=N, p=[0.85, 0.15]  # India is heavily prepaid
)

# Monthly recharge / plan amount in INR, varies by plan type
plan_amount = np.where(
    plan_type == "Prepaid",
    np.round(np.random.choice([149, 179, 199, 239, 299, 349, 399, 449, 599, 719],
                               size=N, p=[0.08, 0.1, 0.15, 0.15, 0.18, 0.12, 0.1, 0.07, 0.03, 0.02]), 0),
    np.round(np.random.choice([399, 499, 599, 699, 999, 1199], size=N,
                               p=[0.15, 0.25, 0.25, 0.2, 0.1, 0.05]), 0)
)

tenure_months = np.clip(np.random.exponential(scale=24, size=N).astype(int), 1, 120)

# Data usage in GB/month
data_usage_gb = np.clip(np.random.gamma(shape=2.0, scale=6.0, size=N), 0.5, 80).round(1)

# Recharge frequency / regularity - days since last recharge
days_since_last_recharge = np.clip(np.random.exponential(scale=20, size=N).astype(int), 0, 120)

# Number of complaints in last 6 months
num_complaints = np.random.poisson(lam=0.6, size=N)
num_complaints = np.clip(num_complaints, 0, 8)

# Network quality rating (1-5, self-reported via app/survey)
network_rating = np.clip(np.round(np.random.normal(3.6, 1.0, N)), 1, 5).astype(int)

# Payment method
payment_method = np.random.choice(
    ["UPI", "Debit/Credit Card", "Net Banking", "Cash/Retail Recharge", "Wallet (Paytm/PhonePe)"],
    size=N, p=[0.40, 0.12, 0.08, 0.25, 0.15]
)

# Has DTH / broadband bundle (cross-sell indicator)
has_bundle = np.random.choice([0, 1], size=N, p=[0.78, 0.22])

# 5G availability/usage flag
uses_5g = np.random.choice([0, 1], size=N, p=[0.55, 0.45])

# ----------------------------------------------------------------------
# 5. Active/VLR status (TRAI: Vi ~85%, BSNL ~58-61%, Jio/Airtel ~98%)
# ----------------------------------------------------------------------
vlr_active_prob = {"Jio": 0.985, "Airtel": 0.99, "Vi": 0.85, "BSNL": 0.60}
is_active_vlr = np.array([
    np.random.choice([1, 0], p=[vlr_active_prob[op], 1 - vlr_active_prob[op]])
    for op in operator
])

# ----------------------------------------------------------------------
# 6. Churn label - logistic combination of risk factors
# ----------------------------------------------------------------------
base_churn = np.array([operator_churn_base[op] for op in operator])

# Risk multipliers
risk_score = base_churn.copy()
risk_score += (num_complaints >= 2) * 0.10
risk_score += (network_rating <= 2) * 0.08
risk_score += (days_since_last_recharge > 45) * 0.12
risk_score += (is_active_vlr == 0) * 0.20
risk_score += (tenure_months < 3) * 0.07          # new customers churn more
risk_score -= (tenure_months > 36) * 0.04          # loyal customers churn less
risk_score -= (has_bundle == 1) * 0.05             # bundled customers stickier
risk_score -= (plan_type == "Postpaid") * 0.03     # postpaid slightly stickier

risk_score = np.clip(risk_score, 0.01, 0.95)
churn = (np.random.rand(N) < risk_score).astype(int)

# ----------------------------------------------------------------------
# 7. Assemble dataframe
# ----------------------------------------------------------------------
df = pd.DataFrame({
    "customer_id": customer_id,
    "name": name,
    "age": age,
    "gender": gender,
    "circle": circle,
    "circle_type": circle_type,
    "operator": operator,
    "plan_type": plan_type,
    "plan_amount_inr": plan_amount.astype(int),
    "tenure_months": tenure_months,
    "data_usage_gb": data_usage_gb,
    "days_since_last_recharge": days_since_last_recharge,
    "num_complaints_6m": num_complaints,
    "network_rating": network_rating,
    "payment_method": payment_method,
    "has_bundle": has_bundle,
    "uses_5g": uses_5g,
    "is_active_vlr": is_active_vlr,
    "churn": churn,
})

# Add a registration date for realism
df["registration_date"] = [
    fake.date_between(start_date="-10y", end_date="-1m") for _ in range(N)
]

df.to_csv("/home/claude/indian_telecom_churn.csv", index=False)

print(f"Dataset shape: {df.shape}")
print(f"\nOverall churn rate: {df['churn'].mean():.2%}")
print(f"\nOperator distribution:\n{df['operator'].value_counts(normalize=True).round(3)}")
print(f"\nChurn rate by operator:\n{df.groupby('operator')['churn'].mean().round(3)}")
print(f"\nChurn rate by circle type:\n{df.groupby('circle_type')['churn'].mean().round(3)}")
print(f"\nSample rows:\n{df.head(3)}")
