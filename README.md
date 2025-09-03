# 📈 AI 기반 금융 분석 대시보드

Streamlit과 OpenAI(GPT)를 활용한 ETF/주식 분석 및 포트폴리오 최적화 대시보드입니다.

## 📄 개요

복잡한 금융 데이터를 직관적으로 시각화하고, AI를 통해 데이터 기반의 자연어 분석 리포트를 제공하여 투자 분석의 효율을 높이는 것을 목표로 합니다. 데이터 수집부터 분석, 포트폴리오 최적화까지의 과정을 하나의 인터페이스에서 통합 관리할 수 있습니다.

## 🚀 주요 기능

- **단일 종목 심층 분석**
    - 핵심 성과 지표 (수익률, 변동성, 샤프 비율) 및 리스크 지표 (베타, 알파, MDD)
    - ETF 프록시 기반 팩터 회귀 분석 및 주요 거시 경제 지표 상관관계 분석
- **포트폴리오 분석 및 최적화**
    - 사용자 맞춤 포트폴리오 구성 및 성과 추적
    - 효율적 투자선(Efficient Frontier) 및 최대 샤프 포트폴리오 계산 (`SLSQP`)
- **AI 기반 분석 리포트**
    - OpenAI GPT-4o mini 연동
    - 버튼 클릭으로 모든 차트와 지표에 대한 자연어 분석 리포트 생성

## 🛠️ 기술 스택

- **Core**: `Python`, `Streamlit`
- **Data Handling**: `Pandas`, `NumPy`, `yfinance`
- **Analysis**: `Scikit-learn`, `SciPy`
- **Visualization**: `Plotly`
- **AI**: `OpenAI API`

## ⚙️ 설치 및 실행 방법

1. **저장소 클론**
    
    ```
    git clone https://github.com/kdc4867/etf_gpt4o.git
    cd etf_gpt4o
    
    ```
    
2. **의존성 패키지 설치**
    
    ```
    pip install -r requirements.txt
    
    ```
    
3. **환경 변수 설정**
프로젝트 루트에 `.env` 파일을 생성하고 OpenAI API 키를 입력합니다.
    
    ```
    OPENAI_API_KEY="sk-..."
    
    ```
    
4. **대시보드 실행**
    
    ```
    streamlit run main.py
    
    ```
    

## 📁 프로젝트 구조

```
.
├── main.py               # Streamlit 앱 메인
├── data_loader.py        # 데이터 로딩 및 캐싱
├── etf_analysis.py       # 단일 종목 분석 로직
├── portfolio_analysis.py # 포트폴리오 분석 로직
├── gpt_analysis.py       # OpenAI API 연동
├── visualizations.py     # Plotly 시각화 함수
├── requirements.txt
└── README.md

```

## 📄 라이선스

이 프로젝트는 MIT 라이선스를 따르며, 비상업적 용도로 작성되었습니다.