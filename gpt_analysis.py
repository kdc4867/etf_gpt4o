###gpt_analysis.py
from openai import OpenAI
import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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

def analyze_etf_performance(etf_data):
    prompt = f"""
Given the following ETF performance data: {etf_data}

1. Analyze the ETF's performnace based on this data.
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

1. Explain the exposure to each factor (e.g., market, size, value, momentum) in detail.
2. Interpret what this factor exposure means from an investment strategy perspective.
3. Analyze how this factor exposure might affect the ETF's performance.
4. Explain the pros and cons of this factor exposure in the current market situation.
5. Considering this ETF's factor exposure, suggest what type of portfolio it would be suitable for.
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

1. Interpret the correlation between each macroeconomic indicator and the ETF specifically.
2. Explain how these correlations might influence investment decisions.
3. Analyze the outlook for this ETF considering the current economic situation.
4. Predict changes in key macroeconomic indicators over the next 6 months and forecast the ETF's performance accordingly.
5. Suggest how this ETF might play a role in hedging macroeconomic risks in a portfolio.
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
"Given the following ETF data: {etf_data}
And considering these market conditions: {market_conditions}

1. Predict the expected performance of this ETF over the next 6-12 months with specific figures (e.g., expected return range).
2. Explain 3 scenarios that could positively impact this ETF's performance and 3 that could negatively impact it.
3. Analyze how the volatility and risk level of this ETF are expected to change.
4. Explain whether it's appropriate to include this ETF in a current portfolio and why.
5. Advise on investment strategies or timing to maximize the performance of this ETF."
"""
    
    return get_gpt_analysis(prompt)