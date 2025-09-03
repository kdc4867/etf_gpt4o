# 📊 ETF 분석 및 포트폴리오 대시보드

이 프로젝트는 **ETF(Exchange Traded Fund)** 및 개별 주식의 성과, 리스크, 팩터 노출, 매크로 지표 연관성을 분석할 수 있는 **대시보드 애플리케이션**입니다.  
Streamlit 기반 인터페이스와 OpenAI GPT 모델을 결합하여, 데이터 기반의 지표와 자연어 분석 리포트를 동시에 제공합니다.  



---

## 🚀 주요 기능

### 1. 단일 ETF/주식 심층 분석
- 가격 추이 및 이동평균선 시각화
- 연간 수익률, 변동성, 샤프 비율 계산
- 리스크 지표 (베타, 알파, 최대 낙폭, VaR)
- 팩터 노출 분석 (Value, Growth, Momentum 등)
- 매크로 지표와의 상관관계 히트맵
- **GPT 기반 분석**: 성과, 리스크, 팩터 노출에 대한 한국어 인사이트 제공

### 2. 포트폴리오 분석
- 사이드바에서 ETF/주식 추가 → 자동 비중 계산
- 포트폴리오 전체 성과 지표 및 누적 수익률
- 자산 배분 파이 차트
- 효율적 투자선(Efficient Frontier) 및 최적 포트폴리오 추천
- **GPT 기반 종합 분석 리포트** 제공

### 3. 사용자 친화적 UI
- Streamlit 대시보드로 직관적인 사용 가능
- 버튼 클릭만으로 GPT 분석 실행
- CSV 파일로 포트폴리오 저장/불러오기 가능

---

## 🛠️ 설치 방법

1. 저장소 클론
```bash
git clone https://github.com/your_username/etf-dashboard.git
cd etf-dashboard

	2.	가상환경 생성 및 패키지 설치

python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt

	3.	환경 변수 설정

	•	프로젝트 루트 디렉토리에 .env 파일 생성 후, OpenAI API 키를 입력합니다.

OPENAI_API_KEY=your_openai_api_key
```

⸻

▶️ 실행 방법

streamlit run main.py

브라우저에서 http://localhost:8501 로 접속하면 대시보드에 접근할 수 있습니다.

⸻

📂 프로젝트 구조

project_folder/
│
├── data_loader.py        # ETF/주식 데이터 로드 및 캐싱
├── etf_analysis.py       # 성과, 리스크, 팩터, 벤치마크 분석
├── gpt_analysis.py       # GPT API 연동 및 분석 리포트 생성
├── portfolio_analysis.py # 포트폴리오 성과·리스크·최적화 분석
├── visualizations.py     # Plotly 기반 시각화 함수
├── main.py               # Streamlit 앱 실행 메인 파일
└── requirements.txt      # 의존성 패키지


⸻


📌 참고
	•	데이터 소스: Yahoo Finance (yfinance API 활용)
	•	분석/시각화: Pandas, NumPy, Plotly
	•	인터페이스: Streamlit
	•	자연어 분석: OpenAI GPT-4o-mini

⸻

📄 라이선스

이 프로젝트는 MIT License를 따르며, 비상업적 용도로 작성되었습니다.

---

