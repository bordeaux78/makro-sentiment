import streamlit as st
import datetime
import requests
from pytrends.request import TrendReq

# === Makro sentiment skor hesaplama ===

def get_dxy_score():
    dxy_value = 106.5  # örnek sabit değer (ileride API ile dinamik yapılabilir)
    score = -1 if dxy_value > 105 else 0
    return score, f"DXY: {dxy_value} → {'-1' if score == -1 else '0'}"

def get_cpi_score():
    cpi_actual = 3.8
    cpi_expected = 3.4
    score = -1 if cpi_actual > cpi_expected else 0
    return score, f"CPI: {cpi_actual}% (beklenti: {cpi_expected}%) → {'-1' if score == -1 else '0'}"

def get_fear_greed_score():
    try:
        res = requests.get("https://api.alternative.me/fng/?limit=1&format=json")
        data = res.json()
        value = int(data["data"][0]["value"])
        score = -1 if value < 25 else (1 if value > 70 else 0)
        return score, f"Fear & Greed Index: {value} → {score:+}"
    except:
        return 0, "Fear & Greed Index: alınamadı → 0"

def get_google_trend_score():
    try:
        pytrends = TrendReq(hl='en-US', tz=360)
        kw_list = ["Bitcoin"]
        pytrends.build_payload(kw_list, cat=0, timeframe='now 7-d', geo='', gprop='')
        data = pytrends.interest_over_time()
        if not data.empty:
            last_val = data["Bitcoin"].iloc[-1]
            prev_val = data["Bitcoin"].iloc[0]
            score = 1 if last_val > prev_val else 0
            return score, f"Google Trends (BTC): artış → {score:+}"
        else:
            return 0, "Google Trends: veri yok → 0"
    except:
        return 0, "Google Trends: alınamadı → 0"

# === Skorları topla ===
scores = []
details = []

for fn in [get_dxy_score, get_cpi_score, get_fear_greed_score, get_google_trend_score]:
    score, detail = fn()
    scores.append(score)
    details.append(detail)

total_score = sum(scores)

# === Sentiment yorumu ===
if total_score >= 2:
    sentiment = "BULLISH"
    color = "green"
elif total_score <= -2:
    sentiment = "BEARISH"
    color = "red"
else:
    sentiment = "NEUTRAL"
    color = "gray"

# === Streamlit Arayüz ===
st.set_page_config(page_title="Makro Sentiment Skoru", layout="centered")
st.title("📊 Makro & Haber Temelli Kripto Sentiment Skoru")
st.markdown(f"### 🧠 Genel Yorum: **`: {sentiment}`**", unsafe_allow_html=True)
st.markdown(f"#### 🔢 Skor: `{total_score:+}`")

st.markdown("---")
st.markdown("### 📋 Detaylar:")
for detail in details:
    st.write("- " + detail)

st.markdown("---")
st.caption(f"Güncellenme zamanı: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
