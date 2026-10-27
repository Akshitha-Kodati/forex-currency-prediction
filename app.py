import os

import joblib
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

MODEL_DIR = "models"

st.set_page_config(page_title="Forex Forecast", page_icon="💱", layout="wide")
st.title("💱 Forex Currency Forecast")


@st.cache_resource
def load_bundle(filename: str) -> dict:
    return joblib.load(os.path.join(MODEL_DIR, filename))


def list_models() -> dict:
    """Map the readable currency name -> model filename."""
    if not os.path.isdir(MODEL_DIR):
        return {}
    out = {}
    for f in sorted(os.listdir(MODEL_DIR)):
        if f.endswith("_model.pkl"):
            out[load_bundle(f).get("currency", f.replace("_model.pkl", ""))] = f
    return out


def make_forecast(currency: str, days: int, models: dict):
    """Load the saved model for `currency` and forecast `days` business days."""
    bundle = load_bundle(models[currency])
    dates = pd.bdate_range(pd.Timestamp(bundle["last_date"]) + pd.Timedelta(days=1), periods=days)
    kind = bundle["type"]
    if kind == "ARIMA":
        yhat = np.asarray(bundle["model"].forecast(days))
    elif kind == "Prophet":
        yhat = bundle["model"].predict(pd.DataFrame({"ds": dates}))["yhat"].values
    else:  # Naive
        yhat = np.repeat(bundle["last_value"], days)
    fc = pd.DataFrame({"Date": dates, "Forecast": np.round(yhat, 4)})
    return kind, bundle, fc


models = list_models()
if not models:
    st.error("No saved models found in the 'models/' folder. Run analysis.ipynb first.")
    st.stop()

st.sidebar.header("Settings")
currency = st.sidebar.selectbox("Currency", list(models))
days = st.sidebar.number_input("Forecast horizon (business days)", 1, 365, 30)

if st.sidebar.button("Generate forecast", type="primary"):
    kind, bundle, fc = make_forecast(currency, int(days), models)
    st.caption(
        f"Model used for **{currency}**: **{kind}** · trained through "
        f"{pd.Timestamp(bundle['last_date']).date()} · "
        f"test RMSE: {bundle.get('rmse', float('nan')):.4f}"
    )
    left, right = st.columns([1, 2])
    left.dataframe(fc, width="stretch", hide_index=True)
    left.download_button("Download CSV", fc.to_csv(index=False), f"{currency}_forecast.csv")

    fig = go.Figure()
    hist = bundle.get("history")
    if hist is not None:
        fig.add_trace(go.Scatter(x=hist.index, y=hist.values, name="History (last 180 days)"))
    fig.add_trace(go.Scatter(x=fc["Date"], y=fc["Forecast"], name="Forecast", mode="lines+markers"))
    fig.update_layout(title=f"{currency}: next {int(days)} business days", xaxis_title="Date", yaxis_title="Rate")
    right.plotly_chart(fig, width="stretch")
    st.info("Exchange rates are very hard to predict. Treat this as a learning project, not financial advice.")
else:
    st.write("Choose a currency and horizon in the sidebar, then click **Generate forecast**.")
