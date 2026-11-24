from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parent
DATA = ROOT / 'deployment'
VEGETABLES = ['Mustard Greens','Tomato','Chilli','Cabbage','Cucumber']
MODELS = ['M1 ARIMA','M2 LSTM','M3a N-BEATSX Price Only','M3b N-BEATSX + Weather','M4 Hybrid']
SHORT = {'ARIMA':'M1 ARIMA','LSTM':'M2 LSTM','N-BEATSX Price-Only':'M3a N-BEATSX Price Only','N-BEATSX + Weather':'M3b N-BEATSX + Weather','Hybrid ARIMA + N-BEATSX + Weather':'M4 Hybrid'}

st.set_page_config(page_title='Weather Aware Forecast Vegetable Price | FYP', page_icon='🥬', layout='wide', initial_sidebar_state='expanded')
st.markdown('''<style>
.block-container{padding-top:1.6rem;width:100%;max-width:none!important}
.hero{isolation:isolate;position:relative;overflow:hidden;background:linear-gradient(115deg,#103b35,#276d5b,#194c58,#103b35);background-size:250% 250%;animation:heroGradient 14s ease-in-out infinite;color:white;padding:38px 36px;border-radius:23px;margin-bottom:22px;box-shadow:0 16px 35px rgba(21,71,60,.14)}
.hero h1{position:relative;z-index:2;margin:0;color:white;font-size:clamp(1.65rem,3vw,2.6rem);letter-spacing:-.035em;animation:riseIn .85s both}.hero p{position:relative;z-index:2;margin:11px 0 0;color:#dcece5;animation:riseIn .85s .15s both}.hero::after{content:'';position:absolute;right:-70px;top:-110px;width:320px;height:320px;border:1px solid rgba(255,255,255,.16);border-radius:50%;box-shadow:0 0 0 55px rgba(255,255,255,.035),0 0 0 110px rgba(255,255,255,.025);pointer-events:none}
.note{border-left:4px solid #d0a85d;padding:12px 15px;background:#fff9ea;color:#54451f;border-radius:7px}
/* Forecast price and error metrics retain their own mathematical units. */
[data-testid="stMetric"]{border:1px solid rgba(38,59,65,.10);border-radius:17px;padding:19px 21px;min-height:145px;box-shadow:0 3px 12px rgba(36,55,64,.045)}
[data-testid="stMetricValue"]{font-weight:800!important;letter-spacing:-.7px;color:#263746}
[data-testid="stMetricLabel"]{font-weight:650;color:#394958;white-space:normal!important;overflow:visible!important;min-height:52px;align-items:flex-start!important}
[data-testid="stMetricLabel"] p{white-space:normal!important;overflow:visible!important;text-overflow:clip!important;word-break:normal!important;line-height:1.35!important;display:block!important}
[data-testid="stMetricLabel"] [data-testid="stTooltipIcon"]{flex-shrink:0!important}
[data-testid="stMetricValue"]{padding-top:12px!important}
[data-testid="stMetric"]{min-height:190px!important;transition:transform .28s ease,box-shadow .28s ease,border-color .28s ease;animation:riseIn .65s both}[data-testid="stMetric"]:hover{transform:translateY(-6px);box-shadow:0 15px 32px rgba(40,62,65,.12);border-color:rgba(40,90,80,.22)}
[data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(1) [data-testid="stMetric"]{background:#e6f4ed}
[data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(2) [data-testid="stMetric"]{background:#eaf1ff}
[data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(3) [data-testid="stMetric"]{background:#fff0e4}
[data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(4) [data-testid="stMetric"]{background:#f3eafd}
[data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(5) [data-testid="stMetric"]{background:#e9f6f7}
/* Calm, Apple-inspired motion; works without JavaScript or extra packages */
@keyframes heroGradient{0%,100%{background-position:0% 50%}50%{background-position:100% 50%}}
@keyframes riseIn{from{opacity:0;transform:translateY(18px)}to{opacity:1;transform:translateY(0)}}
@keyframes softAppear{from{opacity:.25;transform:translateY(22px)}to{opacity:1;transform:translateY(0)}}
[data-testid="stPlotlyChart"]{border:1px solid rgba(50,90,78,.09);border-radius:18px;padding:12px;background:var(--secondary-background-color,transparent);transition:box-shadow .3s ease,transform .3s ease}
[data-testid="stPlotlyChart"]:hover{box-shadow:0 12px 30px rgba(31,72,67,.09);transform:translateY(-2px)}
[data-testid="stDataFrame"]{border-radius:15px;overflow:hidden;transition:box-shadow .25s ease}
[data-testid="stDataFrame"]:hover{box-shadow:0 10px 25px rgba(34,72,65,.08)}
[data-testid="stSidebar"] [data-baseweb="select"]{transition:box-shadow .25s ease}
[data-testid="stSidebar"] [data-baseweb="select"]:focus-within{box-shadow:0 0 0 3px rgba(79,160,132,.15);border-radius:12px}
/* Floating glass bubbles: actual animated HTML elements, not browser-dependent scroll timelines */
.hero .bubble{position:absolute;z-index:1;bottom:-90px;display:block;border-radius:50%;pointer-events:none;
 background:radial-gradient(circle at 28% 24%,rgba(255,255,255,.56),rgba(181,244,224,.18) 44%,rgba(255,255,255,.06) 75%);
 border:1px solid rgba(255,255,255,.34);box-shadow:inset -9px -12px 20px rgba(13,85,73,.14),0 6px 26px rgba(8,31,38,.12);
 animation:bubbleFloat var(--speed,12s) linear infinite;animation-delay:var(--delay,0s);}
@keyframes bubbleFloat{0%{transform:translate3d(0,0,0) scale(.85);opacity:0}12%{opacity:.72}80%{opacity:.60}100%{transform:translate3d(var(--drift,30px),-410px,0) scale(1.18);opacity:0}}
.hero .bubble:nth-child(1){width:55px;height:55px;left:6%;--speed:12s;--delay:-4s;--drift:45px}
.hero .bubble:nth-child(2){width:24px;height:24px;left:22%;--speed:9s;--delay:-7s;--drift:-35px}
.hero .bubble:nth-child(3){width:85px;height:85px;left:61%;--speed:15s;--delay:-10s;--drift:65px}
.hero .bubble:nth-child(4){width:38px;height:38px;left:78%;--speed:11s;--delay:-2s;--drift:-48px}
.hero .bubble:nth-child(5){width:67px;height:67px;left:90%;--speed:13s;--delay:-9s;--drift:-32px}
.hero .bubble:nth-child(6){width:19px;height:19px;left:45%;--speed:8s;--delay:-5s;--drift:26px}
/* Entrance animations on normal render: works without experimental browser features */
[data-testid="stPlotlyChart"]{animation:riseIn .7s ease-out both}
[data-testid="stDataFrame"]{animation:riseIn .8s ease-out both}
.weather-explain{animation:riseIn .75s ease-out both}
[data-testid="stMetric"]{animation:riseIn .6s ease-out both}
[data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(2) [data-testid="stMetric"]{animation-delay:.09s}
[data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(3) [data-testid="stMetric"]{animation-delay:.18s}
[data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(4) [data-testid="stMetric"]{animation-delay:.27s}
/* Distinct, tasteful hover and focus cues */
[data-testid="stMetric"]{cursor:help;position:relative;overflow:hidden}
[data-testid="stMetric"]::after{content:"";position:absolute;top:-110%;left:-70%;width:40%;height:300%;
 background:linear-gradient(90deg,transparent,rgba(255,255,255,.34),transparent);transform:rotate(22deg);
 transition:left .65s ease;pointer-events:none}
[data-testid="stMetric"]:hover::after{left:140%}
[data-testid="stMetric"]:hover [data-testid="stMetricValue"]{transform:translateY(-2px)}
[data-testid="stMetricValue"]{transition:transform .25s ease}
[data-testid="stPlotlyChart"]{overflow:hidden}
[data-testid="stPlotlyChart"]:hover{border-color:rgba(55,151,120,.38);box-shadow:0 16px 34px rgba(31,72,67,.12)}
[data-testid="stDataFrame"]:hover{outline:1px solid rgba(70,151,125,.25)}
[data-testid="stSidebar"] [data-baseweb="select"]:hover{filter:brightness(.98)}
@media (max-width:750px){.hero .bubble:nth-child(n+4){display:none}.hero{padding:28px 22px}}
@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important;transform:none!important}}



/* Weather explanation stays next to the selected vegetable's SHAP chart. */
.weather-explain{background:#f1f8f5;border:1px solid #d2e8df;border-radius:16px;padding:19px 22px;margin:18px 0;color:#263e37;transition:transform .3s ease,box-shadow .3s ease}
.weather-explain h4{margin:0 0 8px 0;color:#204c40}
.weather-explain p{margin:5px 0;line-height:1.55}
.weather-explain:hover{transform:translateY(-2px);box-shadow:0 12px 26px rgba(37,91,68,.10)}
/* Metric grid automatically changes 5 -> fewer columns if space is limited. */
[data-testid="stMain"] [data-testid="stHorizontalBlock"]:has(> [data-testid="stColumn"] [data-testid="stMetric"]) {
  display:grid!important;
  grid-template-columns:repeat(auto-fit,minmax(min(100%,190px),1fr))!important;
  align-items:stretch!important;
  gap:14px!important;
  width:100%!important;
}
[data-testid="stMain"] [data-testid="stHorizontalBlock"]:has(> [data-testid="stColumn"] [data-testid="stMetric"]) > [data-testid="stColumn"]{
  display:block!important;
  width:auto!important;
  min-width:0!important;
  max-width:none!important;
  flex:none!important;
}
[data-testid="stMetric"]{box-sizing:border-box!important;width:100%!important;min-width:0!important;min-height:155px!important;padding:17px 16px!important;overflow:visible!important}
[data-testid="stMetricValue"], [data-testid="stMetricValue"] > div{
  overflow:visible!important;
  text-overflow:clip!important;
  white-space:nowrap!important;
  max-width:100%!important;
  /* Larger result numbers; card grid still wraps on narrower screens. */
  font-size:clamp(1.85rem,2.35vw,2.7rem)!important;
  line-height:1.2!important;
  letter-spacing:-.035em!important;
}
[data-testid="stMetricLabel"]{min-height:45px!important}
[data-testid="stSidebarUserContent"]{padding-top:1.2rem}

/* Desktop hover/expand sidebar with reliable full-width main area.
   Do not let native Streamlit's flex sizing keep a 1,150px content frame. */
@media (min-width:769px){
  :root{--veg-rail:60px;--veg-panel:330px}
  [data-testid="stAppViewContainer"]{
    display:block!important;
    position:relative!important;
    width:100%!important;
    min-width:0!important;
    max-width:none!important;
    overflow-x:clip!important;
  }
  section[data-testid="stSidebar"]{
    position:fixed!important;
    left:0!important;top:0!important;bottom:0!important;
    width:var(--veg-rail)!important;
    min-width:var(--veg-rail)!important;
    max-width:var(--veg-rail)!important;
    transform:none!important;
    overflow:hidden!important;
    z-index:9999!important;
    box-shadow:none!important;
    border:0!important;
    background:transparent!important;
    transition:width .25s ease,min-width .25s ease,max-width .25s ease,box-shadow .25s ease!important;
  }
  section[data-testid="stSidebar"] > div,
  section[data-testid="stSidebar"] [data-testid="stSidebarContent"]{
    width:var(--veg-panel)!important;
    min-width:var(--veg-panel)!important;
    max-width:var(--veg-panel)!important;
  }
  section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"]{
    opacity:0!important;
    visibility:hidden!important;
    transition:opacity .12s ease,visibility .12s ease!important;
  }
  /* Keep it open during keyboard focus and while a portaled dropdown is displayed. */
  section[data-testid="stSidebar"]:is(:hover,:focus-within),
  body:has([role="listbox"]) section[data-testid="stSidebar"]{
    width:var(--veg-panel)!important;
    min-width:var(--veg-panel)!important;
    max-width:var(--veg-panel)!important;
    background:var(--secondary-background-color,#f0f2f6)!important;
    box-shadow:5px 0 24px rgba(25,64,52,.15)!important;
  }
  section[data-testid="stSidebar"]:is(:hover,:focus-within) [data-testid="stSidebarUserContent"],
  body:has([role="listbox"]) section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"]{
    opacity:1!important;
    visibility:visible!important;
  }
  /* Use the leaf-shaped hover handle; do not show Streamlit's native collapse button. */
  section[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"]{display:none!important}
  section[data-testid="stSidebar"]::before{
    content:"🥬";
    position:absolute;
    top:86px;left:0;
    width:59px;height:75px;
    box-sizing:border-box;
    display:flex;align-items:center;justify-content:center;
    font-size:28px;
    border-radius:0 46px 46px 0;
    background:#e7f3ed;
    border:1px solid #d3e7dc;border-left:0;
    box-shadow:3px 4px 14px rgba(35,79,62,.15);
    pointer-events:none;
    z-index:2;
  }
  section[data-testid="stSidebar"]:is(:hover,:focus-within)::before,
  body:has([role="listbox"]) section[data-testid="stSidebar"]::before{display:none}

  /* The main panel takes the entire remaining viewport width.
     Set flex:none to prevent Streamlit flex-basis from overriding width. */
  [data-testid="stAppViewContainer"] [data-testid="stMain"]{
    display:block!important;
    position:relative!important;
    box-sizing:border-box!important;
    left:var(--veg-rail)!important;
    margin:0!important;
    padding:0!important;
    width:calc(100% - var(--veg-rail))!important;
    min-width:0!important;
    max-width:none!important;
    flex:none!important;
    overflow-x:hidden!important;
    transition:left .25s ease,width .25s ease!important;
  }
  [data-testid="stAppViewContainer"]:has(section[data-testid="stSidebar"]:is(:hover,:focus-within)) [data-testid="stMain"],
  body:has([role="listbox"]) [data-testid="stAppViewContainer"] [data-testid="stMain"]{
    left:var(--veg-panel)!important;
    width:calc(100% - var(--veg-panel))!important;
  }
  /* This targets both older and newer Streamlit block-container class names. */
  [data-testid="stMainBlockContainer"],
  [data-testid="stMain"] .block-container{
    box-sizing:border-box!important;
    width:100%!important;
    max-width:none!important;
    min-width:0!important;
    margin:0!important;
    padding-left:clamp(16px,2vw,30px)!important;
    padding-right:clamp(16px,2vw,30px)!important;
  }
  [data-testid="stMain"] [data-testid="stVerticalBlock"],
  [data-testid="stMain"] [data-testid="stElementContainer"],
  [data-testid="stMain"] [data-testid="stPlotlyChart"]{
    box-sizing:border-box!important;
    min-width:0!important;
    max-width:100%!important;
  }
}
@media (min-width:769px) and (max-width:1100px){
  :root{--veg-panel:285px}
}
@media (max-width:768px){
  [data-testid="stMain"] .block-container,
  [data-testid="stMainBlockContainer"]{
    box-sizing:border-box!important;
    width:100%!important;
    max-width:none!important;
    padding-left:1rem!important;
    padding-right:1rem!important;
  }
}
</style>''', unsafe_allow_html=True)

# Let Plotly resize after the main panel changes width on sidebar hover.
# This does not depend on app data and safely does nothing if iframe access is blocked.
import streamlit.components.v1 as components
components.html("""
<script>
(function(){
 try {
  const win=window.parent, doc=win.document;
  const main=doc.querySelector('[data-testid="stMain"]');
  if(!main || !win.ResizeObserver) return;
  if(win.__vegetableMainWidthObserver) win.__vegetableMainWidthObserver.disconnect();
  let frame;
  const obs=new win.ResizeObserver(()=>{
   win.cancelAnimationFrame(frame);
   frame=win.requestAnimationFrame(()=>{
    win.dispatchEvent(new win.Event('resize'));
    doc.querySelectorAll('.js-plotly-plot').forEach(p=>{
     try { if(win.Plotly && p._fullLayout) win.Plotly.Plots.resize(p); } catch(_) {}
    });
   });
  });
  obs.observe(main);
  win.__vegetableMainWidthObserver=obs;
 } catch(_) { /* Streamlit controls iframe security. */ }
})();
</script>
""",height=0,scrolling=False)

st.markdown('''<div class="hero" aria-label="Weather Aware Forecast Vegetable Price">
<span class="bubble"></span><span class="bubble"></span><span class="bubble"></span>
<span class="bubble"></span><span class="bubble"></span><span class="bubble"></span>
<h1>🥬 Weather Aware Forecast Vegetable Price</h1>
<p>Explore weekly vegetable price predictions and the role of weather</p>
</div>''', unsafe_allow_html=True)

@st.cache_data
def read_csv(filename):
    """Read exports from GitHub repository root or deployment/ folder."""
    for path in (ROOT / filename, DATA / filename):
        if path.is_file():
            return pd.read_csv(path)
    return None

@st.cache_data
def fallback_forecasts():
    vals = {
        'Mustard Greens':[5.983649,5.758640,6.242894,6.145991,6.505487],
        'Tomato':[9.230993,6.923649,9.038507,8.869247,10.178044],
        'Chilli':[16.000000,16.088530,15.699203,15.651451,16.832752],
        'Cabbage':[5.000000,4.641447,5.008833,4.945309,5.354099],
        'Cucumber':[3.912239,3.914825,4.044780,4.095160,5.145835],
    }
    return pd.DataFrame([{'vegetable':v,'model':m,'forecast_week':'2026-07-27','forecast_price':p} for v,arr in vals.items() for m,p in zip(MODELS,arr)])

@st.cache_data
def fallback_metrics():
    """Saved final tuned test metrics from the completed research notebook.

    The RMSE and MAPE values here are from its final 25-row evaluation.
    MSE is derived as RMSE squared, using the displayed 4-decimal RMSE.
    An exported deployment CSV takes precedence over this static snapshot.
    """
    # Columns per vegetable: ARIMA, LSTM, price-only N-BEATSX,
    # N-BEATSX + Weather, and tuned Hybrid ARIMA–N-BEATSX.
    results = {
        'Mustard Greens': [
            (.3021, .4338, 5.4487), (.3024, .3985, 5.2094),
            (.2542, .3924, 4.4953), (.4557, .5599, 8.3198),
            (.4309, .5109, 7.7279)],
        'Tomato': [
            (.7092, 1.0025, 11.3176), (.8234, 1.0982, 13.1728),
            (.7294, 1.0770, 10.8190), (.7878, 1.1669, 12.9227),
            (.7977, 1.0435, 13.3910)],
        'Chilli': [
            (.4300, .8063, 2.9033), (.8359, 1.0212, 5.4929),
            (.4337, .8021, 2.9240), (.6863, .9428, 4.5325),
            (.8626, 1.0587, 5.5862)],
        'Cabbage': [
            (.2264, .3821, 4.5247), (.2787, .3941, 5.5331),
            (.2307, .3802, 4.5994), (.2546, .3500, 5.2313),
            (.3422, .4538, 6.9593)],
        'Cucumber': [
            (.6183, .8863, 13.8251), (.5012, .6955, 11.2316),
            (.3237, .4490, 7.7410), (.4420, .5332, 10.9428),
            (.6326, .7862, 15.5772)],
    }
    return pd.DataFrame([
        {'vegetable': vegetable, 'model': model, 'MAE': mae,
         'MSE': rmse ** 2, 'RMSE': rmse, 'MAPE': mape}
        for vegetable, model_results in results.items()
        for model, (mae, rmse, mape) in zip(MODELS, model_results)
    ])

def canonical_vegetable_names(column):
    """Show the English label without changing original CSV data on disk."""
    # CSV exports from the project may still use the original Malay name.
    return column.astype('string').str.strip().replace(
        to_replace=r'(?i)^sawi(?:\s+hijau)?$', value='Mustard Greens', regex=True
    )

def normalize_forecasts(df):
    if df is None:return fallback_forecasts(),True
    d=df.copy(); d.columns=d.columns.str.strip()
    if not {'vegetable','model','forecast_price'}.issubset(d.columns):return fallback_forecasts(),True
    d['model']=d['model'].replace(SHORT)
    d['vegetable'] = canonical_vegetable_names(d['vegetable'])
    if 'forecast_week' not in d.columns:d['forecast_week']='2026-07-27'
    d['forecast_price']=pd.to_numeric(d['forecast_price'],errors='coerce')
    return d.dropna(subset=['forecast_price']),False

def normalize_metrics(df):
    if df is None:
        return fallback_metrics(), True
    d = df.copy()
    d.columns = d.columns.str.strip()
    if not {'vegetable', 'model', 'MAE'}.issubset(d.columns):
        return fallback_metrics(), True
    for col in ['MAE', 'MSE', 'RMSE', 'MAPE']:
        if col not in d.columns:
            d[col] = float('nan')
        d[col] = pd.to_numeric(d[col], errors='coerce')
    # MSE has units RM². If the evaluation CSV has RMSE but no MSE,
    # calculate its mathematically equivalent squared value.
    missing_mse = d['MSE'].isna() & d['RMSE'].notna()
    d.loc[missing_mse, 'MSE'] = d.loc[missing_mse, 'RMSE'] ** 2
    d['model'] = d['model'].replace(SHORT)
    d['vegetable'] = canonical_vegetable_names(d['vegetable'])
    return d, False

forecasts, forecast_fallback = normalize_forecasts(read_csv('all_model_forecasts.csv'))
metrics, metrics_fallback = normalize_metrics(read_csv('model_evaluation.csv'))
prices = read_csv('weekly_vegetable_prices.csv')
if prices is not None and {'week_start','vegetable','retail_price'}.issubset(prices.columns):
    prices=prices.copy();prices['week_start']=pd.to_datetime(prices['week_start'],errors='coerce');prices['retail_price']=pd.to_numeric(prices['retail_price'],errors='coerce')
    prices['vegetable'] = canonical_vegetable_names(prices['vegetable'])
else:prices=None

# One user decision only: which vegetable to inspect.
with st.sidebar:
    st.header('Select a vegetable')
    vegetable = st.selectbox('Vegetable', VEGETABLES, key='selected_vegetable')
    st.divider()
    vegetable_details = {
        'Mustard Greens': {'item': 'Mustard Greens', 'code': '1558'},
        'Tomato': {'item': 'Tomato', 'code': '114'},
        'Chilli': {'item': 'Cili merah – Kulai', 'code': '93'},
        'Cabbage': {'item': 'Kubis bulat – tempatan', 'code': '105'},
        'Cucumber': {'item': 'Timun', 'code': '113'},
    }
    selected_details = vegetable_details[vegetable]
    st.markdown(f'### 🥬 About {vegetable}')
    st.markdown(f'**Vegetable in dataset:** {selected_details["item"]}')
    st.markdown('**Retail price source:** DOSM PriceCatcher (Malaysia)')
    st.markdown(f'**PriceCatcher item code:** {selected_details["code"]}')
    st.markdown('**Price coverage:** Nationwide Malaysian retail prices, grouped by week')
    st.markdown('**Weather locations:** Batu Pahat, Johor and Cameron Highlands-labelled series, Pahang')
    st.markdown('**Weather measurements:** Rainfall, temperature and humidity')
    st.caption('Both weather-location series are used for every vegetable. They do not identify where the vegetable was grown or sold. The Cameron Highlands-labelled station details still require verification.')

# Use one selected vegetable throughout the entire single-page dashboard.
selected_forecasts = forecasts[forecasts['vegetable'].str.casefold() == vegetable.casefold()].copy()
selected_metrics = metrics[metrics['vegetable'].str.casefold() == vegetable.casefold()].copy()
selected_metrics['model'] = selected_metrics['model'].replace(SHORT)
selected_forecasts['model'] = selected_forecasts['model'].replace(SHORT)
hybrid_name = 'M4 Hybrid'
hybrid_f = selected_forecasts[selected_forecasts['model'] == hybrid_name]
hybrid_m = selected_metrics[selected_metrics['model'] == hybrid_name]

def metric_value(row, key, prefix='', suffix='', digits=3):
    if row.empty or key not in row.columns or pd.isna(row.iloc[0][key]):
        return 'N/A'
    return f"{prefix}{float(row.iloc[0][key]):,.{digits}f}{suffix}"

def sorted_models(df):
    result = df.copy()
    result['model'] = pd.Categorical(result['model'], categories=MODELS, ordered=True)
    return result.sort_values('model')

st.subheader(f'{vegetable} weekly price forecasting')
st.caption('Historical demonstration: forecast origin 20 July 2026; target week 27 July 2026. Not a live forecast.')
st.markdown('#### Proposed hybrid model: ARIMA–N-BEATSX + Weather')

# Only the forecast-price card displays an RM currency prefix.  Error cards are
# deliberately displayed as decimal numbers (and MAPE as a percentage), as requested.
# The corresponding academic units remain stated accurately in the help text:
# MAE/RMSE = RM; MSE = RM squared; MAPE = percent.
c1, c2, c3, c4, c5 = st.columns(5, gap='small')
c1.metric('Forecast price', metric_value(hybrid_f, 'forecast_price', digits=2, prefix='RM '),
          help='Saved one-week-ahead M4 hybrid forecast for 27 July 2026. Only this card uses the RM prefix.')
c2.metric('MAE', metric_value(hybrid_m, 'MAE', digits=4),
          help='Mean Absolute Error: average absolute deviation. Shown as a decimal; mathematically its unit is RM. Lower is better.')
c3.metric('MSE', metric_value(hybrid_m, 'MSE', digits=4),
          help='Mean Squared Error: average squared deviation, shown as a decimal (unit RM²). Lower is better.')
c4.metric('RMSE', metric_value(hybrid_m, 'RMSE', digits=4),
          help='Root Mean Squared Error: penalises larger mistakes, shown as a decimal (unit RM). Lower is better.')
c5.metric('MAPE', metric_value(hybrid_m, 'MAPE', digits=2, suffix='%'),
          help='Mean Absolute Percentage Error: average relative forecast error. Shown as a percentage. Lower is better.')

if metrics_fallback:
    st.caption('Accuracy metrics are saved final tuned test results. MSE was calculated by squaring the rounded RMSE. For full-precision results, use deployment/model_evaluation.csv.')
if forecast_fallback:
    st.caption('The forecast uses the saved historical prototype snapshot because deployment/all_model_forecasts.csv is not available.')
st.caption("Accuracy cards show held-out testing errors as decimals (MAPE as a percentage). The forecast card alone displays a predicted price in RM; the errors are not differences from today’s price.")

# The main forecasting visual comes IMMEDIATELY AFTER the cards.
# When the project CSV is present it shows historical prices and the next-week
# M4 forecast. Otherwise, it still gives a truthful graph of saved forecasts:
# five model outputs for 27 July 2026 (not invented historical observations).
st.divider()
st.subheader(f'📈 {vegetable} forecasting graph')
st.caption('Historical research demonstration: last data week 20 July 2026; forecast target 27 July 2026. Not a live price feed.')

forecast_target = pd.NaT
forecast_value = None
if not hybrid_f.empty:
    forecast_target = pd.to_datetime(hybrid_f.iloc[0]['forecast_week'], errors='coerce')
    if pd.notna(hybrid_f.iloc[0]['forecast_price']):
        forecast_value = float(hybrid_f.iloc[0]['forecast_price'])

selected_history = pd.DataFrame()
if prices is not None:
    selected_history = prices[
        prices['vegetable'].str.casefold() == vegetable.casefold()
    ].dropna(subset=['week_start', 'retail_price']).sort_values('week_start').copy()
    # Do not plot data from AFTER the target date as if it were known at the origin.
    if pd.notna(forecast_target):
        selected_history = selected_history[selected_history['week_start'] < forecast_target]
    selected_history = selected_history.tail(30)

if not selected_history.empty:
    forecast_fig = go.Figure()
    forecast_fig.add_trace(go.Scatter(
        x=selected_history['week_start'], y=selected_history['retail_price'],
        mode='lines+markers', name='Observed weekly retail price',
        line=dict(color='#20846d', width=3), marker=dict(size=6),
        hovertemplate='<b>Recorded price</b><br>Week of %{x|%d %b %Y}<br>RM %{y:.2f}<extra></extra>'
    ))
    if forecast_value is not None and pd.notna(forecast_target):
        last_date = selected_history.iloc[-1]['week_start']
        last_price = float(selected_history.iloc[-1]['retail_price'])
        forecast_fig.add_trace(go.Scatter(
            x=[last_date, forecast_target], y=[last_price, forecast_value],
            mode='lines+markers', name='M4 hybrid: next-week forecast',
            line=dict(color='#d18838', width=4, dash='dash'),
            marker=dict(color='#d18838', size=[7, 13], symbol=['circle', 'diamond']),
            customdata=['Last recorded week', 'Forecast week'],
            hovertemplate='<b>%{customdata}</b><br>%{x|%d %b %Y}<br>RM %{y:.2f}<extra></extra>'
        ))
        forecast_fig.add_annotation(
            x=forecast_target, y=forecast_value,
            text=f'<b>Forecast: RM {forecast_value:.2f}</b>',
            showarrow=True, arrowhead=2, ax=-85, ay=-48,
            font=dict(color='#99591a', size=13), bgcolor='#fff4e4',
            bordercolor='#e8cba2', borderpad=5
        )
    forecast_fig.update_layout(
        height=450, autosize=True, width=None,
        margin=dict(l=15, r=20, t=35, b=75),
        hovermode='x unified',
        xaxis_title='Week', yaxis_title='Weekly retail price (RM)',
        legend=dict(orientation='h', x=0, y=-0.23),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
    )
    forecast_fig.update_xaxes(showgrid=True, gridcolor='#e8eeec')
    forecast_fig.update_yaxes(showgrid=True, gridcolor='#e8eeec', tickprefix='RM ')
    st.plotly_chart(forecast_fig, use_container_width=True,
                    config={'responsive': True}, key=f'forecast_line_{vegetable}')
    st.caption('Solid green = observed weekly retail prices; dashed orange = the single next-week hybrid forecast. The orange point is a prediction, not an actual observed price.')
else:
    # Chart always exists even when the optional historical price CSV has not
    # been added to GitHub. This is a forecast-comparison chart, not history.
    forecast_comparison = sorted_models(selected_forecasts).dropna(subset=['forecast_price'])
    if not forecast_comparison.empty:
        st.info('Historical weekly prices are not available in the deployed files. Showing the saved one-week-ahead forecasts from all five models instead.')
        vals = forecast_comparison['forecast_price'].astype(float).tolist()
        colors = ['#cf9c60' if name != hybrid_name else '#20846d'
                  for name in forecast_comparison['model'].astype(str)]
        compare_fig = go.Figure(go.Bar(
            y=forecast_comparison['model'].astype(str), x=vals,
            orientation='h', marker_color=colors,
            text=[f'RM {value:.2f}' for value in vals], textposition='outside',
            cliponaxis=False,
            hovertemplate='<b>%{y}</b><br>27 July 2026 forecast: RM %{x:.2f}<extra></extra>'
        ))
        compare_fig.update_layout(
            height=400, autosize=True, width=None,
            margin=dict(l=15, r=65, t=15, b=45),
            xaxis_title='Predicted weekly retail price (RM)',
            yaxis_title='',
            yaxis=dict(autorange='reversed'),
            xaxis=dict(range=[0, max(vals) * 1.22] if max(vals) > 0 else None),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(compare_fig, use_container_width=True,
                        config={'responsive': True}, key=f'forecast_comparison_{vegetable}')
        st.caption('These are five saved model forecasts for the same historical target week. They do not represent five observed market prices.')
    else:
        st.warning('No forecasting data are available for the selected vegetable.')

st.divider()
# SHAP follows the forecasting graph and updates with the selected vegetable.
# It explains M3b (weather-aware N-BEATSX), not the M4 hybrid forecast.
SHAP_VALUES = {
    'Cabbage': ('Batu Pahat rainfall', .034949, .033331, .006720, .000707),
    'Chilli': ('Cameron Highlands rainfall', .092971, .079317, .021079, .001461),
    'Cucumber': ('Cameron Highlands rainfall', .074078, .095803, .012753, .000762),
    'Mustard Greens': ('Cameron Highlands rainfall', .067985, .098970, .013423, .002099),
    'Tomato': ('Cameron Highlands rainfall', .097092, .064827, .022088, .002625),
}
top_feature, top_influence, rain, humidity, temperature = SHAP_VALUES[vegetable]
st.markdown(f'### 🔎 Explainable AI (SHAP): {vegetable}')
st.caption('What affected the weather-aware N-BEATSX (M3b) forecasts? These are historical SHAP attributions, not explanations of the hybrid (M4) price card.')
st.caption('Six sampled test forecasts per vegetable, with 10 training reference observations. The price input history was held fixed during the weather-input analysis.')

shap_data = pd.DataFrame({
    'Weather factor': ['Rainfall', 'Humidity', 'Temperature'],
    'Mean absolute model influence (RM)': [rain, humidity, temperature]
})
shap_fig = px.bar(
    shap_data, x='Mean absolute model influence (RM)', y='Weather factor',
    orientation='h', color='Weather factor',
    color_discrete_map={'Rainfall': '#24806b', 'Humidity': '#87a2d2', 'Temperature': '#d3a252'},
    text='Mean absolute model influence (RM)'
)
shap_fig.update_traces(
    texttemplate='%{x:.4f}', textposition='outside',
    hovertemplate='<b>%{y}</b><br>Typical model-attribution magnitude: RM %{x:.4f}<extra></extra>'
)
shap_fig.update_layout(
    autosize=True, width=None, showlegend=False, height=290,
    xaxis_title='Mean absolute SHAP magnitude (RM)', yaxis_title='',
    yaxis={'categoryorder': 'total ascending'}, margin=dict(l=10, r=80, t=15, b=20)
)
st.plotly_chart(shap_fig, use_container_width=True, config={'responsive': True},
                key=f'shap_by_vegetable_{vegetable}')

st.markdown(f'''<div class="weather-explain">
<h4>What do the SHAP results mean for {vegetable}?</h4>
<p><b>Rainfall</b> has the largest typical SHAP magnitude among the three weather categories
shown. The single weather measurement with the largest individual influence was
<b>{top_feature}</b> (mean absolute SHAP = <b>RM {top_influence:.4f}</b>).</p>
<p>Longer bars mean the weather input changed the <b>model's prediction</b> more, on average,
relative to its reference conditions. Because these are absolute values, they do not show
whether the prediction increased or decreased.</p>
<p><small><b>Important:</b> SHAP describes model behaviour, not the actual causal effect of
weather on market prices. These are M3b weather-feature attributions and <b>must not</b>
be described as an explanation of the separate M4 hybrid forecast displayed above.</small></p>
</div>''', unsafe_allow_html=True)
st.caption('The bars group the absolute sums of the two weather-location contributions within each sampled forecast. The top individual feature is calculated separately, so its magnitude need not match the rainfall bar.')

st.divider()
st.subheader('How accurate were the five forecasting methods?')
st.caption('Models are ranked using held-out test MAE. The best model has the LOWEST error and is highlighted in green.')
chart_data = selected_metrics.dropna(subset=['MAE']).drop_duplicates(subset=['model']).copy()
if not chart_data.empty:
    # Rank models dynamically for whichever vegetable is selected. This uses
    # the actual evaluation CSV when available, not a hard-coded winner.
    chart_data['MAE'] = pd.to_numeric(chart_data['MAE'], errors='coerce')
    chart_data = chart_data.dropna(subset=['MAE']).sort_values(
        ['MAE', 'model'], ascending=[True, True]
    ).reset_index(drop=True)
    if not chart_data.empty:
        best_mae = float(chart_data.iloc[0]['MAE'])
        best_models = chart_data.loc[chart_data['MAE'].sub(best_mae).abs() < 1e-10, 'model'].tolist()
        winner_text = ', '.join(str(model) for model in best_models)
        st.success(f'🏆 BEST MODEL FOR {vegetable.upper()}: {winner_text} — lowest MAE {best_mae:.4f}')

        short_labels = {
            'M1 ARIMA': 'M1 · ARIMA',
            'M2 LSTM': 'M2 · LSTM',
            'M3a N-BEATSX Price Only': 'M3a · N-BEATSX (Price Only)',
            'M3b N-BEATSX + Weather': 'M3b · N-BEATSX (+ Weather)',
            'M4 Hybrid': 'M4 · Hybrid',
        }
        ranked_names = []
        ranked_values = chart_data['MAE'].astype(float).tolist()
        ranked_colors = []
        for i, row in chart_data.iterrows():
            name = str(row['model'])
            is_best = abs(float(row['MAE']) - best_mae) < 1e-10
            ranked_names.append(f'#{i + 1}  {short_labels.get(name, name)}' + ('  ★ BEST' if is_best else ''))
            ranked_colors.append('#17866D' if is_best else '#BACDC8')

        fig = go.Figure(go.Bar(
            x=ranked_values, y=ranked_names, orientation='h',
            marker=dict(color=ranked_colors, line=dict(width=0)),
            text=[f'{v:.4f}' for v in ranked_values],
            textposition='outside', textfont=dict(size=19, color='#263746'),
            cliponaxis=False,
            customdata=chart_data['model'].astype(str),
            hovertemplate='<b>%{customdata}</b><br>MAE: %{x:.4f}<br>Lower error = better prediction accuracy<extra></extra>'
        ))
        fig.update_layout(
            title=dict(text='Model ranking — best at the top', font=dict(size=20), x=0.01),
            autosize=True, width=None, height=430, showlegend=False,
            margin=dict(l=15, r=95, t=68, b=45),
            font=dict(size=15, color='#344254'),
            xaxis=dict(title='MAE — lower is better', range=[0, max(ranked_values) * 1.18] if max(ranked_values) > 0 else None,
                       tickfont=dict(size=14), gridcolor='#E7ECEB', zeroline=False),
            yaxis=dict(title='', autorange='reversed', tickfont=dict(size=16), automargin=True),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            bargap=0.34,
        )
        st.plotly_chart(fig, use_container_width=True,
                        config={"responsive": True, "displaylogo": False},
                        key=f"vegcast_chart_2_{vegetable}")
        st.caption('Green = lowest MAE (most accurate on these test weeks). Grey = other models. MAE is mathematically measured in RM, although numbers are shown without an RM prefix.')
if not selected_forecasts.empty:
    st.markdown('**Next-week prototype forecasts by model**')
    show = sorted_models(selected_forecasts)[['model', 'forecast_price']].copy()
    show['forecast_price'] = pd.to_numeric(show['forecast_price'], errors='coerce')
    forecast_table = show.rename(columns={'model': 'Model', 'forecast_price': 'Forecast price (RM)'})
    forecast_palette = ['#E8F5EE', '#EAF0FF', '#FFF0E6', '#F4ECFC', '#E9F6F7']
    forecast_style = (forecast_table.style
        .format({'Forecast price (RM)': '{:.2f}'})
        .apply(lambda row: [f'background-color: {forecast_palette[row.name % len(forecast_palette)]}; color: #263744; font-weight: 600' for _ in row], axis=1)
        .set_table_styles([{'selector': 'th', 'props': [('background-color', '#DDECE7'), ('color', '#263744'), ('font-weight', 'bold')]}]))
    st.dataframe(forecast_style, hide_index=True, use_container_width=True)
st.markdown('**Detailed accuracy results**')
st.caption('MAE = mean absolute error (RM); MSE = mean squared error (RM²); RMSE = root mean squared error (RM); MAPE = mean absolute percentage error (%). Lower is better.')
if not selected_metrics.empty:
    table = sorted_models(selected_metrics)[['model', 'MAE', 'MSE', 'RMSE', 'MAPE']].rename(columns={'model':'Model'})
    accuracy_palette = ['#E8F5EE', '#EAF0FF', '#FFF0E6', '#F4ECFC', '#E9F6F7']
    accuracy_style = (table.style
        .format({'MAE': '{:.4f}', 'MSE': '{:.4f}', 'RMSE': '{:.4f}', 'MAPE': '{:.2f}%'}, na_rep='N/A')
        .apply(lambda row: [f'background-color: {accuracy_palette[row.name % len(accuracy_palette)]}; color: #263744; font-weight: 600' for _ in row], axis=1)
        .set_table_styles([{'selector': 'th', 'props': [('background-color', '#DDECE7'), ('color', '#263744'), ('font-weight', 'bold')]}]))
    st.dataframe(accuracy_style, hide_index=True, use_container_width=True)

st.divider()
st.subheader(f'Weather and model accuracy: {vegetable}')
st.markdown('#### Did using weather information improve accuracy?')
ab = selected_metrics[selected_metrics['model'].isin(['M3a N-BEATSX Price Only', 'M3b N-BEATSX + Weather'])].copy()
if not ab.empty:
    fig = px.bar(ab, x='model', y='MAE', color='model', text='MAE', color_discrete_sequence=['#24806b', '#d3a252'])
    fig.update_traces(texttemplate='RM %{y:.4f}', textposition='outside', hovertemplate='<b>%{x}</b><br>Average prediction error: RM %{y:.4f}<extra></extra>')
    fig.update_layout(autosize=True, transition=dict(duration=450, easing='cubic-in-out'), showlegend=False, height=340, xaxis_title='', yaxis_title='Average prediction error (RM)')
    fig.update_layout(autosize=True, width=None)
    st.plotly_chart(fig, use_container_width=True, config={"responsive": True}, key=f"vegcast_chart_3_{vegetable}")
    if len(ab) == 2:
        price_only = float(ab.loc[ab['model']=='M3a N-BEATSX Price Only', 'MAE'].iloc[0])
        weather = float(ab.loc[ab['model']=='M3b N-BEATSX + Weather', 'MAE'].iloc[0])
        if weather > price_only:
            st.info(f'For {vegetable}, weather-aware N-BEATSX had higher MAE (RM {weather:.4f}) than price-only N-BEATSX (RM {price_only:.4f}). This does not prove weather is irrelevant to actual prices.')


st.caption('The weather-aware and price-only N-BEATSX models were tuned separately; this comparison is informative but not a perfectly controlled weather-only ablation.')

st.divider()
st.caption('Weather Aware Forecast Vegetable Price · FYP research prototype · Historical saved model outputs, not a live market-price service')
