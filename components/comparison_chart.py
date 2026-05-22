import plotly.graph_objects as go
import streamlit as st
from core.models import SixDimensionAnalysis


def render_comparison_bars(analysis_a: SixDimensionAnalysis, analysis_b: SixDimensionAnalysis,
                           label_a: str = "", label_b: str = ""):
    labels, scores_a, scores_b = [], [], []
    for label, dim in analysis_a.dimension_list():
        labels.append(label)
        scores_a.append(dim.score)
    for _, dim in analysis_b.dimension_list():
        scores_b.append(dim.score)

    fig = go.Figure()
    fig.add_trace(go.Bar(name=label_a or analysis_a.team_name, x=labels, y=scores_a,
                         marker_color="royalblue", text=[f"{s:.0f}" for s in scores_a],
                         textposition="outside"))
    fig.add_trace(go.Bar(name=label_b or analysis_b.team_name, x=labels, y=scores_b,
                         marker_color="#c0392b", text=[f"{s:.0f}" for s in scores_b],
                         textposition="outside"))

    fig.update_layout(
        barmode="group",
        yaxis=dict(range=[0, 100], title="评分"),
        height=400,
        margin=dict(l=40, r=40, t=20, b=60),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
    )
    st.plotly_chart(fig, use_container_width=True, key=f"comp_bar_{id(analysis_a)}_{id(analysis_b)}")


def render_dimension_detail(dimension_label: str, rating, team_name: str):
    score = rating.score
    color = "#27ae60" if score >= 70 else "#f39c12" if score >= 50 else "#e74c3c"
    st.markdown(f"**{dimension_label}** — 评分 **{score:.0f}**")
    st.progress(score / 100)
    if rating.strengths:
        for s in rating.strengths:
            st.markdown(f"<span style='color:#27ae60'>✓ {s}</span>", unsafe_allow_html=True)
    if rating.weaknesses:
        for w in rating.weaknesses:
            st.markdown(f"<span style='color:#e74c3c'>✗ {w}</span>", unsafe_allow_html=True)
