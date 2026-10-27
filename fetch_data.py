"""Download real daily exchange rates (base USD) and save to data/forex_data.xlsx.

Source: Frankfurter API (European Central Bank reference rates). Free, no key needed.
Usage:  python fetch_data.py
Edit START, END or CURRENCIES below if you want something different.
"""
import os
import sys
from datetime import date, timedelta

import pandas as pd
import requests

START = date(2015, 1, 1)
END = date.today()
CURRENCIES = ["EUR", "JPY", "GBP", "INR", "CAD", "AUD", "CHF", "CNY"]
URL = "https://api.frankfurter.dev/v1/{a}..{b}"
CHUNK_DAYS = 80  # small chunks so the API always returns daily (not weekly) data


def fetch_chunk(a: date, b: date) -> dict:
    r = requests.get(URL.format(a=a, b=b), params={"base": "USD", "symbols": ",".join(CURRENCIES)}, timeout=30)
    r.raise_for_status()
    return r.json().get("rates", {})


def main():
    rates, cur = {}, START
    while cur <= END:
        nxt = min(cur + timedelta(days=CHUNK_DAYS), END)
        print(f"Downloading {cur} -> {nxt}", flush=True)
        rates.update(fetch_chunk(cur, nxt))
        cur = nxt + timedelta(days=1)
    if not rates:
        sys.exit("No data returned. Check your internet connection and try again.")
    df = pd.DataFrame.from_dict(rates, orient="index")
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()
    df.index.name = "Date"
    df = df[~df.index.duplicated()]
    os.makedirs("data", exist_ok=True)
    out = "data/forex_data.xlsx"
    df.reset_index().to_excel(out, index=False)
    print(f"\nSaved {len(df)} rows x {df.shape[1]} currencies to {out}")
    print(df.tail())


if __name__ == "__main__":
    main()
