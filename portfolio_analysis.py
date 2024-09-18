import pandas as pd
import numpy as np
import yfinance as yf
from scipy.optimize import minimize

def analyze_portfolio(portfolio_df, start_date, end_date):
    """포트폴리오 데이터를 분석하고 각 ETF의 수익률 데이터를 반환합니다."""
    portfolio_data = {}
    for etf, weight in portfolio_df[['ETF', 'Weight']].values:
        try:
            data = yf.download(etf, start=start_date, end=end_date)['Adj Close']
            returns = data.pct_change().dropna()
            portfolio_data[etf] = {'returns': returns, 'weight': weight}
        except Exception as e:
            print(f"Error fetching data for {etf}: {e}")
    return portfolio_data

def calculate_portfolio_performance(portfolio_data):
    """포트폴리오의 성과 지표를 계산합니다."""
    weights = np.array([data['weight'] for data in portfolio_data.values()])
    returns = pd.DataFrame({etf: data['returns'] for etf, data in portfolio_data.items()})
    
    portfolio_returns = (returns * weights).sum(axis=1)
    cumulative_returns = (1 + portfolio_returns).cumprod()
    
    annual_return = portfolio_returns.mean() * 252
    annual_volatility = portfolio_returns.std() * np.sqrt(252)
    sharpe_ratio = annual_return / annual_volatility
    
    return {
        'Annual Return': annual_return,
        'Annual Volatility': annual_volatility,
        'Sharpe Ratio': sharpe_ratio,
        'Cumulative Returns': cumulative_returns
    }

def analyze_risk(portfolio_data):
    """포트폴리오의 리스크 지표를 계산합니다."""
    weights = np.array([data['weight'] for data in portfolio_data.values()])
    returns = pd.DataFrame({etf: data['returns'] for etf, data in portfolio_data.items()})
    
    portfolio_returns = (returns * weights).sum(axis=1)
    
    # 베타 계산 (S&P 500을 시장 벤치마크로 사용)
    market_returns = yf.download('^GSPC', start=returns.index[0], end=returns.index[-1])['Adj Close'].pct_change().dropna()
    beta = portfolio_returns.cov(market_returns) / market_returns.var()
    
    # 알파 계산
    risk_free_rate = 0.02 / 252  # 연 2%의 무위험 수익률 가정
    alpha = portfolio_returns.mean() - risk_free_rate - beta * market_returns.mean()
    
    # 최대 낙폭 계산
    cum_returns = (1 + portfolio_returns).cumprod()
    running_max = cum_returns.cummax()
    drawdown = (cum_returns - running_max) / running_max
    max_drawdown = drawdown.min()
    
    return {
        'Beta': beta,
        'Alpha': alpha * 252,  # 연간화
        'Max Drawdown': max_drawdown,
        'Value at Risk (95%)': np.percentile(portfolio_returns, 5)
    }

def analyze_asset_allocation(portfolio_df):
    """포트폴리오의 자산 배분을 분석합니다."""
    asset_allocation = {}
    for etf, weight in portfolio_df[['ETF', 'Weight']].values:
        try:
            info = yf.Ticker(etf).info
            category = info.get('category', 'Other')
            if category not in asset_allocation:
                asset_allocation[category] = 0
            asset_allocation[category] += weight
        except Exception as e:
            print(f"Error fetching info for {etf}: {e}")
    return asset_allocation

def optimize_portfolio(portfolio_data):
    """효율적 프론티어를 계산하고 최적의 포트폴리오를 제안합니다."""
    returns = pd.DataFrame({etf: data['returns'] for etf, data in portfolio_data.items()})
    mean_returns = returns.mean()
    cov_matrix = returns.cov()
    
    num_assets = len(portfolio_data)
    num_portfolios = 10000
    results = np.zeros((3, num_portfolios))
    
    for i in range(num_portfolios):
        weights = np.random.random(num_assets)
        weights /= np.sum(weights)
        portfolio_return = np.sum(mean_returns * weights) * 252
        portfolio_std_dev = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights))) * np.sqrt(252)
        results[0,i] = portfolio_std_dev
        results[1,i] = portfolio_return
        results[2,i] = portfolio_return / portfolio_std_dev
    
    def portfolio_return(weights):
        return np.sum(mean_returns * weights) * 252

    def portfolio_volatility(weights):
        return np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights))) * np.sqrt(252)

    def min_function(weights):
        return -portfolio_return(weights) / portfolio_volatility(weights)

    constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
    bounds = tuple((0, 1) for asset in range(num_assets))
    
    optimal_portfolio = minimize(min_function, num_assets*[1./num_assets], method='SLSQP', bounds=bounds, constraints=constraints)
    
    return results, optimal_portfolio