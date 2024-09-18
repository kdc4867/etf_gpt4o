import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np

def plot_price_performance(data, ticker):
    """ETF의 가격 성과를 시각화합니다."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data.index, y=data['Adj Close'], mode='lines', name=ticker))
    fig.update_layout(title=f"{ticker} 가격 성과", xaxis_title="날짜", yaxis_title="가격")
    st.plotly_chart(fig, use_container_width=True, renderer="svg")

def plot_risk_metrics(risk_metrics, ticker, benchmark_ticker):
    """리스크 메트릭스를 바 차트로 시각화합니다."""
    fig = go.Figure(data=[go.Bar(x=list(risk_metrics.keys()), y=list(risk_metrics.values()))])
    fig.update_layout(title=f"{ticker} vs {benchmark_ticker} 리스크 메트릭스", xaxis_title="메트릭", yaxis_title="값")
    st.plotly_chart(fig, use_container_width=True, renderer="svg")

def plot_factor_exposure(factor_exposure):
    """팩터 노출도를 바 차트로 시각화합니다."""
    fig = go.Figure(data=[go.Bar(x=factor_exposure.index, y=factor_exposure.values)])
    fig.update_layout(title='팩터 노출도', xaxis_title='팩터', yaxis_title='노출도')
    st.plotly_chart(fig, use_container_width=True, renderer="svg")

def plot_etf_comparison(comparison_data):
    """ETF 비교 데이터를 바 차트로 시각화합니다."""
    fig = go.Figure()
    for column in ['Annual Return', 'Sharpe Ratio', 'Max Drawdown']:
        fig.add_trace(go.Bar(x=comparison_data['ETF'], y=comparison_data[column], name=column))
    fig.update_layout(barmode='group', title="ETF 성과 비교")
    st.plotly_chart(fig, use_container_width=True, renderer="svg")

def plot_macro_correlation(correlation_data, ticker):
    """매크로 상관관계를 히트맵으로 시각화합니다."""
    fig = go.Figure(data=go.Heatmap(
        z=correlation_data.values,
        x=correlation_data.columns,
        y=correlation_data.index,
        colorscale='RdBu_r'
    ))
    fig.update_layout(title=f'{ticker}와 매크로 지표 간 상관관계')
    st.plotly_chart(fig, use_container_width=True, renderer="svg")

def plot_portfolio_summary(portfolio_data, performance_metrics):
    """포트폴리오 개요를 시각화합니다."""
    cumulative_returns = performance_metrics['Cumulative Returns']
    fig = go.Figure(data=go.Scatter(x=cumulative_returns.index, y=cumulative_returns.values, mode='lines'))
    fig.update_layout(title='누적 수익률', xaxis_title="날짜", yaxis_title="누적 수익률")
    st.plotly_chart(fig, use_container_width=True, renderer="svg")
    
    st.write("포트폴리오 성과 지표:")
    st.write(f"연간 수익률: {performance_metrics['Annual Return']*100:.2f}%")
    st.write(f"연간 변동성: {performance_metrics['Annual Volatility']*100:.2f}%")
    st.write(f"샤프 비율: {performance_metrics['Sharpe Ratio']:.2f}")

def plot_cumulative_returns(portfolio_data):
    """포트폴리오의 누적 수익률을 시각화합니다."""
    returns = pd.DataFrame({etf: data['returns'] for etf, data in portfolio_data.items()})
    cumulative_returns = (1 + returns).cumprod()
    
    fig = go.Figure()
    for column in cumulative_returns.columns:
        fig.add_trace(go.Scatter(x=cumulative_returns.index, y=cumulative_returns[column], mode='lines', name=column))
    fig.update_layout(title='누적 수익률', xaxis_title="날짜", yaxis_title="누적 수익률")
    st.plotly_chart(fig, use_container_width=True, renderer="svg")

def plot_asset_allocation(asset_allocation):
    """자산 배분을 파이 차트로 시각화합니다."""
    fig = go.Figure(data=[go.Pie(labels=list(asset_allocation.keys()), values=list(asset_allocation.values()))])
    fig.update_layout(title='자산 배분')
    st.plotly_chart(fig, use_container_width=True, renderer="svg")

def plot_efficient_frontier(results, optimal_portfolio):
    """효율적 프론티어와 최적 포트폴리오를 시각화합니다."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=results[0,:],
        y=results[1,:],
        mode='markers',
        marker=dict(
            size=5,
            color=results[2,:],
            colorscale='Viridis',
            showscale=True
        ),
        name='포트폴리오'
    ))
    
    optimal_return = optimal_portfolio.fun * -1
    optimal_volatility = results[0, np.argmax(results[2])]
    fig.add_trace(go.Scatter(
        x=[optimal_volatility],
        y=[optimal_return],
        mode='markers',
        marker=dict(size=15, color='red', symbol='star'),
        name='최적 포트폴리오'
    ))
    
    fig.update_layout(title='효율적 프론티어', xaxis_title='변동성', yaxis_title='수익률')
    st.plotly_chart(fig, use_container_width=True, renderer="svg")

def display_performance_metrics(performance_metrics):
    """성과 지표를 표시합니다."""
    st.write("성과 지표:")
    st.write(f"연간 수익률: {performance_metrics['Annual Return']*100:.2f}%")
    st.write(f"연간 변동성: {performance_metrics['Annual Volatility']*100:.2f}%")
    st.write(f"샤프 비율: {performance_metrics['Sharpe Ratio']:.2f}")

def display_risk_metrics(risk_metrics):
    """리스크 지표를 표시합니다."""
    st.write("리스크 지표:")
    st.write(f"베타: {risk_metrics['Beta']:.4f}")
    st.write(f"알파: {risk_metrics['Alpha']*100:.2f}%")
    st.write(f"최대 낙폭: {risk_metrics['Max Drawdown']*100:.2f}%")
    st.write(f"Value at Risk (95%): {risk_metrics['Value at Risk (95%)']*100:.2f}%")