import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

def plot_price_performance(data, ticker):
    """ETF의 가격 성과를 시각화합니다."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data.index, y=data['Adj Close'], mode='lines', name=ticker))
    fig.update_layout(title=f"{ticker} 가격 성과", xaxis_title="날짜", yaxis_title="가격")
    st.plotly_chart(fig)

def plot_risk_metrics(risk_metrics, ticker, benchmark_ticker):
    """리스크 메트릭스를 레이더 차트로 시각화합니다."""
    categories = ['Beta', 'Alpha', 'Sharpe Ratio', 'Max Drawdown', 'Volatility']
    r = [risk_metrics.get(cat, 0) for cat in categories]

    fig = go.Figure(data=go.Scatterpolar(
      r=r,
      theta=categories,
      fill='toself'
    ))

    fig.update_layout(
      polar=dict(
        radialaxis=dict(
          visible=True,
          range=[0, max(r)]
        )),
      showlegend=False,
      title=f"{ticker} vs {benchmark_ticker} 리스크 메트릭스"
    )
    st.plotly_chart(fig)

def plot_factor_exposure(factor_exposure):
    """팩터 노출도를 시각화합니다."""
    fig = go.Figure(go.Bar(
        x=factor_exposure.index,
        y=factor_exposure.values,
        marker_color='lightblue'
    ))
    fig.update_layout(
        title='팩터 노출도',
        xaxis_title='팩터',
        yaxis_title='노출도',
        template='plotly_white'
    )
    st.plotly_chart(fig)

def plot_etf_comparison(comparison_data):
    """ETF 비교 데이터를 시각화합니다."""
    fig = px.bar(comparison_data, x='ETF', y=['Annual Return', 'Sharpe Ratio', 'Max Drawdown'], 
                 barmode='group', title="ETF 성과 비교")
    fig.update_layout(template="plotly_white")
    st.plotly_chart(fig)

def plot_macro_correlation(correlation_data, ticker):
    """매크로 상관관계를 히트맵으로 시각화합니다."""
    fig = px.imshow(correlation_data, text_auto=True, aspect="auto", color_continuous_scale='RdBu_r')
    fig.update_layout(title=f'{ticker}와 매크로 지표 간 상관관계', width=800, height=600)
    st.plotly_chart(fig)

def plot_gpt_analysis(gpt_analysis):
    """GPT 분석 결과를 시각화합니다."""
    st.write(gpt_analysis)  # 간단히 텍스트로 표시

def plot_portfolio_summary(portfolio_data, performance_metrics):
    """포트폴리오 개요를 시각화합니다."""
    fig = go.Figure()
    
    # 누적 수익률 차트
    cumulative_returns = performance_metrics['Cumulative Returns']
    fig.add_trace(go.Scatter(x=cumulative_returns.index, y=cumulative_returns.values,
                             mode='lines', name='Cumulative Returns'))
    
    # 성과 지표
    metrics = {
        'Annual Return': f"{performance_metrics['Annual Return']*100:.2f}%",
        'Annual Volatility': f"{performance_metrics['Annual Volatility']*100:.2f}%",
        'Sharpe Ratio': f"{performance_metrics['Sharpe Ratio']:.2f}"
    }
    
    table = go.Table(
        header=dict(values=['Metric', 'Value'],
                    fill_color='paleturquoise',
                    align='left'),
        cells=dict(values=[list(metrics.keys()), list(metrics.values())],
                   fill_color='lavender',
                   align='left')
    )
    
    fig.add_trace(table)
    
    fig.update_layout(title='Portfolio Summary', height=600)
    st.plotly_chart(fig)

def plot_cumulative_returns(portfolio_data):
    """포트폴리오의 누적 수익률을 시각화합니다."""
    returns = pd.DataFrame({etf: data['returns'] for etf, data in portfolio_data.items()})
    cumulative_returns = (1 + returns).cumprod()
    
    fig = px.line(cumulative_returns, title='Cumulative Returns')
    fig.update_layout(yaxis_title='Cumulative Returns', xaxis_title='Date')
    st.plotly_chart(fig)

def plot_asset_allocation(asset_allocation):
    """자산 배분을 파이 차트로 시각화합니다."""
    fig = px.pie(values=list(asset_allocation.values()), names=list(asset_allocation.keys()),
                 title='Asset Allocation')
    st.plotly_chart(fig)

def plot_efficient_frontier(results, optimal_portfolio):
    """효율적 프론티어와 최적 포트폴리오를 시각화합니다."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=results[0,:], y=results[1,:], mode='markers',
                             marker=dict(size=5, color=results[2,:], colorscale='Viridis', showscale=True),
                             name='Portfolios'))
    
    optimal_return = optimal_portfolio.fun * -1
    optimal_volatility = results[0, np.argmax(results[2])]
    fig.add_trace(go.Scatter(x=[optimal_volatility], y=[optimal_return], mode='markers',
                             marker=dict(size=15, color='red', symbol='star'),
                             name='Optimal Portfolio'))
    
    fig.update_layout(title='Efficient Frontier',
                      xaxis_title='Volatility',
                      yaxis_title='Return',
                      showlegend=True)
    
    st.plotly_chart(fig)