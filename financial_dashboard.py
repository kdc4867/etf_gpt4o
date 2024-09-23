import yfinance as yf
import streamlit as st

def load_ticker_data(ticker):
    """주어진 티커에 대한 재무 정보를 가져옵니다."""
    try:
        ticker_data = yf.Ticker(ticker).info
        return ticker_data
    except Exception as e:
        st.error(f"{ticker} 데이터를 불러오는 중 오류가 발생했습니다: {str(e)}")
        return None

def format_large_numbers(value):
    """큰 수치를 억 단위로 변환하고 소수점 2자리로 반올림합니다."""
    if isinstance(value, (int, float)):
        if value >= 1e8:
            return f"{value / 1e8:.2f}억"
        else:
            return f"{value:,.2f}"
    return "N/A"

def format_percentage(value):
    """백분율로 표현할 값들을 2자리 반올림하여 처리합니다."""
    if isinstance(value, (int, float)):
        return f"{round(value * 100, 2)}%"
    return "N/A"

def display_financial_info(ticker_data):
    """티커의 재무 정보를 시각화합니다."""
    if ticker_data:
        st.subheader(f"{ticker_data.get('longName', '회사 이름 없음')} ({ticker_data.get('symbol', 'N/A')})")

        st.markdown(f"**산업:** {ticker_data.get('industry', 'N/A')}")
        st.markdown(f"**부문:** {ticker_data.get('sector', 'N/A')}")
        st.markdown(f"**직원 수:** {format_large_numbers(ticker_data.get('fullTimeEmployees', 'N/A'))}")

        st.write("---")
        st.subheader("주요 재무 정보")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("시가총액", format_large_numbers(ticker_data.get('marketCap', 'N/A')))
            st.metric("총 현금", format_large_numbers(ticker_data.get('totalCash', 'N/A')))
            st.metric("부채 비율", format_percentage(ticker_data.get('debtToEquity', 'N/A')))

        with col2:
            st.metric("총 매출", format_large_numbers(ticker_data.get('totalRevenue', 'N/A')))
            st.metric("EBITDA", format_large_numbers(ticker_data.get('ebitda', 'N/A')))
            st.metric("현금 흐름", format_large_numbers(ticker_data.get('operatingCashflow', 'N/A')))

        with col3:
            st.metric("주가 수익 비율(P/E)", f"{ticker_data.get('trailingPE', 'N/A'):.2f}" if ticker_data.get('trailingPE') else "N/A")
            st.metric("주가 대비 장부가(P/B)", f"{ticker_data.get('priceToBook', 'N/A'):.2f}" if ticker_data.get('priceToBook') else "N/A")
            st.metric("배당률", format_percentage(ticker_data.get('dividendYield', 0)))

        st.write("---")
        st.subheader("기타 정보")
        st.markdown(f"**웹사이트:** [여기 클릭]({ticker_data.get('website', '#')})")
        st.markdown(f"**본사:** {ticker_data.get('address1', 'N/A')}, {ticker_data.get('city', 'N/A')}, {ticker_data.get('state', 'N/A')}")
    else:
        st.error("재무 데이터를 표시할 수 없습니다.")
