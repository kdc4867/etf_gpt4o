import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import streamlit as st
from visualizations import plot_price_performance, plot_factor_exposure, plot_correlation_heatmap, plot_investment_style

def analyze_etf(data, ticker):
    daily_returns = data['Adj Close'].pct_change()
    annualized_return = (daily_returns.mean() * 252) * 100
    annualized_volatility = (daily_returns.std() * np.sqrt(252)) * 100
    risk_free_rate = 2.0  # 예시로 2% 사용
    sharpe_ratio = (annualized_return - risk_free_rate) / annualized_volatility
    
    etf = yf.Ticker(ticker)
    expense_ratio = etf.info.get('expenseRatio', 'N/A')
    
    st.write(f"연간 수익률: {annualized_return:.2f}%")
    st.write(f"연간 변동성: {annualized_volatility:.2f}%")
    st.write(f"샤프 비율: {sharpe_ratio:.2f}")
    st.write(f"경비 비율: {expense_ratio}")

    plot_price_performance(data, ticker)

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
    
    st.write(f"변동성 (연간): {etf_returns.std() * np.sqrt(252):.4f}")
    st.write(f"베타: {beta:.4f}")
    st.write(f"최대 낙폭: {max_drawdown:.4f}")
    st.write(f"추적 오차 (연간): {tracking_error:.4f}")
    st.write(f"알파 (연간): {alpha:.4f}")

def analyze_factor_exposure(etf_ticker, start_date, end_date):
    try:
        etf_data = yf.download(etf_ticker, start=start_date, end=end_date)
        if etf_data.empty:
            st.error(f"{etf_ticker}에 대한 데이터를 찾을 수 없습니다.")
            return
        etf_returns = etf_data['Close'].pct_change().dropna()

        factor_tickers = {
            'Market': '^GSPC',  # S&P 500 (시장)
            'Size': 'IWM',      # Russell 2000 (소형주)
            'Value': 'IWD',     # Russell 1000 Value (가치주)
            'Growth': 'IWF',    # Russell 1000 Growth (성장주)
            'Momentum': 'MTUM'  # iShares MSCI USA Momentum Factor ETF
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

        if factor_data.empty:
            st.error("팩터 데이터를 가져올 수 없습니다.")
            return

        aligned_data = pd.concat([etf_returns, factor_data], axis=1).dropna()
        if aligned_data.empty:
            st.error("정렬된 데이터가 없습니다.")
            return

        X = aligned_data[list(factor_tickers.keys())]
        y = aligned_data['Close']

        if len(X) == 0 or len(y) == 0:
            st.error("분석에 필요한 데이터가 충분하지 않습니다.")
            return

        model = LinearRegression()
        model.fit(X, y)
        
        factor_exposure = pd.Series(model.coef_, index=X.columns)
        r_squared = model.score(X, y)
        
        st.write("팩터 노출도:")
        st.write(factor_exposure)
        st.write(f"\nR-squared: {r_squared:.4f}")
        
        plot_factor_exposure(factor_exposure)

        style = interpret_style(factor_exposure)
        st.write(f"\n투자 스타일: {style}")
        plot_investment_style(style)  # 스타일 시각화 함수 호출
    except Exception as e:
        st.error(f"팩터 노출도 분석 중 오류 발생: {str(e)}")

def interpret_style(factor_exposure):
    style = []
    if factor_exposure['Market'] > 0.8:
        style.append("시장 추종형")
    if factor_exposure['Size'] > 0:
        style.append("소형주 편향")
    elif factor_exposure['Size'] < 0:
        style.append("대형주 편향")
    if factor_exposure['Value'] > factor_exposure['Growth']:
        style.append("가치 중심")
    elif factor_exposure['Growth'] > factor_exposure['Value']:
        style.append("성장 중심")
    if factor_exposure['Momentum'] > 0.1:
        style.append("모멘텀 전략")
    
    return ", ".join(style) if style else "중립적"

def compare_etfs(etf_tickers, start_date, end_date):
    if not etf_tickers:
        st.error("비교할 ETF를 선택해 주세요.")
        return

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
            'Ticker': ticker,
            'Name': info.get('longName', 'N/A'),
            'Annual Return': annual_return,
            'Volatility': volatility,
            'Sharpe Ratio': sharpe_ratio,
            'Max Drawdown': max_drawdown,
            'Expense Ratio': info.get('expenseRatio', None),
            'AUM': info.get('totalAssets', None),
            'Yield': info.get('yield', None)
        })
    
    if not comparison_data:
        st.error("유효한 ETF 데이터를 찾을 수 없습니다.")
        return
    
    comparison_df = pd.DataFrame(comparison_data).set_index('Ticker')
    comparison_df = comparison_df.sort_values('Sharpe Ratio', ascending=False)
    
    styled_df = comparison_df.style.format({
        'Name': lambda x: x,
        'Annual Return': lambda x: f'{x:.2%}' if pd.notnull(x) else 'N/A',
        'Volatility': lambda x: f'{x:.2%}' if pd.notnull(x) else 'N/A',
        'Sharpe Ratio': lambda x: f'{x:.2f}' if pd.notnull(x) else 'N/A',
        'Max Drawdown': lambda x: f'{x:.2%}' if pd.notnull(x) else 'N/A',
        'Expense Ratio': lambda x: f'{x:.2%}' if pd.notnull(x) else 'N/A',
        'AUM': lambda x: f'${x:,.0f}' if pd.notnull(x) else 'N/A',
        'Yield': lambda x: f'{x:.2%}' if pd.notnull(x) else 'N/A'
    })

    st.dataframe(styled_df)

def analyze_macro_market_correlation(etf_ticker, start_date, end_date):
    try:
        etf_data = yf.download(etf_ticker, start=start_date, end=end_date, interval='1d')
        if etf_data.empty:
            st.error(f"{etf_ticker}에 대한 데이터를 찾을 수 없습니다.")
            return
        etf_returns = etf_data['Close'].pct_change().dropna()
        
        indicators = {
            'S&P 500': '^GSPC',
            '10Y Treasury Yield': '^TNX',
            'VIX': '^VIX',
            'Gold': 'GC=F',
            'Oil': 'CL=F',
            'USD Index': 'DX-Y.NYB'
        }
        
        indicator_data = pd.DataFrame()
        for name, ticker in indicators.items():
            try:
                ind_data = yf.download(ticker, start=start_date, end=end_date, interval='1d')
                if not ind_data.empty:
                    indicator_data[name] = ind_data['Close'].pct_change().dropna()
                else:
                    st.warning(f"{name} ({ticker})에 대한 데이터를 찾을 수 없습니다.")
            except Exception as e:
                st.warning(f"{name} ({ticker}) 데이터 다운로드 중 오류 발생: {str(e)}")
        
        if indicator_data.empty:
            st.error("지표 데이터를 가져올 수 없습니다.")
            return
        
        all_data = pd.concat([etf_returns.rename(etf_ticker), indicator_data], axis=1).dropna()
        if all_data.empty:
            st.error("분석에 필요한 데이터가 충분하지 않습니다.")
            return
        
        correlation = all_data.corr()
        
        plot_correlation_heatmap(correlation, etf_ticker)
        
        etf_correlation = correlation[etf_ticker].sort_values(ascending=False)
        st.write(f"\n{etf_ticker}와 각 지표간의 상관관계:")
        st.write(etf_correlation)
    except Exception as e:
        st.error(f"매크로 및 마켓 상황 연관성 분석 중 오류 발생: {str(e)}")
