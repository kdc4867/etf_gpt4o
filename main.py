###main.py
import streamlit as st
import pandas as pd
import networkx as nx
from data_loader import load_data
from etf_analysis import analyze_etf, analyze_risk_and_benchmark, analyze_factor_exposure, compare_etfs, analyze_macro_market_correlation
from gpt_analysis import analyze_etf_performance, analyze_risk_and_benchmark as gpt_analyze_risk, analyze_factor_exposure as gpt_analyze_factor, compare_etfs as gpt_compare_etfs, analyze_macro_correlation, get_etf_recommendation, predict_etf_performance
# 페이지 설정
st.set_page_config(page_title="ETF 분석 대시보드", layout="wide")

# 제목
st.title("ETF 분석 대시보드")

# 사이드바 설정
ticker = st.sidebar.text_input("ETF 티커 입력", value="SPY")
start_date = st.sidebar.date_input("시작 날짜", value=pd.to_datetime("2022-01-01"))
end_date = st.sidebar.date_input("종료 날짜", value=pd.to_datetime("2024-07-31"))
benchmark_ticker = st.sidebar.text_input("벤치마크 티커 입력", value="^GSPC")

try:
    # 데이터 로드
    data = load_data(ticker, start_date, end_date)
    benchmark_data = load_data(benchmark_ticker, start_date, end_date)

    if data is not None and benchmark_data is not None:
        # 1. ETF 개요 및 성과 분석
        st.header("1. ETF 개요 및 성과 분석")
        analyze_etf(data, ticker)

        # 2. 리스크 및 벤치마크 분석
        st.header("2. 리스크 및 벤치마크 분석")
        analyze_risk_and_benchmark(data, benchmark_data, ticker, benchmark_ticker)

        # 3. 팩터 분석
        st.header("3. 팩터 분석")
        analyze_factor_exposure(ticker, start_date, end_date)

        # 4. ETF 비교
        st.header("4. ETF 비교")
        etfs_to_compare = st.multiselect("비교할 ETF 선택", ["SPY", "IVV", "VOO", "SPLG"], default=["SPY", "IVV", "VOO"])
        compare_etfs(etfs_to_compare, start_date, end_date)

        # 5. 매크로 및 마켓 상황 연관성
        st.header("5. 매크로 및 마켓 상황 연관성")
        analyze_macro_market_correlation(ticker, start_date, end_date)
        
        # 6. GPT 기반 추천 및 예측
        st.header("6. GPT 기반 ETF 추천 및 예측")

        risk_profile = st.selectbox("투자자 리스크 프로필", ["보수적", "중립적", "공격적"])

        st.subheader("ETF 추천")
        recommendation = get_etf_recommendation(str(data), risk_profile)
        if recommendation:
            st.write(recommendation)

        st.subheader("ETF 성과 예측")
        market_conditions = st.text_area("현재 시장 상황을 간단히 설명해주세요:")
        if market_conditions:
            performance_prediction = predict_etf_performance(str(data), market_conditions)
            if performance_prediction:
                st.write(performance_prediction)
    else:
        st.error("데이터를 불러오는 데 실패했습니다. 입력을 확인하고 다시 시도해주세요.")
except Exception as e:
    st.error(f"분석 중 오류가 발생했습니다: {str(e)}")

# 앱 실행 방법 안내
st.sidebar.markdown("---")
st.sidebar.subheader("앱 실행 방법")
st.sidebar.markdown("""
1. 터미널에서 다음 명령어 실행:
streamlit run main.py
2. 브라우저에서 표시된 URL 열기
""")
