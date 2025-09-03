# file: portfolio_analysis.py
import numpy as np
import pandas as pd
import yfinance as yf
from scipy.optimize import minimize
from typing import List, Tuple, Dict, Optional

TRADING_DAYS = 252
RISK_FREE_ANNUAL = 0.02
RISK_FREE_DAILY = RISK_FREE_ANNUAL / TRADING_DAYS
MARKET_BENCH = "^GSPC"

def _extract_price(df: pd.DataFrame, price_col_priority=("Adj Close", "Close")) -> pd.Series:
    if df.empty:
        return pd.Series(dtype=float)
    if isinstance(df.columns, pd.MultiIndex):
        lvl = df.columns.get_level_values(-1)
        for col in price_col_priority:
            if col in lvl:
                s = df.xs(col, axis=1, level=-1)
                if isinstance(s, pd.DataFrame):
                    s = s.iloc[:, 0]
                return pd.to_numeric(s, errors="coerce").dropna()
    else:
        for col in price_col_priority:
            if col in df.columns:
                return pd.to_numeric(df[col], errors="coerce").dropna()
    num_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
    if num_cols:
        return pd.to_numeric(df[num_cols[0]], errors="coerce").dropna()
    return pd.Series(dtype=float)

def load_price_series(ticker: str, start: pd.Timestamp, end: pd.Timestamp) -> pd.Series:
    df = yf.download(ticker, start=start, end=end, progress=False, actions=False, group_by="ticker")
    s = _extract_price(df)
    s.name = ticker
    return s

def build_returns_matrix(tickers: List[str], start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
    series_list = []
    for t in tickers:
        px = load_price_series(t, start, end)
        if px.empty:
            continue
        series_list.append(px.pct_change().dropna().rename(t))
    if not series_list:
        return pd.DataFrame()
    R = pd.concat(series_list, axis=1).dropna(how="all")
    R = R.dropna(axis=1, how="all")
    return R

def calculate_portfolio_performance(portfolio_df: pd.DataFrame, start_date: pd.Timestamp, end_date: pd.Timestamp) -> Dict[str, any]:
    """
    portfolio_df: ['ETF','Weight'] with Weight in 0~1
    return: {'daily_returns', 'Annual Return', 'Annual Volatility', 'Sharpe Ratio'}
    """
    tickers = [t.strip().upper() for t in portfolio_df["ETF"].tolist() if isinstance(t, str)]
    if not tickers:
        return {"daily_returns": pd.Series(dtype=float), "Annual Return": 0.0, "Annual Volatility": 0.0, "Sharpe Ratio": 0.0}

    R = build_returns_matrix(tickers, start_date, end_date)
    if R.empty:
        return {"daily_returns": pd.Series(dtype=float), "Annual Return": 0.0, "Annual Volatility": 0.0, "Sharpe Ratio": 0.0}

    w = (portfolio_df.set_index("ETF")["Weight"].reindex(R.columns).fillna(0.0).astype(float))
    s = w.sum()
    if s > 0:
        w = w / s

    port = (R * w).sum(axis=1).dropna()
    ann_ret = port.mean() * TRADING_DAYS
    ann_vol = port.std() * np.sqrt(TRADING_DAYS)
    sharpe = (ann_ret - RISK_FREE_ANNUAL) / ann_vol if ann_vol > 0 else 0.0

    return {
        "daily_returns": port,
        "Annual Return": float(ann_ret),
        "Annual Volatility": float(ann_vol),
        "Sharpe Ratio": float(sharpe),
    }

def analyze_portfolio_risk(portfolio_returns: pd.Series, start_date: pd.Timestamp, end_date: pd.Timestamp) -> Dict[str, float]:
    if portfolio_returns.empty:
        return {"Beta": 0.0, "Alpha (Annualized)": 0.0, "Max Drawdown": 0.0}
    mkt_px = load_price_series(MARKET_BENCH, start_date, end_date)
    mkt = mkt_px.pct_change().dropna()
    df = pd.concat([portfolio_returns.rename("p"), mkt.rename("m")], axis=1).dropna()
    if df.empty or df["m"].var() == 0:
        beta = 0.0
    else:
        beta = df["p"].cov(df["m"]) / df["m"].var()
    alpha_daily = df["p"].mean() - RISK_FREE_DAILY - beta * (df["m"].mean() - RISK_FREE_DAILY)
    alpha_annual = alpha_daily * TRADING_DAYS

    cum = (1 + portfolio_returns).cumprod()
    peak = cum.cummax()
    mdd = ((cum - peak) / peak).min()

    return {"Beta": float(beta), "Alpha (Annualized)": float(alpha_annual), "Max Drawdown": float(mdd) if pd.notna(mdd) else 0.0}

def run_portfolio_optimization(tickers: Tuple[str, ...], start_date: pd.Timestamp, end_date: pd.Timestamp, n_sims: int = 8000) -> Optional[Tuple[np.ndarray, Tuple[float, float], pd.DataFrame]]:
    tickers = [t.strip().upper() for t in tickers if isinstance(t, str)]
    R = build_returns_matrix(tickers, start_date, end_date)
    if R.empty or len(R.columns) < 2:
        return None

    mean_R = R.mean()
    cov = R.cov()

    def ann_return(w): return float(np.sum(mean_R * w) * TRADING_DAYS)
    def ann_vol(w):    return float(np.sqrt(np.dot(w.T, np.dot(cov, w))) * np.sqrt(TRADING_DAYS))
    def neg_sharpe(w):
        v = ann_vol(w)
        return 1e6 if v == 0 else - (ann_return(w) - RISK_FREE_ANNUAL) / v

    results = np.zeros((3, n_sims))
    for i in range(n_sims):
        w = np.random.random(len(tickers)); w /= w.sum()
        r = ann_return(w); v = ann_vol(w)
        s = 0.0 if v == 0 else (r - RISK_FREE_ANNUAL) / v
        results[0, i] = v
        results[1, i] = r
        results[2, i] = s

    x0 = np.array([1.0/len(tickers)]*len(tickers))
    bounds = tuple((0.0, 1.0) for _ in tickers)
    cons = {"type": "eq", "fun": lambda w: np.sum(w) - 1.0}
    opt = minimize(neg_sharpe, x0, bounds=bounds, constraints=cons, method="SLSQP")
    w_opt = x0 if (not opt.success or np.isnan(opt.fun)) else opt.x

    max_sharpe_perf = (ann_return(w_opt), ann_vol(w_opt))
    summary = pd.DataFrame({"Weight": w_opt}, index=tickers); summary.index.name = "ETF"
    return results, max_sharpe_perf, summary