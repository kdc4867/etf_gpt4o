from openai import OpenAI
import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def analyze_portfolio_gpt(portfolio_data, performance_metrics, risk_metrics):
    """GPT를 사용하여 포트폴리오를 분석합니다."""
    prompt = f"""
    Given the following portfolio data and metrics:
    
    Portfolio composition:
    {', '.join([f"{etf}: {data['weight']*100:.2f}%" for etf, data in portfolio_data.items()])}
    
    Performance metrics:
    Annual Return: {performance_metrics['Annual Return']*100:.2f}%
    Annual Volatility: {performance_metrics['Annual Volatility']*100:.2f}%
    Sharpe Ratio: {performance_metrics['Sharpe Ratio']:.2f}
    
    Risk metrics:
    Beta: {risk_metrics['Beta']:.2f}
    Alpha: {risk_metrics['Alpha']*100:.2f}%
    Max Drawdown: {risk_metrics['Max Drawdown']*100:.2f}%
    Value at Risk (95%): {risk_metrics['Value at Risk (95%)']*100:.2f}%
    
    Please provide a comprehensive analysis of this portfolio, including:
    1. An overview of the portfolio's performance and risk profile
    2. Strengths and weaknesses of the current asset allocation
    3. Suggestions for potential improvements or rebalancing
    4. Any notable trends or patterns in the portfolio's behavior
    5. Recommendations for the investor based on this analysis
    
    Please structure your response in clear sections and provide specific, actionable advice.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a highly experienced financial analyst specializing in ETF portfolio analysis. Provide your analysis in Korean, ensuring it is clear, concise, and tailored for both novice and experienced investors."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error in GPT analysis: {str(e)}")
        return "GPT 분석 중 오류가 발생했습니다. 나중에 다시 시도해 주세요."

def get_gpt_analysis(prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a highly experienced ETF investment analyst with deep knowledge of global markets and various ETF strategies. Provide your responses in Korean, ensuring they are clear, concise, and tailored for both novice and experienced investors. Always consider current market conditions and potential future scenarios in your analysis."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"API call error: {str(e)}")
        return None

def analyze_financials_with_gpt(ticker, financial_data):
    """GPT를 사용하여 티커의 재무 정보를 분석합니다."""
    prompt = f"""
    Given the following financial data for {ticker}:

    - Market Cap: {financial_data.get('marketCap', 'N/A')}
    - Total Revenue: {financial_data.get('totalRevenue', 'N/A')}
    - Total Cash: {financial_data.get('totalCash', 'N/A')}
    - EBITDA: {financial_data.get('ebitda', 'N/A')}
    - Debt to Equity Ratio: {financial_data.get('debtToEquity', 'N/A')}
    - PE Ratio: {financial_data.get('trailingPE', 'N/A')}
    - PB Ratio: {financial_data.get('priceToBook', 'N/A')}
    - Dividend Yield: {financial_data.get('dividendYield', 'N/A')}%

    Please analyze this data and provide insights on:
    1. The company's financial health.
    2. Risks and opportunities based on the given data.
    3. Key strengths and weaknesses in comparison to industry averages.
    4. Recommendations for an investor looking at this company in the current market environment.
    """
    
    return get_gpt_analysis(prompt)

def analyze_etf_performance(etf_data):
    prompt = f"""
Given the following ETF performance data: {etf_data}

1. Analyze the ETF's performance based on this data.
2. Specifically mention key performance indicators (e.g., annual return, volatility, Sharpe ratio).
3. Clearly explain the strengths and weaknesses of this ETF.
4. Provide 3 actionable insights that would be valuable for investors.
5. Briefly comment on the outlook for this ETF considering the current market conditions.
"""
    return get_gpt_analysis(prompt)

def analyze_risk_and_benchmark(risk_data):
    prompt = f"""
Based on the following risk and benchmark analysis data for the ETF: {risk_data}

1. Interpret this data and explain the key risk indicators (e.g., beta, maximum drawdown, tracking error).
2. Analyze how this ETF is performing compared to its benchmark.
3. Present 5 key points that investors must consider.
4. Explain what type of investor this ETF's risk level is suitable for.
5. Predict how this ETF's risk profile might change in the current market conditions.
"""
    return get_gpt_analysis(prompt)

def analyze_factor_exposure(factor_data):
    prompt = f"""
    Given the following factor exposure analysis results for the ETF: {factor_data}

    1. Explain the exposure to each factor (market, size, value, growth, momentum, quality, low volatility, dividend, high yield, international, emerging markets) in detail.
    2. Interpret what this factor exposure means from an investment strategy perspective.
    3. Analyze how this factor exposure might affect the ETF's performance in different market conditions.
    4. Explain the pros and cons of this factor exposure in the current market situation.
    5. Considering this ETF's factor exposure, suggest what type of portfolio it would be suitable for.
    6. Discuss how this ETF's factor exposure compares to its peers or the broader market.
    """
    return get_gpt_analysis(prompt)

def compare_etfs(comparison_data):
    prompt = f"""
Based on the following comparison data for multiple ETFs: {comparison_data}

1. Summarize the main characteristics, advantages, and disadvantages of each ETF concisely.
2. Compare and analyze the ETFs in terms of performance, risk, and cost.
3. Explain specifically which type of investor each ETF is suitable for.
4. Considering the current market conditions, provide your opinion on which ETF looks most promising.
5. Evaluate the suitability of each ETF from both long-term and short-term investment perspectives.
"""
    return get_gpt_analysis(prompt)

def analyze_macro_correlation(correlation_data):
    prompt = f"""
    Given the following correlation data between the ETF and macroeconomic indicators: {correlation_data}

    Please provide a comprehensive analysis in Korean, addressing the following points:

    1. Interpret the correlation between each macroeconomic indicator (S&P 500, 10Y Treasury Yield, VIX, Gold, Oil, USD Index, Inflation Expectation, Real Estate, Consumer Sentiment, Manufacturing PMI, Unemployment Rate, Corporate Bond Spread) and the ETF specifically.
    2. Analyze how these correlations might change under different market conditions (e.g., economic expansion, recession, high inflation, low interest rates).
    3. Explain how these correlations might influence investment decisions. Provide specific examples of how an investor might use this information.
    4. Considering the current economic situation and the observed correlations, analyze the short-term (3-6 months) and long-term (1-3 years) outlook for this ETF.
    5. Based on historical trends and current economic indicators, predict potential changes in key macroeconomic indicators over the next 6-12 months. Then, forecast how these changes might affect the ETF's performance.
    6. Suggest how this ETF might play a role in hedging macroeconomic risks in a portfolio.
    7. Discuss any limitations of this correlation-based analysis and suggest additional factors or data that could provide a more comprehensive understanding of the ETF's relationship with macroeconomic conditions.
    """
    return get_gpt_analysis(prompt)

def get_etf_recommendation(etf_data, risk_profile):
    prompt = f"""
Based on the following ETF data: {etf_data}
And considering an investor with a {risk_profile} risk profile,

1. Would you recommend to buy, hold, or sell this ETF? Explain your reasoning in detail.
2. Predict the expected performance for the next 6 months, 1 year, and 3 years with specific figures.
3. Explain 3 major risks associated with this ETF, and assess the likelihood and impact of each risk.
4. Suggest what role this ETF could play in the investor's portfolio.
5. Advise on 3 points to be cautious about when investing in this ETF in the current market conditions.
"""
    return get_gpt_analysis(prompt)

def predict_etf_performance(etf_data, market_conditions):
    prompt = f"""
Given the following ETF data: {etf_data}
And considering these market conditions: {market_conditions}

1. Predict the expected performance of this ETF over the next 6-12 months with specific figures (e.g., expected return range).
2. Explain 3 scenarios that could positively impact this ETF's performance and 3 that could negatively impact it.
3. Analyze how the volatility and risk level of this ETF are expected to change.
4. Explain whether it's appropriate to include this ETF in a current portfolio and why.
5. Advise on investment strategies or timing to maximize the performance of this ETF.
"""
    return get_gpt_analysis(prompt)