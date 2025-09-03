# file: financial_dashboard.py
import yfinance as yf
import streamlit as st
from typing import Any, Dict

@st.cache_data(ttl=3600)
def load_ticker_info(ticker: str) -> Dict[str, Any] | None:
    try:
        info = yf.Ticker(ticker).info
        if not info or info.get("regularMarketPrice") is None:
            st.error(f"'{ticker}' 재무 정보를 불러올 수 없습니다. 티커를 확인하세요.")
            return None
        return info
    except Exception as e:
        st.error(f"'{ticker}' 정보를 불러오는 중 오류: {e}")
        return None

def format_large_number(value: Any) -> str:
    if isinstance(value, (int, float)):
        if value >= 1e12:  # 조
            return f"{value/1e12:.2f}조"
        if value >= 1e8:   # 억
            return f"{value/1e8:.2f}억"
        return f"{value:,.0f}"
    return "N/A"

def format_percentage(value: Any) -> str:
    if isinstance(value, (int, float)):
        return f"{value*100:.2f}%"
    return "N/A"

def format_float(value: Any) -> str:
    if isinstance(value, (int, float)):
        return f"{value:.2f}"
    return "N/A"

def display_financial_info(info: Dict[str, Any]):
    if not info:
        return
    st.subheader(f"{info.get('longName','N/A')} ({info.get('symbol','N/A')})")
    st.markdown(
        f"- **산업**: {info.get('industry','N/A')}\n"
        f"- **섹터**: {info.get('sector','N/A')}\n"
        f"- **직원 수**: {format_large_number(info.get('fullTimeEmployees'))}\n"
        f"- **웹사이트**: [{info.get('website','#')}]({info.get('website','#')})\n"
        f"- **본사**: {info.get('address1','N/A')}, {info.get('city','N/A')}, {info.get('state','N/A')}"
    )
    st.divider()
    st.subheader("주요 재무 정보")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("시가총액", format_large_number(info.get('marketCap')))
        st.metric("총 매출", format_large_number(info.get('totalRevenue')))
        st.metric("총 현금", format_large_number(info.get('totalCash')))
    with c2:
        st.metric("EBITDA", format_large_number(info.get('ebitda')))
        st.metric("영업 현금흐름", format_large_number(info.get('operatingCashflow')))
        st.metric("부채비율 (D/E)", format_float(info.get('debtToEquity')))
    with c3:
        st.metric("P/E", format_float(info.get('trailingPE')))
        st.metric("P/B", format_float(info.get('priceToBook')))
        st.metric("배당 수익률", format_percentage(info.get('dividendYield')))

# 과거 호환
load_ticker_data = load_ticker_info