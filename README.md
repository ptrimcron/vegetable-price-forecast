# Vegetable Price Forecasting Dashboard

Streamlit research dashboard for five Malaysian vegetables with ARIMA, LSTM, N-BEATSX and hybrid forecasting, and saved weather SHAP explanations.

## Running locally

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## Publishing to GitHub + Streamlit Community Cloud

1. Upload the CONTENTS of this directory to a GitHub repository, not the `.zip` file.
2. If available, add the three CSV files named in `deployment/ADD_CSV_FILES_HERE.txt`.
3. Visit https://share.streamlit.io and choose **Create app**, then **Yup, I have an app**.
4. Select your repository, branch `main`, and entrypoint `app.py`. Click **Deploy**.

## Research data accuracy

This is a saved historical prototype (not a live price service). Forecasts and accuracy metrics fall back to built-in saved summary results when exported CSVs are unavailable. `weekly_vegetable_prices.csv` is needed for the historical price chart. Saved SHAP attribution explains the **weather-aware N-BEATSX M3b**, not the combined hybrid M4 forecast; SHAP importance is not causal.

## Layout

Desktop CSS supports a hover-to-expand sidebar and reflows main content. On smaller screens the sidebar uses Streamlit's standard behaviour. Layout is best validated in your target browser.

## Responsive hover sidebar (November 2026 update)

The green leaf rail opens when hovered. It stays expanded while the selector is focused or its vegetable list is open. The main content and five metric cards adjust to the remaining viewport width. On mobile, Streamlit's normal sidebar controls apply.

To publish the correction, replace your GitHub repository's root `app.py` with this one and commit changes. After Streamlit redeploys, refresh the webpage (Ctrl+Shift+R). If the live page still shows the old dashboard, confirm the deployed entrypoint is `app.py` in the repository root.

## Mustard Greens label update

The interface shows **Mustard Greens** everywhere instead of **Sawi**. Original PriceCatcher CSV exports using `Sawi` (or `sawi hijau`) are normalized in memory, so no CSV or trained model values need changing. The sidebar, charts, forecasting cards and SHAP explanation all use the English label.
