import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import plotly.graph_objects as go
import networkx as nx



def plot_high_correlation_network(G, etf_ticker):
    pos = nx.spring_layout(G)
    
    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines')

    node_x = []
    node_y = []
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        hoverinfo='text',
        marker=dict(
            showscale=True,
            colorscale='YlGnBu',
            size=10,
            colorbar=dict(
                thickness=15,
                title='Node Connections',
                xanchor='left',
                titleside='right'
            )
        ),
        text=[],
        textposition="top center"
    )

    node_adjacencies = []
    node_text = []
    for node, adjacencies in enumerate(G.adjacency()):
        node_adjacencies.append(len(adjacencies[1]))
        node_text.append(f'{adjacencies[0]}<br># of connections: {len(adjacencies[1])}')

    node_trace.marker.color = node_adjacencies
    node_trace.text = node_text

    fig = go.Figure(data=[edge_trace, node_trace],
                 layout=go.Layout(
                    title=f'High Correlation Network (|correlation| >= 0.75) for {etf_ticker}',
                    titlefont_size=16,
                    showlegend=False,
                    hovermode='closest',
                    margin=dict(b=20,l=5,r=5,t=40),
                    annotations=[ dict(
                        showarrow=False,
                        xref="paper", yref="paper",
                        x=0.005, y=-0.002 ) ],
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                    )
    
    st.plotly_chart(fig)


def plot_price_performance(data, ticker):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data.index, y=data['Adj Close'], mode='lines', name=ticker))
    fig.update_layout(title=f"{ticker} 가격 성과", xaxis_title="날짜", yaxis_title="가격")
    st.plotly_chart(fig)

def plot_factor_exposure(factor_exposure):
    fig = go.Figure(go.Bar(x=factor_exposure.index, y=factor_exposure.values))
    fig.update_layout(title="팩터 노출도", xaxis_title="팩터", yaxis_title="노출도")
    st.plotly_chart(fig)

def plot_correlation_heatmap(correlation, etf_ticker):
    fig = px.imshow(correlation, text_auto=True, aspect="auto", color_continuous_scale='RdBu_r')
    fig.update_layout(title=f'{etf_ticker}와 매크로 지표 간 상관관계', width=800, height=600)
    st.plotly_chart(fig)

def plot_investment_style(style):
    st.markdown(f"<h2 style='text-align: center; color: blue;'>{style}</h2>", unsafe_allow_html=True)

def plot_performance_comparison(data, tickers):
    fig = go.Figure()
    for ticker in tickers:
        fig.add_trace(go.Scatter(x=data.index, y=data[ticker], mode='lines', name=ticker))
    fig.update_layout(title="ETF 성과 비교", xaxis_title="날짜", yaxis_title="정규화된 가격")
    st.plotly_chart(fig)