import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

def plot_price_performance(data, ticker):
    fig = px.line(data, y='Adj Close', title=f"{ticker} 가격 성과")
    st.plotly_chart(fig)

def plot_factor_exposure(factor_exposure):
    fig = px.bar(factor_exposure, title="팩터 노출도")
    st.plotly_chart(fig)

def plot_correlation_heatmap(correlation, etf_ticker):
    fig, ax = plt.subplots(figsize=(12, 10))
    sns.heatmap(correlation, annot=True, cmap='coolwarm', vmin=-1, vmax=1, center=0, ax=ax)
    plt.title(f'Correlation between {etf_ticker} and Macro Indicators')
    st.pyplot(fig)

def plot_investment_style(style):
    st.markdown(f"<h2 style='text-align: center; color: blue;'>{style}</h2>", unsafe_allow_html=True)