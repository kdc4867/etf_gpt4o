# file: main.py
import streamlit as st
import pandas as pd
import datetime
import numpy as np

from data_loader import load_data
try:
    from financial_dashboard import load_ticker_info, display_financial_info
except ImportError:
    from financial_dashboard import load_ticker_data as load_ticker_info, display_financial_info

from etf_analysis import (
    analyze_etf_basic,
    analyze_risk_and_benchmark,
    analyze_factor_exposure,
    compare_etfs,
    analyze_macro_correlation,
)
from portfolio_analysis import (
    calculate_portfolio_performance,
    analyze_portfolio_risk,
    run_portfolio_optimization,
)
import visualizations as viz
import gpt_analysis as gpt

st.set_page_config(
    page_title="금융 분석 대시보드",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

def show_gpt_analysis(button_key: str, analysis_function, *args):
    if st.button("🤖 GPT 종합 분석 실행", key=button_key):
        with st.spinner("AI가 데이터를 분석하고 있습니다..."):
            gpt_response = analysis_function(*args)
        with st.chat_message("assistant"):
            st.markdown(gpt_response)

# ---- 단일 ETF 탭 렌더러 ----
def render_etf_overview_tab(data: pd.DataFrame, ticker: str):
    st.header(f"{ticker} 개요", divider="rainbow")
    c1, c2 = st.columns([2, 1])
    with c1:
        viz.plot_price_chart(data, ticker)
    with c2:
        basic = analyze_etf_basic(data)
        for k, v in basic.items():
            st.metric(k, v)
        show_gpt_analysis("gpt_overview", gpt.analyze_etf_performance_with_gpt, ticker, basic)

def render_etf_risk_tab(data: pd.DataFrame, benchmark_data: pd.DataFrame, ticker: str):
    st.header("리스크 분석", divider="rainbow")
    risk = analyze_risk_and_benchmark(data, benchmark_data)
    viz.plot_risk_metrics(risk)
    show_gpt_analysis("gpt_risk", gpt.analyze_risk_with_gpt, ticker, risk)

def render_etf_factor_tab(ticker: str, start_date, end_date):
    st.header("팩터 분석", divider="rainbow")
    with st.spinner("팩터 데이터를 분석 중입니다..."):
        exposure = analyze_factor_exposure(ticker, str(start_date), str(end_date))
    viz.plot_factor_exposure(exposure)
    if exposure is not None and not exposure.empty:
        show_gpt_analysis("gpt_factor", gpt.analyze_factor_with_gpt, ticker, exposure)

def render_etf_comparison_tab(start_date, end_date):
    st.header("ETF 비교 분석", divider="rainbow")
    base = ["SPY", "IVV", "VOO", "QQQ"]
    chosen = st.multiselect("비교할 ETF 선택", options=base, default=base)
    if not chosen:
        st.info("비교할 ETF를 하나 이상 선택하세요.")
        return
    df = compare_etfs(chosen, str(start_date), str(end_date))
    if df.empty:
        st.warning("선택한 ETF 데이터를 가져올 수 없습니다.")
        return
    metric = st.selectbox("비교 기준", options=df.columns[1:])
    viz.plot_etf_comparison(df, metric)
    st.dataframe(df, use_container_width=True)
    show_gpt_analysis("gpt_compare", gpt.compare_etfs_with_gpt, df)

def render_etf_macro_tab(ticker: str, start_date, end_date):
    st.header("매크로 분석", divider="rainbow")
    with st.spinner("거시 지표와의 상관관계를 계산 중..."):
        corr = analyze_macro_correlation(ticker, str(start_date), str(end_date))
    viz.plot_macro_correlation(corr, ticker)
    if not corr.empty:
        show_gpt_analysis("gpt_macro", gpt.analyze_macro_with_gpt, ticker, corr)

# ---- 재무 정보 ----
def financial_info_dashboard():
    st.title("💡 개별 티커 재무 정보")
    ticker = st.text_input("주식/ETF 티커 (예: AAPL, NVDA, SPY)", value="NVDA").upper()
    if not ticker:
        return
    info = load_ticker_info(ticker)
    if info:
        display_financial_info(info)
        st.divider()
        show_gpt_analysis("financial_gpt", gpt.analyze_financials_with_gpt, ticker, info)

# ---- 단일 ETF ----
def etf_analysis_dashboard():
    st.title("🔬 단일 ETF 심층 분석")
    with st.sidebar:
        st.header("분석 설정")
        ticker = st.text_input("ETF/주식 티커", value="SPY").upper()
        bench = st.text_input("벤치마크 티커", value="^GSPC").upper()
        today = datetime.date.today()
        start_date = st.date_input("시작 날짜", today - datetime.timedelta(days=365 * 3))
        end_date = st.date_input("종료 날짜", today)

    if not ticker:
        return

    data = load_data(ticker, start_date, end_date)
    bench_data = load_data(bench, start_date, end_date)
    if data is None or bench_data is None:
        st.error("데이터 로드 실패. 티커/날짜를 확인하세요.")
        return

    t1, t2, t3, t4, t5 = st.tabs(["개요", "리스크 분석", "팩터 분석", "ETF 비교", "매크로 분석"])
    with t1: render_etf_overview_tab(data, ticker)
    with t2: render_etf_risk_tab(data, bench_data, ticker)
    with t3: render_etf_factor_tab(ticker, start_date, end_date)
    with t4: render_etf_comparison_tab(start_date, end_date)
    with t5: render_etf_macro_tab(ticker, start_date, end_date)

# ---- 포트폴리오 ----
def portfolio_dashboard():
    st.title("💼 ETF 포트폴리오 분석")

    if "portfolio" not in st.session_state:
        st.session_state.portfolio = pd.DataFrame(columns=["ETF", "Weight"])

    with st.sidebar:
        st.header("포트폴리오 구성")
        edited = st.data_editor(
            st.session_state.portfolio,
            num_rows="dynamic",
            column_config={
                "ETF": st.column_config.TextColumn("ETF 티커", required=True),
                "Weight": st.column_config.NumberColumn("비중 (%)", min_value=0, max_value=100, format="%d%%"),
            },
            key="portfolio_editor",
        )
        if st.button("비중 재계산 및 적용"):
            tot = edited["Weight"].sum()
            if tot > 0:
                edited["Weight"] = (edited["Weight"] / tot) * 100
            st.session_state.portfolio = edited.copy()
            st.success("포트폴리오가 업데이트되었습니다.")
            st.rerun()

    total_w = st.session_state.portfolio["Weight"].sum()
    st.sidebar.metric("현재 총 비중", f"{total_w:.0f}%")
    if not st.session_state.portfolio.empty and not np.isclose(total_w, 100):
        st.sidebar.warning("비중 합이 100%가 아닙니다. 재계산 버튼으로 맞춰주세요.")

    if st.session_state.portfolio.empty or not np.isclose(total_w, 100):
        st.info("👈 사이드바에서 ETF와 비중을 입력하고 적용하세요.")
        return

    portfolio_df = st.session_state.portfolio.copy()
    portfolio_df["Weight"] = portfolio_df["Weight"] / 100.0

    today = datetime.date.today()
    start_5y = today - datetime.timedelta(days=365 * 5)

    perf = calculate_portfolio_performance(portfolio_df, start_5y, today)
    risk = analyze_portfolio_risk(perf["daily_returns"], start_5y, today)

    t1, t2, t3 = st.tabs(["포트폴리오 개요", "성과 및 리스크", "포트폴리오 최적화"])
    with t1:
        st.header("포트폴리오 요약", divider="rainbow")
        c1, c2 = st.columns(2)
        with c1:
            viz.plot_asset_allocation(portfolio_df)
        with c2:
            viz.plot_cumulative_returns(perf["daily_returns"])
        show_gpt_analysis("gpt_portfolio", gpt.analyze_portfolio_with_gpt, perf, risk, portfolio_df)

    with t2:
        st.header("상세 성과 및 리스크 지표", divider="rainbow")
        c1, c2, c3 = st.columns(3)
        c1.metric("연간 수익률", f"{perf['Annual Return']*100:.2f}%")
        c2.metric("연간 변동성", f"{perf['Annual Volatility']*100:.2f}%")
        c3.metric("샤프 비율", f"{perf['Sharpe Ratio']:.2f}")
        c1.metric("베타", f"{risk['Beta']:.2f}")
        c2.metric("연환산 알파", f"{risk['Alpha (Annualized)']*100:.2f}%")
        c3.metric("최대 낙폭", f"{risk['Max Drawdown']*100:.2f}%")

    with t3:
        st.header("포트폴리오 최적화 제안 (효율적 투자선)", divider="rainbow")
        st.info("현재 구성 종목만으로 계산한 최대 샤프 포트폴리오와 효율적 투자선을 표시합니다.")
        tickers_tuple = tuple(sorted(portfolio_df['ETF'].tolist()))
        with st.spinner("최적화 계산 중..."):
            opt = run_portfolio_optimization(tickers_tuple, start_5y, today)
        if opt is None:
            st.warning("최적화에 필요한 데이터가 부족합니다(2종목 이상 필요).")
        else:
            results, max_sharpe_perf, optimal_summary = opt
            viz.plot_efficient_frontier(results, max_sharpe_perf, optimal_summary)

def main():
    st.sidebar.title("대시보드 네비게이션")
    pages = {
        "🔬 단일 ETF 심층 분석": etf_analysis_dashboard,
        "💼 ETF 포트폴리오 분석": portfolio_dashboard,
        "💡 개별 티커 재무 정보": financial_info_dashboard,
    }
    choice = st.sidebar.radio("보고 싶은 대시보드를 선택하세요:", list(pages.keys()))
    st.sidebar.divider()
    st.sidebar.info("© 2025 Financial Analysis Dashboard")
    pages[choice]()

if __name__ == "__main__":
    main()