import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import streamlit as st

def analyze_etf(data, ticker):
    daily_returns = data['Adj Close'].pct_change()
    annualized_return = (daily_returns.mean() * 252) * 100
    annualized_volatility = (daily_returns.std() * np.sqrt(252)) * 100
    risk_free_rate = 2.0  # 예시로 2% 사용
    sharpe_ratio = (annualized_return - risk_free_rate) / annualized_volatility
    
    etf = yf.Ticker(ticker)
    #경비 비율 제거
    etf_info = {
        "연간 수익률": f"{annualized_return:.2f}%",
        "연간 변동성": f"{annualized_volatility:.2f}%",
        "샤프 비율": f"{sharpe_ratio:.2f}",
    }
    
    return etf_info

def analyze_risk_and_benchmark(etf_data, benchmark_data, etf_ticker, benchmark_ticker):
    etf_returns = etf_data['Close'].pct_change()
    benchmark_returns = benchmark_data['Close'].pct_change()
    
    covariance = etf_returns.cov(benchmark_returns)
    variance = benchmark_returns.var()
    beta = covariance / variance
    
    cum_returns = (1 + etf_returns).cumprod()
    running_max = cum_returns.cummax()
    drawdown = (cum_returns - running_max) / running_max
    max_drawdown = drawdown.min()
    
    tracking_error = (etf_returns - benchmark_returns).std() * np.sqrt(252)
    
    risk_free_rate = 0.02 / 252  # 일일 무위험 수익률 (예: 2% 연간)
    etf_excess_return = etf_returns - risk_free_rate
    benchmark_excess_return = benchmark_returns - risk_free_rate
    alpha = etf_excess_return.mean() - (beta * benchmark_excess_return.mean())
    alpha = alpha * 252  # 연간화
    
    sharpe_ratio = (etf_returns.mean() - risk_free_rate) / etf_returns.std() * np.sqrt(252)
    
    risk_metrics = {
        "Beta": beta,
        "Alpha": alpha,
        "Sharpe Ratio": sharpe_ratio,
        "Max Drawdown": max_drawdown,
        "Volatility": etf_returns.std() * np.sqrt(252)
    }
    
    return risk_metrics

def analyze_factor_exposure(etf_ticker, start_date, end_date):
    try:
        etf_data = yf.download(etf_ticker, start=start_date, end=end_date)
        if etf_data.empty:
            st.error(f"{etf_ticker}에 대한 데이터를 찾을 수 없습니다.")
            return pd.Series()
        
        etf_returns = etf_data['Close'].pct_change().dropna()

        # 팩터 티커
        factor_tickers = {
            'Market': '^GSPC',
            'Size': 'IWM',
            'Value': 'IWD',
            'Growth': 'IWF',
            'Momentum': 'MTUM',
            'Quality': 'QUAL',
            'Low Volatility': 'USMV',
            'Dividend': 'DVY',
            'High Yield': 'HYG',
            'International': 'EFA',
            'Emerging Markets': 'EEM'
        }

        factor_data = pd.DataFrame()
        for factor, ticker in factor_tickers.items():
            try:
                factor_data_temp = yf.download(ticker, start=start_date, end=end_date)
                if not factor_data_temp.empty:
                    factor_returns = factor_data_temp['Close'].pct_change().dropna()
                    factor_data[factor] = factor_returns
                else:
                    st.warning(f"{factor} ({ticker})에 대한 데이터를 찾을 수 없습니다.")
            except Exception as e:
                st.warning(f"{factor} ({ticker}) 데이터 다운로드 중 오류 발생: {str(e)}")

        # 팩터 데이터가 비어있을 경우
        if factor_data.empty:
            st.error("팩터 데이터를 가져올 수 없습니다.")
            return pd.Series()

        # ETF와 팩터 데이터를 정렬 및 병합
        aligned_data = pd.concat([etf_returns.rename('ETF'), factor_data], axis=1).dropna()
        if aligned_data.empty:
            st.error("정렬된 데이터가 없습니다.")
            return pd.Series()

        # 독립 변수(X)와 종속 변수(y) 정의
        X = aligned_data[factor_tickers.keys()]
        y = aligned_data['ETF']

        # 회귀 분석 수행
        if len(X) == 0 or len(y) == 0:
            st.error("분석에 필요한 데이터가 충분하지 않습니다.")
            return pd.Series()

        model = LinearRegression()
        model.fit(X, y)
        
        # 팩터 노출도 반환
        factor_exposure = pd.Series(model.coef_, index=X.columns)
        return factor_exposure

    except Exception as e:
        st.error(f"팩터 노출도 분석 중 오류 발생: {str(e)}")
        return pd.Series()


def compare_etfs(etf_tickers, start_date, end_date):
    if not etf_tickers:
        st.error("비교할 ETF를 선택해 주세요.")
        return pd.DataFrame()

    comparison_data = []
    
    for ticker in etf_tickers:
        etf = yf.Ticker(ticker)
        hist_data = etf.history(start=start_date, end=end_date)
        
        if hist_data.empty:
            st.warning(f"{ticker}에 대한 데이터를 찾을 수 없습니다.")
            continue

        returns = hist_data['Close'].pct_change().dropna()
        annual_return = returns.mean() * 252
        volatility = returns.std() * np.sqrt(252)
        sharpe_ratio = annual_return / volatility
        
        cum_returns = (1 + returns).cumprod()
        running_max = cum_returns.cummax()
        drawdown = (cum_returns - running_max) / running_max
        max_drawdown = drawdown.min()
        
        info = etf.info
        
        comparison_data.append({
            'ETF': ticker,
            'Annual Return': annual_return,
            'Sharpe Ratio': sharpe_ratio,
            'Max Drawdown': max_drawdown,
            'Expense Ratio': info.get('expenseRatio', None),
            'AUM': info.get('totalAssets', None),
            'Yield': info.get('yield', None)
        })
    
    return pd.DataFrame(comparison_data)

def analyze_macro_market_correlation(etf_ticker, start_date, end_date):
    try:
        etf_data = yf.download(etf_ticker, start=start_date, end=end_date)
        if etf_data.empty:
            st.error(f"{etf_ticker}에 대한 데이터를 찾을 수 없습니다.")
            return pd.DataFrame()
        etf_returns = etf_data['Close'].pct_change().dropna()
        
        indicators = {
            'S&P 500': '^GSPC',
            '10Y Treasury Yield': '^TNX',
            'VIX': '^VIX',
            'Gold': 'GC=F',
            'Oil': 'CL=F',
            'USD Index': 'DX-Y.NYB',
            'Inflation Expectation (5Y)': '^FVX',
            'High Yield Bonds': 'HYG',
            'Emerging Markets': 'EEM',
            'Real Estate': 'VNQ',
            'Investment Grade Bonds': 'LQD',
            'Developed Markets': 'EFA',
            'Commodities': 'DBC'
        }
        
        indicator_data = pd.DataFrame()
        for name, ticker in indicators.items():
            try:
                ind_data = yf.download(ticker, start=start_date, end=end_date)
                if not ind_data.empty:
                    indicator_data[name] = ind_data['Close'].pct_change().dropna()
                else:
                    st.warning(f"{name} ({ticker})에 대한 데이터를 찾을 수 없습니다.")
            except Exception as e:
                st.warning(f"{name} ({ticker}) 데이터 다운로드 중 오류 발생: {str(e)}")
        
        if indicator_data.empty:
            st.error("지표 데이터를 가져올 수 없습니다.")
            return pd.DataFrame()
        
        all_data = pd.concat([etf_returns.rename(etf_ticker), indicator_data], axis=1).dropna()
        if all_data.empty:
            st.error("분석에 필요한 데이터가 충분하지 않습니다.")
            return pd.DataFrame()
        
        correlation = all_data.corr()
        
        return correlation

    except Exception as e:
        st.error(f"매크로 및 마켓 상황 연관성 분석 중 오류 발생: {str(e)}")
        return pd.DataFrame()