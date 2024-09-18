import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objs as go
from data_loader import load_data
from etf_analysis import analyze_etf, analyze_risk_and_benchmark, analyze_factor_exposure, compare_etfs, analyze_macro_market_correlation
from gpt_analysis import analyze_etf_performance, analyze_risk_and_benchmark as gpt_analyze_risk, analyze_factor_exposure as gpt_analyze_factor, compare_etfs as gpt_compare_etfs, analyze_macro_correlation, get_etf_recommendation, predict_etf_performance
from visualizations import (
    plot_price_performance, plot_risk_metrics, plot_factor_exposure, 
    plot_etf_comparison, plot_macro_correlation,
    plot_portfolio_summary, plot_cumulative_returns, plot_asset_allocation, plot_efficient_frontier
)
from portfolio_analysis import analyze_portfolio, calculate_portfolio_performance, analyze_risk, analyze_asset_allocation, optimize_portfolio

st.set_page_config(page_title="ETF 분석 및 포트폴리오 대시보드", layout="wide", initial_sidebar_state="expanded")

# 대시보드 선택
dashboard_type = st.sidebar.radio("대시보드 선택", ["ETF 분석 대시보드", "ETF 포트폴리오 분석 대시보드"])

if dashboard_type == "ETF 분석 대시보드":
    # ETF 분석 대시보드 코드
    st.title("ETF 분석 대시보드")
    
    # 사이드바 설정
    ticker = st.sidebar.text_input("ETF 티커 입력", value="SPY")
    start_date = st.sidebar.date_input("시작 날짜", value=pd.to_datetime("2022-01-01"))
    end_date = st.sidebar.date_input("종료 날짜", value=pd.to_datetime("2024-07-31"))
    benchmark_ticker = st.sidebar.text_input("벤치마크 티커 입력", value="^GSPC")

    @st.cache_data
    def load_cached_data(ticker, start_date, end_date):
        return load_data(ticker, start_date, end_date)

    # 데이터 로드 및 기본 분석
    data = load_cached_data(ticker, start_date, end_date)
    benchmark_data = load_cached_data(benchmark_ticker, start_date, end_date)

    if data is None or benchmark_data is None:
        st.error("데이터를 불러오는 데 실패했습니다. 입력을 확인하고 다시 시도해주세요.")
        st.stop()

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["개요", "성과 분석", "리스크 분석", "팩터 분석", "ETF 비교", "매크로 분석"])

    with tab1:
        st.header("ETF 개요")
        col1, col2 = st.columns([2, 1])
        with col1:
            plot_price_performance(data, ticker)
        with col2:
            etf_info = analyze_etf(data, ticker)
            for key, value in etf_info.items():
                st.metric(label=key, value=value)

    with tab2:
        st.header("성과 분석")
        performance_metrics = analyze_etf(data, ticker)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("연간 수익률", performance_metrics["연간 수익률"])
        with col2:
            st.metric("연간 변동성", performance_metrics["연간 변동성"])
        with col3:
            st.metric("샤프 비율", performance_metrics["샤프 비율"])
        
        if st.button("GPT 성과 분석 실행", key="performance_gpt"):
            with st.spinner("GPT 분석 중..."):
                gpt_analysis = analyze_etf_performance(str(data))
            st.success("GPT 분석 완료!")
            st.write(gpt_analysis)

    with tab3:
        st.header("리스크 분석")
        risk_metrics = analyze_risk_and_benchmark(data, benchmark_data, ticker, benchmark_ticker)
        plot_risk_metrics(risk_metrics, ticker, benchmark_ticker)
        
        if st.button("GPT 리스크 분석 실행", key="risk_gpt"):
            with st.spinner("GPT 분석 중..."):
                gpt_analysis = gpt_analyze_risk(str(risk_metrics))
            st.success("GPT 분석 완료!")
            st.write(gpt_analysis)

    with tab4:
        st.header("팩터 분석")
        factor_exposure = analyze_factor_exposure(ticker, start_date, end_date)
        plot_factor_exposure(factor_exposure)
        
        if st.button("GPT 팩터 분석 실행", key="factor_gpt"):
            with st.spinner("GPT 분석 중..."):
                gpt_analysis = gpt_analyze_factor(str(factor_exposure))
            st.success("GPT 분석 완료!")
            st.write(gpt_analysis)

    with tab5:
        st.header("ETF 비교")
        etfs_to_compare = st.multiselect("비교할 ETF 선택", ["SPY", "IVV", "VOO", "SPLG"], default=["SPY", "IVV", "VOO"])
        comparison_data = compare_etfs(etfs_to_compare, start_date, end_date)
        plot_etf_comparison(comparison_data)
        
        if st.button("GPT ETF 비교 분석 실행", key="compare_gpt"):
            with st.spinner("GPT 분석 중..."):
                gpt_analysis = gpt_compare_etfs(str(comparison_data))
            st.success("GPT 분석 완료!")
            st.write(gpt_analysis)

    with tab6:
        st.header("매크로 분석")
        correlation_data = analyze_macro_market_correlation(ticker, start_date, end_date)
        plot_macro_correlation(correlation_data, ticker)
        
        if st.button("GPT 매크로 분석 실행", key="macro_gpt"):
            with st.spinner("GPT 분석 중..."):
                gpt_analysis = analyze_macro_correlation(str(correlation_data))
            st.success("GPT 분석 완료!")
            st.write(gpt_analysis)

else:
    # ETF 포트폴리오 분석 대시보드 코드
    st.title("ETF 포트폴리오 분석 대시보드")

    # 포트폴리오 입력
    st.sidebar.title("포트폴리오 구성")

    if 'portfolio' not in st.session_state:
        st.session_state.portfolio = pd.DataFrame(columns=['ETF', 'Weight'])

    new_etf = st.sidebar.text_input("ETF 티커 입력")
    new_weight = st.sidebar.number_input("비중 입력 (%)", min_value=0.0, max_value=100.0, step=0.1)

    if st.sidebar.button("ETF 추가"):
        new_row = pd.DataFrame({'ETF': [new_etf], 'Weight': [new_weight/100]})
        st.session_state.portfolio = pd.concat([st.session_state.portfolio, new_row], ignore_index=True)

    st.sidebar.write("현재 포트폴리오:")
    edited_portfolio = st.sidebar.data_editor(st.session_state.portfolio, num_rows="dynamic")
    st.session_state.portfolio = edited_portfolio

    if st.sidebar.button("포트폴리오 저장"):
        st.sidebar.download_button(
            label="Download Portfolio",
            data=st.session_state.portfolio.to_csv(index=False),
            file_name="my_portfolio.csv",
            mime="text/csv"
        )

    uploaded_file = st.sidebar.file_uploader("포트폴리오 불러오기", type="csv")
    if uploaded_file is not None:
        st.session_state.portfolio = pd.read_csv(uploaded_file)

    if not st.session_state.portfolio.empty:
        # 데이터 준비
        end_date = pd.Timestamp.now()
        start_date = end_date - pd.DateOffset(years=5)
        
        # 포트폴리오 분석
        portfolio_data = analyze_portfolio(st.session_state.portfolio, start_date, end_date)
        performance_metrics = calculate_portfolio_performance(portfolio_data)
        risk_metrics = analyze_risk(portfolio_data)
        asset_allocation = analyze_asset_allocation(st.session_state.portfolio)

        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "포트폴리오 개요", "성과 분석", "리스크 분석", "자산 배분", "개별 ETF 분석", "최적화 제안"
        ])

        with tab1:
            st.header("포트폴리오 개요")
            plot_portfolio_summary(portfolio_data, performance_metrics)

        with tab2:
            st.header("성과 분석")
            st.write("연간 수익률: {:.2f}%".format(performance_metrics['Annual Return'] * 100))
            st.write("연간 변동성: {:.2f}%".format(performance_metrics['Annual Volatility'] * 100))
            st.write("샤프 비율: {:.2f}".format(performance_metrics['Sharpe Ratio']))
            plot_cumulative_returns(portfolio_data)

        with tab3:
            st.header("리스크 분석")
            st.write("베타: {:.4f}".format(risk_metrics['Beta']))
            st.write("알파: {:.2f}%".format(risk_metrics['Alpha'] * 100))
            st.write("최대 낙폭: {:.2f}%".format(risk_metrics['Max Drawdown'] * 100))
            st.write("Value at Risk (95%): {:.2f}%".format(risk_metrics['Value at Risk (95%)'] * 100))


        with tab4:
            st.header("자산 배분")
            plot_asset_allocation(asset_allocation)

        with tab5:
            st.header("개별 ETF 분석")
            for etf in st.session_state.portfolio['ETF']:
                with st.expander(f"{etf} 상세 정보"):
                    etf_data = yf.Ticker(etf).info
                    st.write(etf_data)

        with tab6:
            st.header("포트폴리오 최적화 제안")
            efficient_frontier, optimal_portfolio = optimize_portfolio(portfolio_data)
            plot_efficient_frontier(efficient_frontier, optimal_portfolio)

        # GPT 분석
        if st.button("GPT 포트폴리오 분석 실행"):
            with st.spinner("GPT 분석 중..."):
                gpt_analysis = analyze_portfolio_gpt(portfolio_data, performance_metrics, risk_metrics)
            st.success("GPT 분석 완료!")
            st.write(gpt_analysis)

    else:
        st.info("포트폴리오를 구성하려면 사이드바에서 ETF를 추가하세요.")

# 푸터
st.sidebar.markdown("---")
st.sidebar.info("© 2024 ETF 분석 및 포트폴리오 대시보드. All rights reserved.")