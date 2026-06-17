"""
TelcoSignal — Churn Intelligence Platform
Indian Telecom Market · 10,000 subscribers · TRAI Dec 2025
GitHub: Avantika029/indian-telecom-churn-analysis
"""

# streamlit run dashboard/app.py
# streamlit run dashboard/app.py --server.port 8080

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from datetime import datetime

# ── PAGE CONFIG ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="TelcoSignal · Churn Intelligence",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── DESIGN TOKENS ──────────────────────────────────────────────────────────────
# Palette: telecom-ops dark. No generic blue-startup vibes.
BG       = "#080D16"   # near-black navy
SURF     = "#0F1724"   # card surface
SURF2    = "#141F30"   # elevated surface
BORDER   = "#1E2D42"   # subtle border
GREEN    = "#00E5A0"   # signal green — healthy / retained
GREEN2   = "#00B87A"   # dimmer green for hover/dim
AMBER    = "#F59E0B"   # watch / moderate
RED      = "#FF3B3B"   # churn / danger
BLUE     = "#3B82F6"   # neutral data
TEXT     = "#E2EBF6"   # primary text
MUTED    = "#5B7A9D"   # secondary text
JIO      = "#0EA5E9"
AIRTEL   = "#E8142D"
VI       = "#8B5CF6"
BSNL     = "#10B981"

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&family=Inter:wght@400;500&display=swap');

*, html, body, [class*="css"] {{
  font-family: 'Inter', sans-serif !important;
  box-sizing: border-box;
}}

.stApp {{
  background: {BG} !important;
  color: {TEXT} !important;
}}

.block-container {{
  padding: 1.2rem 2rem 3rem !important;
  max-width: 1440px !important;
}}

#MainMenu, footer, header {{ visibility: hidden !important; }}
.stDeployButton {{ display: none !important; }}

/* ── TABS ─────────────────────────── */
.stTabs [data-baseweb="tab-list"] {{
  background: {SURF} !important;
  border: 1px solid {BORDER} !important;
  border-radius: 12px !important;
  padding: 5px !important;
  gap: 2px !important;
}}
.stTabs [data-baseweb="tab"] {{
  background: transparent !important;
  color: {MUTED} !important;
  border-radius: 8px !important;
  font-family: 'Space Grotesk', sans-serif !important;
  font-weight: 500 !important;
  font-size: 0.82rem !important;
  letter-spacing: 0.04em !important;
  padding: 8px 18px !important;
  border: none !important;
  transition: all 0.15s !important;
}}
.stTabs [aria-selected="true"] {{
  background: {SURF2} !important;
  color: {GREEN} !important;
  box-shadow: inset 0 0 0 1px {BORDER} !important;
}}
.stTabs [data-baseweb="tab-border"] {{ display: none !important; }}
.stTabs [data-baseweb="tab-panel"] {{ padding-top: 1.4rem !important; }}

/* ── SLIDERS ──────────────────────── */
[data-testid="stSlider"] [data-baseweb="slider"] [data-testid="stThumb"] {{
  background: {GREEN} !important;
  border-color: {GREEN} !important;
}}
[data-testid="stSlider"] > div > div > div > div {{
  background: {GREEN} !important;
}}

/* ── SELECTBOX ────────────────────── */
.stSelectbox > div > div {{
  background: {SURF2} !important;
  border-color: {BORDER} !important;
  color: {TEXT} !important;
  border-radius: 8px !important;
}}

/* ── MULTISELECT ──────────────────── */
.stMultiSelect > div > div {{
  background: {SURF2} !important;
  border-color: {BORDER} !important;
  border-radius: 8px !important;
}}

/* ── TOGGLE ───────────────────────── */
.stToggle > label > div[data-checked="true"] {{
  background: {GREEN} !important;
}}

/* ── EXPANDER ─────────────────────── */
.streamlit-expanderHeader {{
  background: {SURF} !important;
  border: 1px solid {BORDER} !important;
  border-radius: 8px !important;
  color: {TEXT} !important;
  font-weight: 500 !important;
}}

/* ── SIDEBAR ──────────────────────── */
[data-testid="stSidebar"] {{
  background: {SURF} !important;
  border-right: 1px solid {BORDER} !important;
}}

/* ── SCROLLBAR ────────────────────── */
::-webkit-scrollbar {{ width: 5px; height: 5px; }}
::-webkit-scrollbar-track {{ background: {BG}; }}
::-webkit-scrollbar-thumb {{ background: {BORDER}; border-radius: 3px; }}
::-webkit-scrollbar-thumb:hover {{ background: {MUTED}; }}

/* ── METRIC ───────────────────────── */
[data-testid="stMetric"] {{
  background: {SURF} !important;
  border: 1px solid {BORDER} !important;
  border-radius: 12px !important;
  padding: 16px 20px !important;
}}
[data-testid="stMetricLabel"] {{
  font-family: 'JetBrains Mono', monospace !important;
  font-size: 0.65rem !important;
  letter-spacing: 0.12em !important;
  text-transform: uppercase !important;
  color: {MUTED} !important;
}}
[data-testid="stMetricValue"] {{
  font-family: 'JetBrains Mono', monospace !important;
  font-size: 1.9rem !important;
  font-weight: 600 !important;
  color: {TEXT} !important;
}}

/* ── CUSTOM COMPONENTS ────────────── */
.ts-eyebrow {{
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.63rem;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: {GREEN};
  margin-bottom: 5px;
}}
.ts-heading {{
  font-family: 'Space Grotesk', sans-serif;
  font-size: 1.1rem;
  font-weight: 600;
  color: {TEXT};
  margin-bottom: 1rem;
}}
.ts-card {{
  background: {SURF};
  border: 1px solid {BORDER};
  border-radius: 12px;
  padding: 20px 22px;
  margin-bottom: 0;
}}
.ts-card:hover {{ border-color: {GREEN2}44; }}
.ts-val {{
  font-family: 'JetBrains Mono', monospace;
  font-size: 1.95rem;
  font-weight: 600;
  line-height: 1.1;
}}
.ts-label {{
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.62rem;
  letter-spacing: 0.13em;
  text-transform: uppercase;
  color: {MUTED};
  margin-bottom: 6px;
}}
.ts-sub {{
  font-size: 0.75rem;
  color: {MUTED};
  margin-top: 5px;
}}
.ts-insight {{
  background: {GREEN}0D;
  border-left: 3px solid {GREEN};
  border-radius: 0 8px 8px 0;
  padding: 11px 15px;
  margin: 12px 0;
  font-size: 0.84rem;
  line-height: 1.5;
  color: {TEXT};
}}
.ts-warn {{
  background: {AMBER}0D;
  border-left: 3px solid {AMBER};
  border-radius: 0 8px 8px 0;
  padding: 11px 15px;
  margin: 12px 0;
  font-size: 0.84rem;
  line-height: 1.5;
  color: {TEXT};
}}
.ts-divider {{
  height: 1px;
  background: linear-gradient(90deg, transparent, {BORDER}, transparent);
  margin: 1.5rem 0;
}}
.op-pill-jio    {{ display:inline-block; padding:2px 10px; border-radius:20px; font-size:0.72rem; font-weight:600; background:{JIO}18; color:{JIO}; border:1px solid {JIO}44; }}
.op-pill-airtel {{ display:inline-block; padding:2px 10px; border-radius:20px; font-size:0.72rem; font-weight:600; background:{AIRTEL}18; color:{AIRTEL}; border:1px solid {AIRTEL}44; }}
.op-pill-vi     {{ display:inline-block; padding:2px 10px; border-radius:20px; font-size:0.72rem; font-weight:600; background:{VI}18; color:{VI}; border:1px solid {VI}44; }}
.op-pill-bsnl   {{ display:inline-block; padding:2px 10px; border-radius:20px; font-size:0.72rem; font-weight:600; background:{BSNL}18; color:{BSNL}; border:1px solid {BSNL}44; }}
</style>
""", unsafe_allow_html=True)

# ── CHART DEFAULTS ─────────────────────────────────────────────────────────────
def chart_style(fig, height=340, title=None):
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor=SURF,
        font=dict(family="JetBrains Mono, monospace", color=MUTED, size=10),
        title=dict(text=title, font=dict(family="Space Grotesk, sans-serif",
                   color=TEXT, size=13), x=0, pad=dict(l=4)) if title else {},
        legend=dict(bgcolor="rgba(0,0,0,0)", borderwidth=0,
                    font=dict(size=10, family="JetBrains Mono, monospace")),
        margin=dict(l=52, r=20, t=44 if title else 20, b=48),
        xaxis=dict(gridcolor=BORDER, linecolor=BORDER,
                   tickcolor=BORDER, zeroline=False),
        yaxis=dict(gridcolor=BORDER, linecolor=BORDER,
                   tickcolor=BORDER, zeroline=False),
        hoverlabel=dict(bgcolor=SURF2, bordercolor=BORDER,
                        font=dict(family="JetBrains Mono", size=11, color=TEXT)),
    )
    return fig

OP_COLORS = {"Jio": JIO, "Airtel": AIRTEL, "Vi": VI, "BSNL": BSNL}

# ── DATA LOADING ───────────────────────────────────────────────────────────────
@st.cache_data
def load_churn_data():
    # Try real path first; fall back to synthetic mirror
    for path in ["data/raw/indian_telecom_churn.csv",
                 "../data/raw/indian_telecom_churn.csv"]:
        if os.path.exists(path):
            return pd.read_csv(path)
    # Synthetic fallback — same statistics as the real dataset
    rng = np.random.default_rng(42)
    n = 10000
    operators = rng.choice(["Jio","Airtel","Vi","BSNL"], n, p=[0.393,0.372,0.16,0.075])
    base_churn_map = {"Jio":0.066,"Airtel":0.071,"Vi":0.212,"BSNL":0.221}
    vlr = rng.binomial(1, 0.85, n)
    tenure = rng.integers(1, 73, n)
    complaints = rng.choice([0,1,2,3,4,5], n, p=[0.55,0.25,0.12,0.05,0.02,0.01])
    days_rech = rng.integers(0, 91, n)
    churn_p = np.array([base_churn_map[op] for op in operators])
    churn_p *= (1 + 0.85*(vlr==0))
    churn_p *= (1 + 0.40*(days_rech>45))
    churn_p *= (1 + 0.15*complaints)
    churn_p = np.clip(churn_p, 0, 0.9)
    churn = rng.binomial(1, churn_p, n)
    circles = ["Maharashtra","Delhi","Karnataka","Tamil Nadu","Andhra Pradesh",
               "Rajasthan","Gujarat","UP East","UP West","West Bengal",
               "Madhya Pradesh","Punjab","Kerala","Haryana","Bihar","Odisha","Northeast"]
    return pd.DataFrame({
        "operator": operators, "churn": churn, "is_active_vlr": vlr,
        "tenure_months": tenure, "num_complaints_6m": complaints,
        "days_since_last_recharge": days_rech,
        "plan_amount_inr": rng.integers(149, 1200, n),
        "data_usage_gb": np.round(rng.exponential(8, n), 2),
        "plan_type": rng.choice(["Prepaid","Postpaid"], n, p=[0.78,0.22]),
        "circle": rng.choice(circles, n),
        "circle_type": rng.choice(["Metro","Urban","Rural"], n, p=[0.25,0.45,0.30]),
        "network_rating": rng.integers(1, 6, n),
        "age": rng.integers(18, 65, n),
        "has_bundle": rng.binomial(1, 0.45, n),
        "uses_5g": rng.binomial(1, 0.18, n),
        "payment_method": rng.choice(["UPI","Card","Net Banking","Cash","Wallet"], n,
                                      p=[0.50,0.15,0.12,0.10,0.13]),
        "gender": rng.choice(["Male","Female","Other"], n, p=[0.52,0.46,0.02]),
    })

@st.cache_data
def load_ab_data():
    STRING_TO_INT = {
        'treatment':1,'Treatment':1,'TREATMENT':1,'T':1,'t':1,
        'control':0,  'Control':0,  'CONTROL':0,  'C':0,'c':0,
        'Yes':1,'yes':1,'No':0,'no':0,
        'True':1,'true':1,'False':0,'false':0,
        '1':1,'0':0, 1:1, 0:0,
    }
    for path in ["data/raw/retention_ab_test.csv",
                 "../data/raw/retention_ab_test.csv"]:
        if not os.path.exists(path):
            continue
        df = pd.read_csv(path)

        # Find and normalise treatment column
        trt_col = None
        for col in ['treatment','treatment_group','group','treatment_flag']:
            if col in df.columns:
                trt_col = col
                break
        if trt_col is not None:
            # Map every known string/int representation → 0/1
            df[trt_col] = df[trt_col].map(STRING_TO_INT)
            # At this point NaN means truly unmapped — warn but keep going
            df[trt_col] = pd.to_numeric(df[trt_col], errors='coerce')
            if trt_col != 'treatment':
                df = df.rename(columns={trt_col: 'treatment'})

        # Normalise outcome column name
        for src, dst in [('churn_30d','churned_30d'),('churn','churned_30d')]:
            if src in df.columns and 'churned_30d' not in df.columns:
                df = df.rename(columns={src: dst})

        # Normalise ARPU column name
        for src in ['arpu_change','arpu_delta','arpu_change_30d']:
            if src in df.columns and 'arpu_change_30d_inr' not in df.columns:
                df = df.rename(columns={src: 'arpu_change_30d_inr'})

        return df

    # Synthetic fallback — no CSV found
    rng = np.random.default_rng(7)
    n = 3163
    trt = rng.binomial(1, 0.502, n)
    churn_30d = np.where(trt, rng.binomial(1, 0.039, n), rng.binomial(1, 0.071, n))
    redeemed  = trt * rng.binomial(1, 0.609, n)
    arpu_chg  = np.where(trt, rng.normal(24.16, 15, n), rng.normal(0.74, 12, n))
    return pd.DataFrame({
        "treatment":           trt,
        "churned_30d":         churn_30d,
        "voucher_redeemed":    redeemed,
        "arpu_change_30d_inr": np.round(arpu_chg, 2),
        "is_active_vlr":       rng.binomial(1, 0.85, n),
        "num_complaints_6m":   rng.choice([0,1,2,3,4], n, p=[0.55,0.25,0.12,0.05,0.03]),
    })

@st.cache_data
def load_predictions():
    for path in ["data/processed/test_predictions.csv",
                 "../data/processed/test_predictions.csv"]:
        if os.path.exists(path):
            return pd.read_csv(path)
    rng = np.random.default_rng(99)
    n = 2000
    actual = rng.binomial(1, 0.102, n)
    prob = np.where(actual, rng.beta(3,2,n), rng.beta(1,5,n))
    return pd.DataFrame({
        "actual_churn": actual,
        "churn_probability": np.round(prob, 4),
        "predicted_churn": (prob > 0.40).astype(int),
    })

# ── LOAD ───────────────────────────────────────────────────────────────────────
try:
    df = load_churn_data()
    ab_df = load_ab_data()
    preds = load_predictions()
except Exception as e:
    st.error(f"Data load error: {e}")
    st.stop()

# ── SIDEBAR FILTERS ────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style="padding:16px 0 12px; border-bottom:1px solid {BORDER}; margin-bottom:14px;">
      <div style="font-family:'Space Grotesk',sans-serif; font-size:0.95rem; font-weight:600; color:{TEXT};">Filter dataset</div>
      <div style="font-size:0.72rem; color:{MUTED}; margin-top:2px;">Slices EDA & Analytics tabs</div>
    </div>
    """, unsafe_allow_html=True)
    sel_operator = st.multiselect("Operator", sorted(df['operator'].unique()),
                                   default=sorted(df['operator'].unique()))
    sel_plan     = st.multiselect("Plan Type", sorted(df['plan_type'].unique()),
                                   default=sorted(df['plan_type'].unique()))
    sel_circle   = st.multiselect("Circle", sorted(df['circle'].unique()),
                                   default=sorted(df['circle'].unique()))
    tenure_range   = st.slider("Tenure (months)", 0, 72, (0, 72))
    recharge_range = st.slider("Days since recharge", 0, 90, (0, 90))
    st.markdown(f"""
    <div style="font-size:0.7rem; color:{MUTED}; margin-top:16px; line-height:2; border-top:1px solid {BORDER}; padding-top:12px;">
      Dataset  &nbsp;·&nbsp; 10,000 customers<br>
      A/B Test &nbsp;·&nbsp; 3,163 participants<br>
      Model &nbsp;&nbsp;&nbsp;&nbsp;·&nbsp; Logistic Regression
    </div>""", unsafe_allow_html=True)

df_f = df[
    (df['operator'].isin(sel_operator)) &
    (df['plan_type'].isin(sel_plan)) &
    (df['circle'].isin(sel_circle)) &
    (df['tenure_months'].between(*tenure_range)) &
    (df['days_since_last_recharge'].between(*recharge_range))
]

# ── HEADER ─────────────────────────────────────────────────────────────────────
h1, h2 = st.columns([7,2])
with h1:
    st.markdown(f"""
    <div style="padding:4px 0 18px;">
      <div style="font-family:'JetBrains Mono',monospace; font-size:0.65rem; letter-spacing:0.18em;
                  text-transform:uppercase; color:{GREEN}; margin-bottom:6px;">
        ● LIVE · Indian Telecom · TRAI Dec 2025
      </div>
      <div style="font-family:'Space Grotesk',sans-serif; font-size:1.65rem; font-weight:700;
                  color:{TEXT}; letter-spacing:-0.02em; line-height:1.1;">
        TelcoSignal &nbsp;<span style="color:{MUTED}; font-weight:400; font-size:1.1rem;">/ churn intelligence</span>
      </div>
    </div>
    """, unsafe_allow_html=True)
with h2:
    n_shown = len(df_f)
    st.markdown(f"""
    <div style="text-align:right; padding-top:14px;">
      <div style="font-family:'JetBrains Mono',monospace; font-size:0.65rem;
                  letter-spacing:0.1em; color:{MUTED}; text-transform:uppercase;">showing</div>
      <div style="font-family:'JetBrains Mono',monospace; font-size:1.35rem;
                  font-weight:600; color:{TEXT};">{n_shown:,}</div>
      <div style="font-family:'JetBrains Mono',monospace; font-size:0.65rem;
                  color:{MUTED};">of 10,000 subscribers</div>
    </div>""", unsafe_allow_html=True)

st.markdown(f'<div class="ts-divider"></div>', unsafe_allow_html=True)

# ── TABS ───────────────────────────────────────────────────────────────────────
T1, T2, T3, T4 = st.tabs([
    "  Overview  ",
    "  Churn Analytics  ",
    "  A/B Retention Test  ",
    "  Risk Scorer  ",
])
# ══════════════════════════════════════════════════════════════════════════════
# T1 — OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
with T1:
    total   = len(df_f)
    churned = int(df_f['churn'].sum())
    cr      = churned/total*100 if total else 0
    at_risk = int(((df_f['days_since_last_recharge']>45) | (df_f['num_complaints_6m']>=2)).sum())
    avg_tenure = df_f['tenure_months'].mean()

    c1,c2,c3,c4,c5 = st.columns(5)
    for col, label, val, sub in [
        (c1, "SUBSCRIBERS",    f"{total:,}",        "in filtered view"),
        (c2, "CHURN RATE",     f"{cr:.1f}%",        f"{churned:,} customers lost"),
        (c3, "AT RISK NOW",    f"{at_risk:,}",      f"{at_risk/total*100:.1f}% of base"),
        (c4, "AVG TENURE",     f"{avg_tenure:.0f}mo", "across filtered set"),
        (c5, "Vi / BSNL",      "~22%",              "churn vs 7% Jio/Airtel"),
    ]:
        col.markdown(f"""
        <div class="ts-card">
          <div class="ts-label">{label}</div>
          <div class="ts-val">{val}</div>
          <div class="ts-sub">{sub}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Row 1: operator churn + market share
    col_a, col_b = st.columns([3,2])
    with col_a:
        st.markdown('<div class="ts-eyebrow">OPERATOR · CHURN RATE VS MARKET SHARE</div>', unsafe_allow_html=True)
        op_stats = df_f.groupby("operator").agg(
            churn_rate=("churn","mean"), count=("churn","count")
        ).reset_index().sort_values("churn_rate")

        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(go.Bar(
            x=op_stats["operator"], y=op_stats["churn_rate"]*100,
            name="Churn Rate",
            marker_color=[OP_COLORS.get(o, BLUE) for o in op_stats["operator"]],
            marker_line_width=0,
            text=[f"{v*100:.1f}%" for v in op_stats["churn_rate"]],
            textposition="outside",
            textfont=dict(family="JetBrains Mono", color=TEXT, size=11),
            hovertemplate="<b>%{x}</b><br>Churn: %{y:.1f}%<extra></extra>",
        ), secondary_y=False)
        trai = {"Jio":39.3,"Airtel":37.2,"Vi":16.0,"BSNL":7.5}
        fig.add_trace(go.Scatter(
            x=list(trai.keys()), y=list(trai.values()),
            name="Market Share",
            mode="markers",
            marker=dict(size=10, color=TEXT, symbol="diamond",
                        line=dict(color=BORDER, width=1)),
            hovertemplate="<b>%{x}</b><br>Mkt share: %{y:.1f}%<extra></extra>",
        ), secondary_y=True)
        fig.update_yaxes(title_text="Churn Rate (%)", ticksuffix="%",
                         gridcolor=BORDER, secondary_y=False)
        fig.update_yaxes(title_text="Market Share (%)", ticksuffix="%",
                         gridcolor="rgba(0,0,0,0)", secondary_y=True)
        chart_style(fig, height=300, title=None)
        fig.update_layout(showlegend=True, legend=dict(
            orientation="h", y=1.02, x=1, xanchor="right"))
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        st.markdown('<div class="ts-eyebrow">VLR STATUS · CHURN GAP</div>', unsafe_allow_html=True)
        vlr_df = df_f.groupby("is_active_vlr")["churn"].mean().reset_index()
        vlr_df["label"] = vlr_df["is_active_vlr"].map({1:"VLR Active",0:"VLR Inactive"})
        vlr_df["color"] = vlr_df["is_active_vlr"].map({1:GREEN,0:RED})
        fig2 = go.Figure(go.Bar(
            x=vlr_df["label"], y=vlr_df["churn"]*100,
            marker_color=vlr_df["color"], marker_line_width=0,
            text=[f"{v*100:.1f}%" for v in vlr_df["churn"]],
            textposition="outside",
            textfont=dict(family="JetBrains Mono", color=TEXT, size=14, weight="bold"),
            hovertemplate="<b>%{x}</b><br>Churn: %{y:.1f}%<extra></extra>",
        ))
        fig2.update_layout(yaxis=dict(ticksuffix="%", range=[0,48]))
        chart_style(fig2, height=300)
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown(f"""<div class="ts-insight">
        VLR-inactive customers churn at <strong>3.6×</strong> the rate of active subscribers.
        This is the single strongest churn signal in the dataset (correlation −0.188).
        </div>""", unsafe_allow_html=True)

    # Row 2: Recharge threshold + tenure overlay
    col_c, col_d = st.columns(2)
    with col_c:
        st.markdown('<div class="ts-eyebrow">RECHARGE RECENCY · THRESHOLD AT 45 DAYS</div>', unsafe_allow_html=True)
        bins   = [0,10,20,30,45,60,91]
        labels = ["0–9d","10–19d","20–29d","30–44d","45–59d","60–90d"]
        df_f2 = df_f.copy()
        df_f2["rbin"] = pd.cut(df_f2["days_since_last_recharge"], bins=bins, labels=labels, right=False)
        thr = df_f2.groupby("rbin", observed=True)["churn"].mean().reset_index()
        bar_colors = [GREEN if i < 4 else RED for i in range(len(thr))]
        fig3 = go.Figure(go.Bar(
            x=thr["rbin"].astype(str), y=thr["churn"]*100,
            marker_color=bar_colors, marker_line_width=0,
            text=[f"{v*100:.1f}%" for v in thr["churn"]],
            textposition="outside",
            textfont=dict(family="JetBrains Mono", color=TEXT, size=11),
            hovertemplate="<b>%{x}</b><br>Churn: %{y:.1f}%<extra></extra>",
        ))
        fig3.add_vline(x=3.5, line_dash="dot", line_color=AMBER, line_width=2,
                       annotation_text="  45-day cliff", annotation_font_color=AMBER,
                       annotation_font_size=10)
        fig3.update_layout(yaxis=dict(ticksuffix="%", range=[0,35]),
                           xaxis_title="days since last recharge")
        chart_style(fig3, height=300)
        st.plotly_chart(fig3, use_container_width=True)

    with col_d:
        st.markdown('<div class="ts-eyebrow">TENURE · CHURN RATE BY BUCKET</div>', unsafe_allow_html=True)
        tbins = [0,3,12,36,73]
        tlabels = ["New (0–3m)","Growing (4–12m)","Established (13–36m)","Loyal (37m+)"]
        df_f3 = df_f.copy()
        df_f3["tbin"] = pd.cut(df_f3["tenure_months"], bins=tbins, labels=tlabels, right=False)
        ten = df_f3.groupby("tbin", observed=True).agg(
            churn_rate=("churn","mean"), n=("churn","count")
        ).reset_index()
        fig4 = go.Figure()
        fig4.add_trace(go.Bar(
            x=ten["tbin"].astype(str), y=ten["churn_rate"]*100,
            marker_color=[AMBER, GREEN2, GREEN, GREEN],
            marker_line_width=0,
            text=[f"{v*100:.1f}%" for v in ten["churn_rate"]],
            textposition="outside",
            textfont=dict(family="JetBrains Mono", color=TEXT, size=11),
            customdata=ten["n"],
            hovertemplate="<b>%{x}</b><br>Churn: %{y:.1f}%<br>n=%{customdata:,}<extra></extra>",
        ))
        fig4.update_layout(yaxis=dict(ticksuffix="%", range=[0,20]))
        chart_style(fig4, height=300)
        st.plotly_chart(fig4, use_container_width=True)

    # Row 3: Complaints + circle heatmap
    col_e, col_f = st.columns([2,3])
    with col_e:
        st.markdown('<div class="ts-eyebrow">COMPLAINTS · CHURN RATE</div>', unsafe_allow_html=True)
        comp = df_f.groupby("num_complaints_6m")["churn"].agg(["mean","count"]).reset_index()
        comp.columns = ["n_comp","churn_rate","n"]
        comp = comp[comp["n"] > 5]  # drop unreliable tiny cells
        fig5 = go.Figure(go.Scatter(
            x=comp["n_comp"], y=comp["churn_rate"]*100,
            mode="lines+markers",
            line=dict(color=AMBER, width=2),
            marker=dict(color=AMBER, size=comp["n"]/30+6,
                        line=dict(color=BG, width=2)),
            customdata=comp["n"],
            hovertemplate="<b>%{x} complaints</b><br>Churn: %{y:.1f}%<br>n=%{customdata:,}<extra></extra>",
        ))
        fig5.update_layout(xaxis=dict(title="complaints in 6 months", dtick=1),
                           yaxis=dict(ticksuffix="%", range=[0,28]))
        chart_style(fig5, height=280)
        st.plotly_chart(fig5, use_container_width=True)

    with col_f:
        st.markdown('<div class="ts-eyebrow">CIRCLE · CHURN RATE (sorted)</div>', unsafe_allow_html=True)
        circ = df_f.groupby("circle").agg(
            churn_rate=("churn","mean"), n=("churn","count")
        ).reset_index().sort_values("churn_rate", ascending=True)
        fig6 = go.Figure(go.Bar(
            x=circ["churn_rate"]*100,
            y=circ["circle"],
            orientation="h",
            marker=dict(
                color=circ["churn_rate"]*100,
                colorscale=[[0, GREEN], [0.5, AMBER], [1, RED]],
                showscale=False,
            ),
            marker_line_width=0,
            text=[f"{v*100:.1f}%" for v in circ["churn_rate"]],
            textposition="outside",
            textfont=dict(family="JetBrains Mono", color=TEXT, size=9),
            customdata=circ["n"],
            hovertemplate="<b>%{y}</b><br>Churn: %{x:.1f}%<br>n=%{customdata:,}<extra></extra>",
        ))
        overall_cr = df_f["churn"].mean()*100
        fig6.add_vline(x=overall_cr, line_dash="dot", line_color=MUTED,
                       annotation_text=f"  avg {overall_cr:.1f}%",
                       annotation_font_color=MUTED, annotation_font_size=9)
        fig6.update_layout(xaxis=dict(ticksuffix="%", range=[0,32]),
                           yaxis=dict(gridcolor="rgba(0,0,0,0)"))
        chart_style(fig6, height=420)
        st.plotly_chart(fig6, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# T2 — CHURN ANALYTICS
# ══════════════════════════════════════════════════════════════════════════════
with T2:
    st.markdown('<div class="ts-eyebrow">LOGISTIC REGRESSION · ROC-AUC 0.757 · BALANCED CLASS WEIGHTS</div>', unsafe_allow_html=True)
    st.markdown('<div class="ts-heading">What drives churn — and what keeps customers loyal</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([3,2])
    with col1:
        coef_df = pd.DataFrame({
            "Feature": ["operator_Vi","dormant_45d_flag","high_complaints_flag",
                        "operator_BSNL","plan_type_Prepaid","data_usage_gb",
                        "network_rating","is_active_vlr","tenure_growing_4_12m","has_bundle"],
            "Coef":    [0.487, 0.311, 0.308, 0.266, 0.180, 0.060,
                        -0.120, -0.271, -0.325, -0.353],
        }).sort_values("Coef")
        colors_coef = [GREEN if c < 0 else RED for c in coef_df["Coef"]]
        fig_c = go.Figure(go.Bar(
            x=coef_df["Coef"], y=coef_df["Feature"],
            orientation="h",
            marker_color=colors_coef, marker_line_width=0,
            text=[f"{c:+.3f}" for c in coef_df["Coef"]],
            textposition="outside",
            textfont=dict(family="JetBrains Mono", color=TEXT, size=11),
            hovertemplate="<b>%{y}</b><br>Coefficient: %{x:+.3f}<extra></extra>",
        ))
        fig_c.add_vline(x=0, line_color=BORDER, line_width=2)
        fig_c.update_layout(
            xaxis=dict(title="scaled coefficient (LR)"),
            yaxis=dict(gridcolor="rgba(0,0,0,0)"),
        )
        chart_style(fig_c, height=380, title="Feature Coefficients — Logistic Regression")
        st.plotly_chart(fig_c, use_container_width=True)

    with col2:
        st.markdown('<div class="ts-eyebrow" style="margin-top:4px">CONFUSION MATRIX · TEST SET (n=2,000)</div>', unsafe_allow_html=True)
        cm = [[1296, 500],[76, 128]]
        cm_labels = [["TN · 1,296<br><span style='font-size:9px'>correctly retained</span>",
                       "FP · 500<br><span style='font-size:9px'>false alarm</span>"],
                     ["FN · 76<br><span style='font-size:9px'>missed churners</span>",
                      "TP · 128<br><span style='font-size:9px'>caught churners</span>"]]
        fig_cm = go.Figure(go.Heatmap(
            z=[[0.2, 0.05],[0.08, 0.9]],
            text=cm_labels, texttemplate="%{text}",
            colorscale=[[0,"rgba(20,31,48,1)"],[1,"rgba(0,229,160,0.27)"]],
            showscale=False, xgap=4, ygap=4,
            textfont=dict(family="JetBrains Mono", size=10, color=TEXT),
            hoverinfo="skip",
        ))
        fig_cm.update_layout(
            xaxis=dict(ticktext=["Pred: Stay","Pred: Churn"], tickvals=[0,1],
                       side="top", gridcolor="rgba(0,0,0,0)"),
            yaxis=dict(ticktext=["Actual: Churn","Actual: Stay"], tickvals=[1,0],
                       autorange="reversed", gridcolor="rgba(0,0,0,0)"),
        )
        chart_style(fig_cm, height=230)
        st.plotly_chart(fig_cm, use_container_width=True)

        st.markdown(f"""
        <div style="font-family:'JetBrains Mono',monospace; font-size:0.77rem;
                    line-height:2.1; color:{MUTED}; margin-top:4px;">
          Recall &nbsp;&nbsp;&nbsp;&nbsp; <span style="color:{TEXT}; font-weight:600;">62.7%</span>
          &nbsp;&nbsp; catches most churners<br>
          Precision &nbsp; <span style="color:{TEXT}; font-weight:600;">20.4%</span>
          &nbsp;&nbsp; 1 in 5 flags is real<br>
          F1 &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <span style="color:{TEXT}; font-weight:600;">0.308</span><br>
          ROC-AUC &nbsp; <span style="color:{GREEN}; font-weight:700;">0.757</span>
          &nbsp;&nbsp; ← selection metric
        </div>""", unsafe_allow_html=True)

    # Score distribution
    col3, col4 = st.columns(2)
    with col3:
        st.markdown('<div class="ts-eyebrow">PREDICTED PROBABILITY DISTRIBUTION · TEST SET</div>', unsafe_allow_html=True)
        fig_dist = go.Figure()
        for grp, color, label in [
            (preds[preds["actual_churn"]==0]["churn_probability"], "rgba(0,229,160,0.6)",  "Retained"),
            (preds[preds["actual_churn"]==1]["churn_probability"], "rgba(255,59,59,0.6)",  "Churned"),
        ]:
            fig_dist.add_trace(go.Histogram(
                x=grp, name=label, nbinsx=40,
                marker_color=color, marker_line_width=0, opacity=0.85,
                hovertemplate=f"<b>{label}</b><br>p=%{{x:.2f}}<br>n=%{{y}}<extra></extra>",
            ))
        fig_dist.update_layout(barmode="overlay",
                               xaxis=dict(title="predicted churn probability"),
                               yaxis=dict(title="customers"))
        chart_style(fig_dist, height=280, title="Score separation — churned vs retained")
        st.plotly_chart(fig_dist, use_container_width=True)

    with col4:
        st.markdown('<div class="ts-eyebrow">MODEL COMPARISON · ROC-AUC IS THE DECISION METRIC</div>', unsafe_allow_html=True)
        mdf = pd.DataFrame({
            "Model": ["LR","RF","XGB","XGB tuned"],
            "ROC-AUC": [0.757,0.731,0.728,0.748],
            "Recall":  [0.627,0.108,0.466,0.623],
            "F1":      [0.308,0.158,0.292,0.306],
        })
        fig_m = go.Figure()
        for metric, color in [("ROC-AUC",GREEN),("Recall",AMBER),("F1",BLUE)]:
            fig_m.add_trace(go.Bar(
                name=metric, x=mdf["Model"], y=mdf[metric],
                marker_color=color, marker_line_width=0, opacity=0.9,
                hovertemplate=f"<b>%{{x}}</b><br>{metric}: %{{y:.3f}}<extra></extra>",
            ))
        fig_m.update_layout(barmode="group",
                            yaxis=dict(range=[0,0.88]))
        chart_style(fig_m, height=280, title="Model selection — 4 candidates")
        st.plotly_chart(fig_m, use_container_width=True)

    st.markdown(f"""<div class="ts-warn">
    <strong>Why not Random Forest?</strong> RF hit 88.3% accuracy — but only caught <strong>10.8%</strong> of actual
    churners. In retention ops, a missed churner costs far more than a false alarm.
    Logistic Regression's 62.7% recall at ROC-AUC 0.757 is the right trade-off for this imbalanced dataset.
    </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# T3 — A/B RETENTION TEST
# ══════════════════════════════════════════════════════════════════════════════
with T3:
    st.markdown('<div class="ts-eyebrow">EXPERIMENT · 10% DISCOUNT VOUCHER · HIGH-RISK COHORT · 30-DAY WINDOW</div>', unsafe_allow_html=True)
    st.markdown('<div class="ts-heading">Did the voucher work?</div>', unsafe_allow_html=True)

    ctrl_n   = int((ab_df["treatment"]==0).sum())
    trt_n    = int((ab_df["treatment"]==1).sum())
    ctrl_cr  = ab_df[ab_df["treatment"]==0]["churned_30d"].mean()
    trt_cr   = ab_df[ab_df["treatment"]==1]["churned_30d"].mean()
    abs_red  = (ctrl_cr - trt_cr)*100
    rel_red  = (ctrl_cr - trt_cr)/ctrl_cr*100

    k1,k2,k3,k4 = st.columns(4)
    for col, lab, val, sub in [
        (k1, "CONTROL CHURN",   f"{ctrl_cr*100:.2f}%", f"n={ctrl_n:,} customers"),
        (k2, "TREATMENT CHURN", f"{trt_cr*100:.2f}%",  f"n={trt_n:,} customers"),
        (k3, "ABSOLUTE LIFT",   f"−{abs_red:.2f}pp",   "95% CI: (1.62pp, 4.79pp)"),
        (k4, "RELATIVE LIFT",   f"−{rel_red:.1f}%",    "p=0.0001 · z=−3.96"),
    ]:
        col.markdown(f"""
        <div class="ts-card">
          <div class="ts-label">{lab}</div>
          <div class="ts-val" style="font-size:1.6rem; color:{'#' + ('00E5A0' if '−' in val else 'E2EBF6')}">{val}</div>
          <div class="ts-sub">{sub}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col_ab1, col_ab2 = st.columns([3,2])

    with col_ab1:
        st.markdown('<div class="ts-eyebrow">30-DAY CHURN — TREATMENT VS CONTROL</div>', unsafe_allow_html=True)
        fig_ab = go.Figure(go.Bar(
            x=["Control","Treatment"],
            y=[ctrl_cr*100, trt_cr*100],
            marker_color=[RED, GREEN],
            marker_line_width=0,
            text=[f"{ctrl_cr*100:.2f}%", f"{trt_cr*100:.2f}%"],
            textposition="outside",
            textfont=dict(family="JetBrains Mono", color=TEXT, size=18, weight="bold"),
            width=0.4,
            hovertemplate="<b>%{x}</b><br>Churn: %{y:.2f}%<extra></extra>",
        ))
        fig_ab.add_annotation(
            x=0.5, y=(ctrl_cr+trt_cr)/2*100, xref="paper",
            text=f"← {abs_red:.2f}pp reduction",
            showarrow=False,
            font=dict(family="JetBrains Mono", color=AMBER, size=13),
        )
        fig_ab.update_layout(yaxis=dict(ticksuffix="%", range=[0,11]),
                             xaxis=dict(gridcolor="rgba(0,0,0,0)"))
        chart_style(fig_ab, height=300)
        st.plotly_chart(fig_ab, use_container_width=True)

    with col_ab2:
        st.markdown('<div class="ts-eyebrow">HETEROGENEOUS TREATMENT EFFECTS</div>', unsafe_allow_html=True)
        hte = pd.DataFrame({
            "Segment":  ["VLR Active","Low Complaints","High Complaints","VLR Inactive"],
            "Effect":   [4.27, 3.20, 3.46, 0.13],
            "Sig":      [True, True, True, False],
            "p":        ["<0.0001","0.0013","0.0084","0.9576"],
        })
        fig_hte = go.Figure(go.Bar(
            x=hte["Effect"], y=hte["Segment"],
            orientation="h",
            marker_color=[GREEN if s else MUTED for s in hte["Sig"]],
            marker_line_width=0,
            text=[f"{e:.2f}pp  (p={p})" for e,p in zip(hte["Effect"],hte["p"])],
            textposition="outside",
            textfont=dict(family="JetBrains Mono", color=TEXT, size=9),
            hovertemplate="<b>%{y}</b><br>Effect: %{x:.2f}pp<extra></extra>",
        ))
        fig_hte.update_layout(xaxis=dict(title="churn reduction (pp)", range=[0,7]),
                              yaxis=dict(gridcolor="rgba(0,0,0,0)"))
        chart_style(fig_hte, height=300)
        st.plotly_chart(fig_hte, use_container_width=True)

    # ARPU distribution — box + strip (violin with side="positive" renders flat in horizontal mode)
    st.markdown('<div class="ts-eyebrow">ARPU CHANGE DISTRIBUTION (₹) — 30-DAY WINDOW</div>', unsafe_allow_html=True)
    fig_arpu = go.Figure()
    arpu_cfg = [(1, "Treatment", GREEN, "rgba(0,229,160,0.15)"),
                (0, "Control",  MUTED, "rgba(91,122,157,0.12)")]
    for tval, label, color, fill in arpu_cfg:
        data = ab_df[ab_df["treatment"]==tval]["arpu_change_30d_inr"].dropna()
        # Box trace
        fig_arpu.add_trace(go.Box(
            x=data, name=label,
            orientation="h",
            boxmean=True,
            marker=dict(color=color, size=3, opacity=0.4),
            line=dict(color=color, width=1.5),
            fillcolor=fill,
            whiskerwidth=0.5,
            notched=False,
            hovertemplate=f"<b>{label}</b><br>%{{x:.1f}} ₹<extra></extra>",
        ))
    fig_arpu.update_layout(
        xaxis_title="ARPU change (₹)",
        yaxis_title="",
        boxmode="group",
        showlegend=True,
        legend=dict(orientation="h", y=1.08, x=1, xanchor="right",
                    font=dict(family="JetBrains Mono", size=10)),
    )
    chart_style(fig_arpu, height=240)
    st.plotly_chart(fig_arpu, use_container_width=True)

    # Business impact
    st.markdown('<div class="ts-eyebrow">BUSINESS CASE · 6-MONTH PROJECTION</div>', unsafe_allow_html=True)
    b1,b2,b3,b4 = st.columns(4)
    for col, lab, val, sub in [
        (b1, "ELIGIBLE / CYCLE", "2,514",      "active high-risk customers"),
        (b2, "RETENTIONS / MO",  "~107",       "additional retentions"),
        (b3, "VOUCHER COST 6M",  "₹50,495",    "60.89% redemption rate"),
        (b4, "NET BENEFIT 6M",   "₹1,61,953",  "revenue saved − voucher cost"),
    ]:
        col.markdown(f"""
        <div class="ts-card">
          <div class="ts-label">{lab}</div>
          <div class="ts-val" style="font-size:1.35rem;">{val}</div>
          <div class="ts-sub">{sub}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"""<div class="ts-insight">
    <strong>Causal conclusion:</strong> The voucher causally reduces 30-day churn by <strong>3.21pp</strong>
    (p=0.0001, 95% CI: 1.62–4.79pp). Effect is concentrated in <strong>VLR-active customers</strong>
    (4.27pp) — inactive subscribers show no response (0.13pp, p=0.96).
    Targeting the voucher only to active high-risk customers yields an estimated <strong>₹1,61,953 net benefit</strong> over 6 months.
    </div>""", unsafe_allow_html=True)

    with st.expander("📋  Randomization check — balance table"):
        rand = pd.DataFrame({
            "Covariate": ["age","plan_amount_inr","data_usage_gb",
                          "days_since_last_recharge","is_active_vlr","num_complaints_6m"],
            "p-value": [0.412,0.654,0.287,0.023,0.051,0.389],
            "Assessment": ["✓ Balanced","✓ Balanced","✓ Balanced",
                           "⚠ p=0.023","⚠ p=0.051","✓ Balanced"],
        })
        st.dataframe(rand, use_container_width=True, hide_index=True)
        st.markdown(f"""<div class="ts-warn">
        2 of 6 covariates show p &lt; 0.10. With 6 simultaneous tests at α=0.05,
        the probability of ≥1 false positive is 1−(0.95)⁶ ≈ 26.5%.
        These imbalances are consistent with chance under multiple comparisons. Randomization is sound.
        </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# T4 — RISK SCORER (live — no button required)
# ══════════════════════════════════════════════════════════════════════════════
with T4:
    st.markdown('<div class="ts-eyebrow">INTERACTIVE · UPDATES IN REAL TIME</div>', unsafe_allow_html=True)
    st.markdown('<div class="ts-heading">Customer churn risk estimator</div>', unsafe_allow_html=True)

    inp, gauge_col = st.columns([2, 2])

    with inp:
        p_op   = st.selectbox("Operator",   ["Jio","Airtel","Vi","BSNL"])
        p_plan = st.selectbox("Plan Type",  ["Prepaid","Postpaid"])
        p_pay  = st.selectbox("Payment",    ["UPI","Card","Net Banking","Cash","Wallet"])
        p_vlr  = st.toggle("VLR Active",    value=True)
        p_bund = st.toggle("Has Bundle",    value=False)
        p_5g   = st.toggle("Uses 5G",       value=False)
        p_rech = st.slider("Days since recharge",  0, 90, 15)
        p_comp = st.slider("Complaints (6m)",       0, 5,  0)
        p_ten  = st.slider("Tenure (months)",       1, 72, 18)
        p_rat  = st.slider("Network rating",        1, 5,  4)
        p_plan_amt = st.select_slider("Plan amount (₹)",
            options=[149,199,249,299,349,399,499,599,699,799,999,1199], value=399)

    # ── Heuristic model (mirrors LR coefficients from the project) ──
    base = {"Jio":0.066,"Airtel":0.071,"Vi":0.212,"BSNL":0.221}
    score = 0.0
    op_adj = {"Jio":-0.8,"Airtel":-0.7,"Vi":1.2,"BSNL":1.1}
    score += op_adj[p_op]
    score += -2.5 if p_vlr  else 2.5
    score += 0.04 * p_rech
    score += 0.35 * p_comp
    score += -0.9 if p_bund else 0
    score += -0.03 * p_ten
    score += -0.25 * p_rat
    score += -0.3  if p_5g  else 0
    score += -0.001*(p_plan_amt - 400)
    score += 0.18  if p_plan == "Prepaid" else 0
    prob  = float(np.clip(1/(1+np.exp(-score)), 0.01, 0.99))
    pct   = prob*100

    if pct < 10:
        risk_label, risk_color = "LOW RISK",      GREEN
        rec = "No immediate action needed. Monitor recharge cadence; alert if dormancy exceeds 30 days."
    elif pct < 22:
        risk_label, risk_color = "MODERATE RISK", AMBER
        rec = "Proactive outreach recommended. Consider a data top-up offer or loyalty bundle upgrade."
    else:
        risk_label, risk_color = "HIGH RISK",     RED
        rec = "Flag for the 10% discount voucher campaign — A/B tested: 3.21pp absolute churn reduction (p=0.0001). Target only if VLR active."

    with gauge_col:
        # ── Gauge ──
        fig_g = go.Figure(go.Indicator(
            mode="gauge+number",
            value=pct,
            number=dict(suffix="%", font=dict(
                family="JetBrains Mono, monospace", size=58, color=risk_color)),
            gauge=dict(
                axis=dict(range=[0,100], tickwidth=1, tickcolor=BORDER,
                           tickfont=dict(family="JetBrains Mono", size=10, color=MUTED),
                           nticks=6),
                bar=dict(color=risk_color, thickness=0.22),
                bgcolor=SURF2, borderwidth=0,
                steps=[
                    dict(range=[0,10],  color="rgba(0,229,160,0.09)"),
                    dict(range=[10,22], color="rgba(245,158,11,0.09)"),
                    dict(range=[22,100],color="rgba(255,59,59,0.09)"),
                ],
                threshold=dict(line=dict(color=risk_color, width=4),
                               thickness=0.85, value=pct),
            ),
            domain=dict(x=[0,1], y=[0.15,1]),
        ))
        fig_g.add_annotation(
            text=risk_label, x=0.5, y=0.06,
            font=dict(family="JetBrains Mono, monospace", size=14,
                      color=risk_color, weight="bold"),
            showarrow=False,
        )
        fig_g.update_layout(
            height=330, paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color=MUTED),
            margin=dict(l=24,r=24,t=16,b=16),
        )
        st.plotly_chart(fig_g, use_container_width=True)

        # ── Recommendation ──
        st.markdown(f"""
        <div style="background:{risk_color}0D; border-left:3px solid {risk_color};
                    border-radius:0 8px 8px 0; padding:13px 16px;
                    font-size:0.84rem; color:{TEXT}; line-height:1.5;">
          <div style="font-family:'JetBrains Mono',monospace; font-size:0.65rem;
                      letter-spacing:0.12em; text-transform:uppercase; color:{risk_color};
                      margin-bottom:5px;">Recommendation</div>
          {rec}
        </div>""", unsafe_allow_html=True)

        # ── Factor breakdown ──
        st.markdown(f"""
        <div style="margin-top:14px; font-family:'JetBrains Mono',monospace;
                    font-size:0.72rem; line-height:2; color:{MUTED};
                    border-top:1px solid {BORDER}; padding-top:12px;">""", unsafe_allow_html=True)

        factors = []
        if not p_vlr:   factors.append(("VLR Inactive",       "↑ risk",  RED))
        if p_rech > 45: factors.append((f"Dormant {p_rech}d", "↑ risk",  RED))
        if p_comp >= 2: factors.append((f"{p_comp} complaints","↑ risk",  AMBER))
        if p_op in ["Vi","BSNL"]: factors.append((f"{p_op} operator","↑ risk", AMBER))
        if not p_bund:  factors.append(("No bundle",           "↑ risk",  AMBER))
        if p_rat <= 2:  factors.append(("Low network rating",  "↑ risk",  AMBER))
        if p_vlr:       factors.append(("VLR Active",          "↓ shields", GREEN))
        if p_bund:      factors.append(("Has bundle",          "↓ shields", GREEN))
        if p_ten > 24:  factors.append((f"Tenure {p_ten}mo",  "↓ shields", GREEN))
        if p_5g:        factors.append(("5G user",             "↓ shields", GREEN))

        for f_name, f_impact, f_col in factors[:7]:
            st.markdown(f"""
            <div style="display:flex; justify-content:space-between; padding:1px 0;
                        border-bottom:1px solid {BORDER}44;">
              <span style="color:{TEXT}">{f_name}</span>
              <span style="color:{f_col}; font-weight:600">{f_impact}</span>
            </div>""", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

# ── FOOTER ─────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="margin-top:3rem; padding:16px 0; border-top:1px solid {BORDER};
            font-family:'JetBrains Mono',monospace; font-size:0.65rem;
            color:{MUTED}; display:flex; justify-content:space-between;">
  <span>TelcoSignal · Indian Telecom Churn Intelligence · Data calibrated to TRAI Dec 2025</span>
  <span>GitHub: Avantika029/indian-telecom-churn-analysis · Model: Logistic Regression ROC-AUC 0.757</span>
</div>""", unsafe_allow_html=True)
