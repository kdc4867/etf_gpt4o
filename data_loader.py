import yfinance as yf
import streamlit as st

@st.cache_data
def load_data(ticker, start_date, end_date):
    try:
        data = yf.download(ticker, start=start_date, end=end_date)
        if data.empty:
            st.warning(f"{ticker}에 대한 데이터를 찾을 수 없습니다.")
            return None
        return data
    except Exception as e:
        st.error(f"{ticker} 데이터 다운로드 중 오류 발생: {str(e)}")
        return None