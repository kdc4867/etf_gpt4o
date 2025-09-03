# file: gpt_analysis.py

from openai import OpenAI
import streamlit as st
import os
from dotenv import load_dotenv
from typing import Dict, Any
import pandas as pd # 'pd'를 사용하기 위해 pandas를 import합니다.

# .env 파일 로드 (파일이 없어도 에러 발생 안 함)
load_dotenv()

@st.cache_resource
def get_openai_client():
    """OpenAI API 클라이언트를 생성하고 캐시합니다."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        st.error("OPENAI_API_KEY 환경변수가 설정되지 않았습니다. .env 파일을 확인해주세요.")
        return None
    return OpenAI(api_key=api_key)

def get_gpt_analysis(prompt: str) -> str:
    """주어진 프롬프트로 GPT-4o mini 모델에 분석을 요청합니다."""
    client = get_openai_client()
    if not client:
        return "OpenAI 클라이언트 초기화에 실패했습니다."
    
    system_prompt = """
    당신은 글로벌 시장과 ETF 전략에 대한 깊은 지식을 가진 숙련된 금융 투자 분석가입니다. 
    모든 답변은 한국어로 제공하며, 초보자와 숙련된 투자자 모두를 위해 명확하고 간결하게 작성해주세요. 
    분석 시에는 현재 시장 상황과 잠재적인 미래 시나리오를 항상 고려해야 합니다.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"GPT API 호출 중 오류 발생: {e}")
        return "GPT 분석 중 오류가 발생했습니다. API 키와 네트워크 상태를 확인해주세요."

def analyze_financials_with_gpt(ticker: str, financial_data: Dict[str, Any]) -> str:
    """GPT를 사용하여 기업 재무 정보를 분석합니다."""
    # GPT에게 보낼 데이터 요약
    data_summary = {
        "시가총액": financial_data.get('marketCap'),
        "총 매출": financial_data.get('totalRevenue'),
        "P/E 비율": financial_data.get('trailingPE'),
        "P/B 비율": financial_data.get('priceToBook'),
        "배당 수익률": financial_data.get('dividendYield'),
        "부채 비율(D/E)": financial_data.get('debtToEquity'),
    }

    prompt = f"""
    ### 기업 재무 분석 요청: {ticker}

    **주요 재무 데이터:**
    ```json
    {data_summary}
    ```

    **분석 요청 사항:**
    1.  위 데이터를 바탕으로 이 기업의 **재무 건전성**을 평가해주세요.
    2.  데이터에서 발견되는 **기회와 리스크 요인**은 무엇인가요?
    3.  현재 시장 상황을 고려할 때, 이 기업에 대한 **투자자로서의 권장사항**을 제시해주세요.
    """
    return get_gpt_analysis(prompt)

def analyze_etf_performance_with_gpt(ticker: str, performance_data: Dict[str, Any]) -> str:
    """GPT를 사용하여 ETF 성과를 분석합니다."""
    prompt = f"""
    ### ETF 성과 분석 요청: {ticker}

    **주요 성과 지표:**
    ```json
    {performance_data}
    ```

    **분석 요청 사항:**
    1.  이 ETF의 **성과를 핵심 지표(수익률, 변동성, 샤프 비율)를 중심으로 해석**해주세요.
    2.  이 ETF의 **강점과 약점**은 무엇이라고 생각하나요?
    3.  투자자에게 도움이 될 만한 **실질적인 인사이트 3가지**를 제시해주세요.
    """
    return get_gpt_analysis(prompt)

def analyze_risk_with_gpt(ticker: str, risk_data: Dict[str, Any]) -> str:
    """GPT를 사용하여 ETF 리스크를 분석합니다."""
    prompt = f"""
    ### ETF 리스크 분석 요청: {ticker}

    **주요 리스크 지표:**
    ```json
    {risk_data}
    ```

    **분석 요청 사항:**
    1.  **베타, 알파, 최대 낙폭 등의 핵심 리스크 지표**가 의미하는 바를 쉽게 설명해주세요.
    2.  이 ETF는 **어떤 투자 성향의 투자자에게 적합**한가요?
    3.  현재 시장 상황에서 투자자가 **반드시 고려해야 할 5가지 핵심 포인트**를 짚어주세요.
    """
    return get_gpt_analysis(prompt)

def analyze_factor_with_gpt(ticker: str, factor_data: pd.Series) -> str:
    """GPT를 사용하여 ETF 팩터 노출도를 분석합니다."""
    prompt = f"""
    ### ETF 팩터 노출도 분석 요청: {ticker}

    **팩터 노출도 분석 결과 (회귀 계수):**
    ```
    {factor_data.to_string()}
    ```

    **분석 요청 사항:**
    1.  각 팩터(Market, Size, Value 등)에 대한 **노출도가 의미하는 바를 투자 전략 관점에서 해석**해주세요.
    2.  이러한 팩터 구성이 **다양한 시장 국면(상승장, 하락장, 횡보장)에서 ETF 성과에 어떤 영향을 미칠지** 분석해주세요.
    3.  현재 시장 상황에서 이 ETF의 **팩터 구성이 갖는 장단점**은 무엇인가요?
    """
    return get_gpt_analysis(prompt)

def compare_etfs_with_gpt(comparison_data: pd.DataFrame) -> str:
    """GPT를 사용하여 여러 ETF를 비교 분석합니다."""
    prompt = f"""
    ### 다수 ETF 비교 분석 요청

    **비교 데이터:**
    ```
    {comparison_data.to_markdown(index=False)}
    ```

    **분석 요청 사항:**
    1.  각 ETF의 **주요 특징과 장단점을 간결하게 요약**해주세요.
    2.  **성과, 리스크, 비용 측면에서 ETF들을 비교 분석**하고, 어떤 ETF가 가장 유망해 보이는지 의견을 제시해주세요.
    3.  각 ETF가 **어떤 유형의 투자자에게 적합할지** 구체적으로 설명해주세요.
    """
    return get_gpt_analysis(prompt)

def analyze_macro_with_gpt(ticker: str, correlation_data: pd.DataFrame) -> str:
    """GPT를 사용하여 ETF와 거시 경제 지표의 상관관계를 분석합니다."""
    prompt = f"""
    ### ETF-거시경제 지표 상관관계 분석 요청: {ticker}

    **상관관계 행렬:**
    ```
    {correlation_data.to_string()}
    ```

    **분석 요청 사항:**
    1.  **주요 거시경제 지표(S&P 500, 10년물 국채, VIX 등)와 ETF 수익률 간의 상관관계**를 해석해주세요.
    2.  이러한 상관관계가 **투자 결정에 어떤 영향을 미칠 수 있는지** 구체적인 예시를 들어 설명해주세요.
    3.  현재 경제 상황과 관찰된 상관관계를 고려할 때, 이 ETF의 **단기(3-6개월) 및 장기(1-3년) 전망**을 분석해주세요.
    """
    return get_gpt_analysis(prompt)

def analyze_portfolio_with_gpt(performance_metrics: Dict, risk_metrics: Dict, portfolio_df: pd.DataFrame) -> str:
    """GPT를 사용하여 포트폴리오 전체를 종합적으로 분석합니다."""
    prompt = f"""
    ### 포트폴리오 종합 분석 요청

    **포트폴리오 구성:**
    ```
    {portfolio_df[['ETF', 'Weight']].to_markdown(index=False)}
    ```

    **주요 성과 지표:**
    - 연간 수익률: {performance_metrics['Annual Return'] * 100:.2f}%
    - 연간 변동성: {performance_metrics['Annual Volatility'] * 100:.2f}%
    - 샤프 비율: {performance_metrics['Sharpe Ratio']:.2f}

    **주요 리스크 지표:**
    - 베타: {risk_metrics['Beta']:.2f}
    - 연환산 알파: {risk_metrics['Alpha (Annualized)'] * 100:.2f}%
    - 최대 낙폭: {risk_metrics['Max Drawdown'] * 100:.2f}%
    - 95% VaR: {risk_metrics['Value at Risk (95%)'] * 100:.2f}%

    **분석 요청 사항:**
    1.  포트폴리오의 **전반적인 성과와 리스크 프로필을 종합적으로 평가**해주세요.
    2.  현재 자산 배분의 **강점과 약점**은 무엇인가요?
    3.  **개선이나 리밸런싱을 위한 구체적이고 실행 가능한 제안**을 3가지 이상 제시해주세요.
    """
    return get_gpt_analysis(prompt)