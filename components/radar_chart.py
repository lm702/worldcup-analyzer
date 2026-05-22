import plotly.graph_objects as go
import streamlit as st
from core.models import SixDimensionAnalysis


def render_radar_chart(analysis: SixDimensionAnalysis, title: str = ""):
    labels, values = [], []
    for label, dim in analysis.dimension_list():
        labels.append(label)
        values.append(dim.score)

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values + [values[0]],
        theta=labels + [labels[0]],
        fill="toself",
        name=analysis.team_name,
        line_color="royalblue",
        fillcolor="rgba(65, 105, 225, 0.15)",
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], tickfont_size=10),
            angularaxis=dict(tickfont_size=12),
        ),
        title=dict(text=title, font_size=14),
        showlegend=False,
        height=400,
        margin=dict(l=60, r=60, t=40, b=30),
    )
    st.plotly_chart(fig, use_container_width=True, key=f"radar_{analysis.team_name}_{id(analysis)}")


def render_comparison_radar(analysis_a: SixDimensionAnalysis, analysis_b: SixDimensionAnalysis,
                            label_a: str = "", label_b: str = ""):
    labels_a, values_a = [], []
    for label, dim in analysis_a.dimension_list():
        labels_a.append(label)
        values_a.append(dim.score)

    labels_b, values_b = [], []
    for label, dim in analysis_b.dimension_list():
        labels_b.append(label)
        values_b.append(dim.score)

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values_a + [values_a[0]], theta=labels_a + [labels_a[0]],
        fill="toself", name=label_a or analysis_a.team_name,
        line_color="royalblue", fillcolor="rgba(65,105,225,0.15)",
    ))
    fig.add_trace(go.Scatterpolar(
        r=values_b + [values_b[0]], theta=labels_b + [labels_b[0]],
        fill="toself", name=label_b or analysis_b.team_name,
        line_color="#c0392b", fillcolor="rgba(192,57,43,0.10)",
    ))

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100], tickfont_size=10)),
        legend=dict(orientation="h", yanchor="bottom", y=1.08, xanchor="center", x=0.5),
        height=450,
        margin=dict(l=60, r=60, t=40, b=30),
    )
    st.plotly_chart(fig, use_container_width=True, key=f"comp_radar_{id(analysis_a)}_{id(analysis_b)}")
