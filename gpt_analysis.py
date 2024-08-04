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
                {"role": "system", "content": "You are an expert ETF investment analyst. Please provide your responses in Korean. "},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"API call error: {str(e)}")
        return None

def analyze_etf_performance(etf_data):
    prompt = f"""
The following is performance data for an ETF:

{etf_data}

Based on this data, analyze the ETF's performance and provide valuable insights for investors.
"""
    return get_gpt_analysis(prompt)

def analyze_risk_and_benchmark(risk_data):
    prompt = f"""
The following is risk and benchmark analysis data for an ETF:

{risk_data}

Interpret this data and explain the key points that investors should consider.
"""
    return get_gpt_analysis(prompt)

def analyze_factor_exposure(factor_data):
    prompt = f"""
The following is the factor exposure analysis result for an ETF:

{factor_data}

Explain what this factor exposure means how it might affect investment strategy.
"""
    return get_gpt_analysis(prompt)

def compare_etfs(comparison_data):
    prompt = f"""
The following is comparison data for multiple ETFs:

{comparison_data}

Based on this data, analyze the pros and cons of each ETF and suggest which types of investors they might be suitable for.
"""
    return get_gpt_analysis(prompt)

def analyze_macro_correlation(correlation_data):
    prompt = f"""
The following is correlation data between an ETF and macroeconomic indicators:
{correlation_data}

Interpret what these correlations mean and analyze the outlook for this ETF in the current economic situation.
"""
    return get_gpt_analysis(prompt)

def get_etf_recommendation(etf_data, risk_profile):
    prompt = f"""
Based on the following ETF data:
{etf_data}

And considering a {risk_profile} risk profile investor,
provide a detailed recommendation on whether to buy, hold, or sell this ETF.
Include potential future performance predictions and any risks to be aware of.
"""
    
    return get_gpt_analysis(prompt)

def predict_etf_performance(etf_data, market_conditions):
    prompt = f"""
Given the following ETF data:
{etf_data}

And considering these market conditions:
{market_conditions}

Predict the potential performance of the ETF over the next 6-12 months.
Provide a detailed analysis including potential upsides and downsides.
"""
    
    return get_gpt_analysis(prompt)