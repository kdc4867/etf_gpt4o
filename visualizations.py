# file: visualizations.py
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from typing import Dict, Tuple

def _pick_price(df: pd.DataFrame, ticker: str | None = None) -> pd.Series | None:
    if df is None or df.empty:
        return None

    # 1) MultiIndex 컬럼(예: ('Close', 'SPY')) 대비
    if isinstance(df.columns, pd.MultiIndex):
        for candidate in ("Adj Close", "Close"):
            if candidate in df.columns.get_level_values(0):
                s = df.xs(candidate, axis=1, level=0)  # 남는 건 (티커) 컬럼들
                # 특정 티커가 있으면 그 컬럼 우선, 없으면 첫 컬럼
                if isinstance(s, pd.DataFrame):
                    if ticker and ticker in s.columns:
                        s = s[ticker]
                    else:
                        s = s.iloc[:, 0]
                s = pd.to_numeric(s, errors="coerce").dropna()
                return s if not s.empty else None

    # 2) 일반 단일 컬럼 구조 대비
    for candidate in ("Adj Close", "Close"):
        if candidate in df.columns:
            s = df[candidate]
            # 혹시라도 DataFrame이면 첫 컬럼으로 축소
            if isinstance(s, pd.DataFrame):
                s = s.iloc[:, 0]
            s = pd.to_numeric(s, errors="coerce").dropna()
            return s if not s.empty else None

    # 3) 마지막 안전장치: 숫자형 첫 컬럼
    num_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
    if num_cols:
        s = pd.to_numeric(df[num_cols[0]], errors="coerce").dropna()
        return s if not s.empty else None

    return None

def plot_price_chart(data: pd.DataFrame, ticker: str):
    """ETF/주가 추이 + 20/60일 이동평균."""
    s = _pick_price(data, ticker)
    if s is None or s.empty:
        st.warning("가격 추이 데이터를 표시할 수 없습니다.")
        return
    s.index = pd.to_datetime(s.index)
    df = pd.DataFrame({"Close": s})
    df["MA20"] = df["Close"].rolling(20).mean()
    df["MA60"] = df["Close"].rolling(60).mean()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["Close"], mode="lines", name="종가"))
    fig.add_trace(go.Scatter(x=df.index, y=df["MA20"], mode="lines", name="20일", line=dict(dash="dot")))
    fig.add_trace(go.Scatter(x=df.index, y=df["MA60"], mode="lines", name="60일", line=dict(dash="dash")))
    fig.update_layout(title=f"{ticker} 가격 추이", xaxis_title="날짜", yaxis_title="가격",
                      legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    st.plotly_chart(fig, use_container_width=True)

def plot_risk_metrics(risk_metrics: Dict[str, float]):
    if not risk_metrics:
        st.info("리스크 데이터가 없습니다.")
        return
    labels = list(risk_metrics.keys())
    values = [risk_metrics[k] for k in labels]
    fig = go.Figure(data=[go.Bar(x=labels, y=values, text=[f"{v:.2f}" for v in values], textposition="auto")])
    fig.update_layout(title="주요 리스크 지표", xaxis_title="지표", yaxis_title="값")
    st.plotly_chart(fig, use_container_width=True)

def plot_factor_exposure(factor_exposure: pd.Series):
    if factor_exposure is None or factor_exposure.empty:
        st.info("표시할 팩터 노출도 데이터가 없습니다.")
        return
    fig = go.Figure(data=[go.Bar(y=factor_exposure.index.tolist(), x=factor_exposure.values.tolist(), orientation="h")])
    fig.update_layout(title="팩터 노출도", xaxis_title="회귀 계수", yaxis_title="팩터")
    st.plotly_chart(fig, use_container_width=True)

def plot_etf_comparison(df: pd.DataFrame, metric: str):
    if df.empty or metric not in df.columns:
        st.info("비교할 데이터가 없습니다.")
        return
    fig = go.Figure(data=[go.Bar(x=df["ETF"], y=df[metric],
                                 text=df[metric].apply(lambda x: f"{x:.2f}"), textposition="auto")])
    fig.update_layout(title=f"ETF 비교: {metric}", xaxis_title="ETF", yaxis_title=metric)
    st.plotly_chart(fig, use_container_width=True)

def plot_macro_correlation(corr: pd.DataFrame, ticker: str):
    if corr.empty:
        st.info("상관관계 데이터가 없어 표시할 수 없습니다.")
        return
    fig = go.Figure(data=go.Heatmap(z=corr.values, x=corr.columns, y=corr.index, colorscale="RdBu", zmid=0))
    fig.update_layout(title=f"{ticker} vs 거시 지표 상관관계(피어슨)")
    st.plotly_chart(fig, use_container_width=True)

def plot_cumulative_returns(portfolio_returns: pd.Series):
    if portfolio_returns is None or portfolio_returns.empty:
        st.info("포트폴리오 수익률이 없습니다.")
        return
    cum = (1 + portfolio_returns).cumprod()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=cum.index, y=cum.values, mode="lines", name="포트폴리오"))
    fig.update_layout(title="포트폴리오 누적 수익률", xaxis_title="날짜", yaxis_title="지수(초기=1)")
    st.plotly_chart(fig, use_container_width=True)

def plot_asset_allocation(portfolio_df: pd.DataFrame):
    if portfolio_df.empty or "ETF" not in portfolio_df or "Weight" not in portfolio_df:
        st.info("자산 배분 데이터가 없습니다.")
        return
    labels = portfolio_df["ETF"].tolist()
    values = portfolio_df["Weight"].tolist()
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.35)])
    fig.update_layout(title="자산 배분")
    st.plotly_chart(fig, use_container_width=True)

def plot_efficient_frontier(results: np.ndarray, max_sharpe_perf: Tuple[float, float], optimal_summary: pd.DataFrame):
    """results: (3 x N) [vol, ret, sharpe], max_sharpe_perf: (return, volatility)"""
    if results.size == 0:
        st.info("최적화 결과 없음")
        return
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=results[0, :], y=results[1, :],
        mode="markers",
        marker=dict(size=5, color=results[2, :], colorscale="Viridis", showscale=True),
        name="무작위 포트폴리오"
    ))
    fig.add_trace(go.Scatter(
        x=[max_sharpe_perf[1]], y=[max_sharpe_perf[0]],
        mode="markers", marker=dict(size=16, color="red", symbol="star"),
        name="최대 샤프 포트폴리오"
    ))
    fig.update_layout(title="효율적 프론티어", xaxis_title="변동성(연율)", yaxis_title="수익률(연율)")
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("최적 포트폴리오 가중치 보기"):
        st.dataframe(optimal_summary.style.format("{:.2%}"))