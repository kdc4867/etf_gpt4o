# file: etf_analysis.py
import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import streamlit as st
from typing import Dict, Any, List, Union

RISK_FREE_RATE_ANNUAL = 0.035
TRADING_DAYS_PER_YEAR = 252

FACTOR_TICKERS: Dict[str, str] = {
    "Market": "^GSPC",
    "Size": "IWM",
    "Value": "IWD",
    "Growth": "IWF",
    "Momentum": "MTUM",
    "Quality": "QUAL",
    "Low Volatility": "USMV",
}
MACRO_INDICATORS: Dict[str, str] = {
    "S&P 500": "^GSPC",
    "10Y Treasury": "^TNX",
    "VIX": "^VIX",
    "Gold": "GC=F",
    "Oil": "CL=F",
    "USD Index": "DX-Y.NYB",
    "Real Estate": "VNQ",
}

def _ensure_series(x: Union[pd.Series, pd.DataFrame]) -> pd.Series:
    if isinstance(x, pd.Series):
        return pd.to_numeric(x, errors="coerce").dropna()
    if isinstance(x, pd.DataFrame):
        if x.shape[1] == 0:
            return pd.Series(dtype=float)
        return pd.to_numeric(x.iloc[:, 0], errors="coerce").dropna()
    return pd.Series(dtype=float)

def _extract_price_frame(raw: pd.DataFrame, tickers: List[str]) -> pd.DataFrame:
    """
    yfinance.download 결과에서 가격 프레임을 표준화(컬럼=티커, 값=가격)하여 반환.
    MultiIndex가 (필드, 티커)든 (티커, 필드)든 둘 다 안전 처리.
    """
    if raw.empty:
        return pd.DataFrame()

    def _clean(df: pd.DataFrame) -> pd.DataFrame:
        cols = [t for t in tickers if t in df.columns]
        if not cols:
            cols = list(df.columns)
        out = df[cols].copy()
        out.index = pd.to_datetime(out.index)
        out = out.sort_index().dropna(how="all")
        return out

    if isinstance(raw.columns, pd.MultiIndex):
        lvl0 = raw.columns.get_level_values(0)
        lvlN = raw.columns.get_level_values(-1)
        # 경우 1) (필드, 티커)
        for candidate in ("Adj Close", "Close"):
            if candidate in lvl0:
                df = raw.xs(candidate, axis=1, level=0)
                return _clean(df)
        # 경우 2) (티커, 필드)
        for candidate in ("Adj Close", "Close"):
            if candidate in lvlN:
                df = raw.xs(candidate, axis=1, level=-1)
                return _clean(df)
        return pd.DataFrame()

    # 단일 인덱스 DataFrame
    for candidate in ("Adj Close", "Close"):
        if candidate in raw.columns:
            s = raw[candidate]
            if isinstance(s, pd.DataFrame):
                s = s.iloc[:, 0]
            name = tickers[0] if tickers else "TICKER"
            df = pd.DataFrame({name: s})
            return _clean(df)

    # 최후의 보루: 숫자형 첫 컬럼
    num_cols = [c for c in raw.columns if pd.api.types.is_numeric_dtype(raw[c])]
    if num_cols:
        s = pd.to_numeric(raw[num_cols[0]], errors="coerce")
        name = tickers[0] if tickers else "TICKER"
        df = pd.DataFrame({name: s})
        return _clean(df)

    return pd.DataFrame()


@st.cache_data(ttl=900)
def get_multiple_tickers_data(
    tickers: List[str], start_date, end_date
) -> pd.DataFrame:
    """
    여러 티커의 가격(Adj Close 우선)을 2D DataFrame으로 반환(컬럼=티커).
    group_by를 건드리지 않고(=기본 'column') 어떤 형태로 와도 _extract_price_frame에서 정규화.
    """
    if not tickers:
        return pd.DataFrame()
    try:
        raw = yf.download(
            tickers,
            start=start_date,
            end=end_date,
            progress=False,
            auto_adjust=False,   # 경고 방지 & Adj Close 유지
        )
    except Exception:
        return pd.DataFrame()
    return _extract_price_frame(raw, tickers)

def analyze_etf_basic(data: pd.DataFrame) -> Dict[str, Any]:
    price = None
    if "Close" in data.columns:
        price = _ensure_series(data["Close"])
    elif "Adj Close" in data.columns:
        price = _ensure_series(data["Adj Close"])
    else:
        price = _ensure_series(data)
    if price.empty or float(price.std()) == 0:
        return {"연간 수익률 (%)": "N/A", "연간 변동성 (%)": "N/A", "샤프 비율": "N/A"}
    daily = price.pct_change().dropna()
    ann_ret = daily.mean() * TRADING_DAYS_PER_YEAR
    ann_vol = daily.std() * np.sqrt(TRADING_DAYS_PER_YEAR)
    sharpe = (ann_ret - RISK_FREE_RATE_ANNUAL) / ann_vol if ann_vol != 0 else 0.0
    return {
        "연간 수익률 (%)": f"{ann_ret*100:.2f}",
        "연간 변동성 (%)": f"{ann_vol*100:.2f}",
        "샤프 비율": f"{sharpe:.2f}",
    }

def analyze_risk_and_benchmark(etf_data: pd.DataFrame, benchmark_data: pd.DataFrame) -> Dict[str, float]:
    etf_price = _ensure_series(etf_data["Close"] if "Close" in etf_data.columns else etf_data)
    bench_price = _ensure_series(benchmark_data["Close"] if "Close" in benchmark_data.columns else benchmark_data)
    if etf_price.empty or bench_price.empty:
        return {}
    ret = pd.concat(
        [etf_price.pct_change().rename("etf"), bench_price.pct_change().rename("benchmark")],
        axis=1,
    ).dropna()
    if ret.empty:
        return {}
    cov = ret.cov()
    bench_var = cov.loc["benchmark", "benchmark"]
    beta = cov.loc["etf", "benchmark"] / bench_var if bench_var != 0 else np.nan
    rf_d = RISK_FREE_RATE_ANNUAL / TRADING_DAYS_PER_YEAR
    alpha_d = ret["etf"].mean() - rf_d - beta * (ret["benchmark"].mean() - rf_d)
    alpha_ann = alpha_d * TRADING_DAYS_PER_YEAR
    cum = (1 + ret["etf"]).cumprod()
    mdd = ((cum - cum.cummax()) / cum.cummax()).min()
    te = (ret["etf"] - ret["benchmark"]).std() * np.sqrt(TRADING_DAYS_PER_YEAR)
    return {
        "Beta (베타)": float(beta),
        "Alpha (알파, 연환산 %)": float(alpha_ann * 100),
        "Max Drawdown (최대 낙폭 %)": float(mdd * 100),
        "Tracking Error (추적 오차 %)": float(te * 100),
    }

def analyze_factor_exposure(etf_ticker: str, start_date: str, end_date: str) -> pd.Series:
    all_tickers = [etf_ticker] + list(FACTOR_TICKERS.values())
    prices = get_multiple_tickers_data(all_tickers, start_date, end_date)
    if prices.empty or etf_ticker not in prices.columns:
        st.error(f"'{etf_ticker}' 가격 데이터를 가져올 수 없어 팩터 분석 중단.")
        return pd.Series(dtype=float)
    returns = prices.pct_change().dropna()
    if returns.empty:
        st.warning("수익률 데이터가 비어 있어 팩터 분석 불가.")
    etf_r = returns[etf_ticker]
    rev_map = {v: k for k, v in FACTOR_TICKERS.items()}
    fac_cols = [t for t in FACTOR_TICKERS.values() if t in returns.columns]
    if not fac_cols:
        st.warning("가용한 팩터 데이터가 없습니다.")
        return pd.Series(dtype=float)
    X = returns[fac_cols].rename(columns=rev_map)
    model = LinearRegression()
    model.fit(X, etf_r)
    coef = pd.Series(model.coef_, index=X.columns, name="Factor Exposure").sort_values(ascending=False)
    return coef

def analyze_macro_correlation(etf_ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
    all_tickers = [etf_ticker] + list(MACRO_INDICATORS.values())
    prices = get_multiple_tickers_data(all_tickers, start_date, end_date)
    if prices.empty or etf_ticker not in prices.columns:
        st.error(f"'{etf_ticker}' 가격 데이터를 가져올 수 없어 매크로 분석 중단.")
        return pd.DataFrame()
    rets = prices.pct_change().dropna()
    if rets.empty:
        return pd.DataFrame()
    rev_map = {v: k for k, v in MACRO_INDICATORS.items()}
    renamed = rets.rename(columns=rev_map)
    return renamed.corr()

@st.cache_data(ttl=900)
def compare_etfs(etf_tickers: List[str], start_date: str, end_date: str) -> pd.DataFrame:
    if not etf_tickers:
        return pd.DataFrame()
    prices = get_multiple_tickers_data(etf_tickers, start_date, end_date)
    if prices.empty:
        return pd.DataFrame()
    rets = prices.pct_change().dropna()
    if rets.empty:
        return pd.DataFrame()
    ann_ret = rets.mean() * TRADING_DAYS_PER_YEAR
    ann_vol = rets.std() * np.sqrt(TRADING_DAYS_PER_YEAR)
    sharpe = (ann_ret - RISK_FREE_RATE_ANNUAL) / ann_vol.replace(0, np.nan)
    cum = (1 + rets).cumprod()
    peak = cum.cummax()
    mdd = ((cum - peak) / peak).min()

    rows = []
    for t in rets.columns:
        rows.append({
            "ETF": t,
            "연간 수익률 (%)": float(ann_ret.get(t, np.nan) * 100),
            "연간 변동성 (%)": float(ann_vol.get(t, np.nan) * 100),
            "샤프 비율": float(sharpe.get(t, np.nan)),
            "최대 낙폭 (%)": float(mdd.get(t, np.nan) * 100),
        })
    return pd.DataFrame(rows)