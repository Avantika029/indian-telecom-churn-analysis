# 📡 Indian Telecom Churn Analysis

> End-to-end data science project — churn prediction and retention experiment for the Indian telecom market, calibrated to TRAI December 2025 operator statistics.

**[🚀 Live Dashboard →](https://indian-telecom-churn-analysis-ogucbshjr8bxfbcld3lxcu.streamlit.app/)** &nbsp;|&nbsp; **[GitHub →](https://github.com/Avantika029/indian-telecom-churn-analysis)**

---

## What this project covers

| Phase | Notebook | What was done |
|-------|----------|---------------|
| EDA | `01_eda.ipynb` | Signal discovery across 20 features; identified VLR status and recharge recency as dominant churn drivers |
| Preprocessing | `02_preprocessing.ipynb` | Feature engineering, one-hot encoding, class imbalance handling |
| Modelling | `03_modeling.ipynb` | Compared Logistic Regression, Random Forest, XGBoost; selected on ROC-AUC |
| A/B Testing | `04_ab_test.ipynb` | Causal inference on a 10% discount voucher experiment; HTE analysis by segment |
| SHAP | `03_shap_section.ipynb` | Individual prediction explanations via waterfall charts |
| Dashboard | `dashboard/dashboard_app.py` | Interactive Streamlit app with live risk scorer |

---

## Dataset

**10,000 synthetic subscribers** calibrated to real TRAI Dec 2025 market share:
Jio 39.3% · Airtel 37.2% · Vi 16.0% · BSNL 7.5%

| Column | Description |
|--------|-------------|
| `operator` | Jio / Airtel / Vi / BSNL |
| `is_active_vlr` | Whether SIM is active on the network's Visitor Location Register |
| `days_since_last_recharge` | Recency of last top-up |
| `num_complaints_6m` | Complaints filed in past 6 months |
| `churn` | Target — 1 if customer churned, 0 if retained |

Overall churn rate: **10.18%** · Vi: 21.2% · BSNL: 22.1% · Airtel: 7.1% · Jio: 6.6%

---

## Key findings

### 1 — VLR status is the strongest single signal

Customers whose SIM is inactive on the network's VLR churn at **31.7%** versus **8.7%** for active subscribers — a 3.6× gap. Detectable in real-time from network data, making it actionable before a customer shows any behavioural sign of leaving.

### 2 — Recharge recency has a cliff at 45 days

Churn is flat at ~9% for customers who recharged within the last 45 days. Beyond that it jumps to over 21% — a clean, operationalisable early-warning rule.

### 3 — Random Forest's 88% accuracy was misleading

| Model | ROC-AUC | Recall | F1 |
|-------|---------|--------|----|
| Logistic Regression | **0.757** | **0.627** | **0.308** |
| Random Forest | 0.731 | 0.108 | 0.158 |
| XGBoost (default) | 0.728 | 0.466 | 0.292 |
| XGBoost (tuned) | 0.748 | 0.623 | 0.306 |

Random Forest achieved 88.3% accuracy by predicting "stay" for nearly everyone — catching only 10.8% of actual churners. With a 10:1 class imbalance, accuracy is the wrong metric. Logistic Regression with `class_weight='balanced'` was selected for its recall and ROC-AUC.

### 4 — The 10% voucher experiment worked, but only for active subscribers

3,163 high-risk customers were randomly assigned to receive a discount voucher (Treatment) or not (Control).

| | Control | Treatment |
|--|---------|-----------|
| 30-day churn | 7.11% | 3.90% |
| Absolute reduction | — | **−3.21pp** |
| Relative reduction | — | **−45.1%** |
| p-value | — | 0.0001 |
| 95% CI | — | (1.62pp, 4.79pp) |

HTE analysis revealed VLR-active customers responded strongly (−4.27pp, p<0.0001), while VLR-inactive customers showed no effect (−0.13pp, p=0.96). **Estimated 6-month net benefit (active segment only): ₹1,61,953.**

---

## Model coefficients

```
operator_Vi          +0.487   ← strongest churn signal
dormant_45d_flag     +0.311
high_complaints_flag +0.308
operator_BSNL        +0.266
is_active_vlr        −0.271
tenure_growing_4_12m −0.325
has_bundle           −0.353   ← strongest retention signal
```

---

## Running locally

```bash
git clone https://github.com/Avantika029/indian-telecom-churn-analysis
cd indian-telecom-churn-analysis
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt

python src/generate_telecom_data.py
python src/generate_ab_test_data.py

streamlit run dashboard/dashboard_app.py
```

---

## Project structure

```
indian-telecom-churn-analysis/
├── data/
│   ├── raw/
│   │   ├── indian_telecom_churn.csv
│   │   └── retention_ab_test.csv
│   └── processed/
│       ├── X_train.csv / X_test.csv
│       ├── y_train.csv / y_test.csv
│       └── test_predictions.csv
├── notebooks/
│   ├── 01_eda.ipynb
│   ├── 02_preprocessing.ipynb
│   ├── 03_modeling.ipynb
│   ├── 03_shap_section.ipynb
│   └── 04_ab_test.ipynb
├── src/
│   ├── generate_telecom_data.py
│   └── generate_ab_test_data.py
├── models/
│   ├── logistic_regression_churn.pkl
│   └── scaler.pkl
├── dashboard/
│   └── dashboard_app.py
├── requirements.txt
└── README.md
```

---

*Synthetic dataset calibrated to TRAI subscriber statistics, December 2025.*
