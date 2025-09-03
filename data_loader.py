# file: data_loader.py

import yfinance as yf
import streamlit as st
import pandas as pd

@st.cache_data(ttl=900)
def load_data(ticker: str, start_date, end_date) -> pd.DataFrame | None:
    """
    지정된 티커와 기간에 대한 주식 데이터를 Yahoo Finance에서 다운로드합니다.
    데이터는 15분 동안 캐시됩니다.
    """
    try:
        data = yf.download(ticker, start=start_date, end=end_date)
        if data.empty:
            st.warning(f"'{ticker}'에 대한 데이터를 찾을 수 없습니다.")
            return None
        
        # --- START: 추가된 부분 ---
        # 데이터 로드 직후, 인덱스가 날짜 타입이 아닐 가능성을 원천 차단합니다.
        data.index = pd.to_datetime(data.index)
        data = data[data.index.notna()]
        # --- END: 추가된 부분 ---
        
        return data
    except Exception as e:
        st.error(f"'{ticker}' 데이터 다운로드 중 오류 발생: {e}")
        return None