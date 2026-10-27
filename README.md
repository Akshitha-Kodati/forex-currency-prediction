# 💱 Forex Currency Prediction

End-to-end ML project: data cleaning → EDA → model comparison (Naive, ARIMA, Prophet) → best model saved per currency → Streamlit app → Docker.

## Structure
| Path | Purpose |
|---|---|
| `analysis.ipynb` | EDA, modeling, evaluation (MAE/RMSE/MAPE), saves models |
| `app.py` | Streamlit app (pick currency + horizon, get table + chart) |
| `data/` | Excel dataset (`forex_sample.xlsx` is **synthetic** demo data) |
| `models/` | One `.pkl` per currency (created by the notebook) |
| `Dockerfile`, `requirements.txt` | Packaging |

## No dataset? Download real data
```bash
python fetch_data.py
```
This saves `data/forex_data.xlsx` (USD base, ECB rates via the free Frankfurter API). The notebook picks it up automatically.

## Use your own data
1. Put your `.xlsx` in `data/` (first column = dates, other columns = one currency each).
2. Open `analysis.ipynb`, set `DATA_FILE`, run all cells.
3. Models are regenerated in `models/`.

## Run locally
```bash
pip install -r requirements.txt jupyter matplotlib seaborn
streamlit run app.py
```

## Run with Docker
```bash
docker build -t forex-app .
docker run -p 8501:8501 forex-app
```
Open http://localhost:8501

> Exchange rates are close to a random walk; the Naive baseline often wins. Not financial advice.
