### README.md

```markdown
# ETF Analysis Dashboard

This project aims to build a dashboard for analyzing the performance of ETFs (Exchange Traded Funds). It uses Streamlit and OpenAI's GPT-4 to perform analysis on ETF performance, risk, factor exposure, and benchmark comparison.

이 프로젝트는 ETF(Exchange Traded Funds) 성과 분석을 위한 대시보드를 구축하는 것을 목표로 합니다. Streamlit과 OpenAI의 GPT-4o-mini를 사용하여 ETF 성과, 리스크, 팩터 노출도 및 벤치마크와의 비교를 수행할 수 있습니다.

## Features / 기능
- **ETF Performance Analysis / ETF 성과 분석**: Calculates and displays annual return, volatility, Sharpe ratio, and expense ratio. / 연간 수익률, 연간 변동성, 샤프 비율 및 경비 비율을 계산하고 표시합니다.
- **Risk and Benchmark Analysis / 리스크 및 벤치마크 분석**: Analyzes risk metrics including beta, maximum drawdown, tracking error, and alpha. / 베타, 최대 낙폭, 추적 오차 및 알파를 포함한 리스크 지표를 분석합니다.
- **Factor Analysis / 팩터 분석**: Evaluates exposure to market, size, value, growth, and momentum factors. / 시장, 사이즈, 가치, 성장 및 모멘텀 팩터에 대한 노출도를 평가합니다.
- **ETF Comparison / ETF 비교**: Allows users to compare multiple ETFs based on performance and risk metrics. / 여러 ETF를 선택하여 성과와 리스크 지표를 비교합니다.
- **Macro and Market Correlation / 매크로 및 시장 상황 연관성**: Analyzes correlations between ETFs and major macroeconomic indicators. / ETF와 주요 거시 경제 지표 간의 상관관계를 분석합니다.
- **GPT-4 Enhanced Analysis / GPT-4 기반 분석**: Provides additional analysis and recommendations using GPT-4, with responses in Korean. / GPT-4를 사용하여 추가적인 분석과 추천을 제공합니다. (응답은 한국어로 제공됩니다)

## Installation / 설치
1. Clone the repository / 리포지토리를 클론합니다:
   ```bash
   git clone https://github.com/your_username/your_repository_name.git
   cd your_repository_name
   ```
2. Create and activate a virtual environment / 가상 환경을 생성하고 활성화합니다:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```
3. Install the required packages / 필요한 패키지를 설치합니다:
   ```bash
   pip install -r requirements.txt
   ```

## Environment Variables / 환경 변수 설정
1. Create a `.env` file and add your OpenAI API key / `.env` 파일을 생성하고 OpenAI API 키를 추가합니다:
   ```bash
   OPENAI_API_KEY=your_openai_api_key
   ```

## Usage / 사용 방법
1. Run the Streamlit app / Streamlit 앱을 실행합니다:
   ```bash
   streamlit run main.py
   ```
2. Open your browser and go to `http://localhost:8501` to access the dashboard / 브라우저에서 `http://localhost:8501`을 열어 대시보드에 접근합니다.

## Project Structure / 프로젝트 구조
```
your_project_folder/
│
├── data_loader.py           # Functions to load and cache ETF data / ETF 데이터를 로드하고 캐시하는 함수
├── etf_analysis.py          # Functions for ETF performance, risk, factor, and benchmark analysis / ETF 성과, 리스크, 팩터 및 벤치마크 분석 함수
├── gpt_analysis.py          # Functions to integrate GPT-4 API for enhanced analysis / GPT-4 API를 통합한 추가 분석 함수
├── main.py                  # Main file for the Streamlit app / Streamlit 앱 메인 파일
└── visualizations.py        # Functions to create visualizations / 시각화 함수
```



이제 이 두 파일을 프로젝트 루트 디렉토리에 저장하고, Git을 통해 커밋 및 푸시하면 됩니다.

### 커밋 및 푸시

```bash
# 변경된 파일을 스테이징
git add README.md LICENSE

# 변경 사항 커밋
git commit -m "Add bilingual README and LICENSE files"

# 변경 사항 푸시
git push origin master
```
