import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

from data.storage import list_team_names, load_analysis, load_squad
from core.analysis_engine import analyze_squad, compare_teams
from data.storage import save_analysis
from core.simulation import run_simulation, expected_score_probabilities
from core.models import SimulationParams
from utils.constants import DIMENSION_ORDER, DIMENSION_LABELS


def _get_analysis(team_name: str):
    analysis = load_analysis(team_name)
    if analysis is None:
        squad = load_squad(team_name)
        if squad:
            analysis = analyze_squad(squad)
            save_analysis(analysis)
    return analysis


def _render_outcome_gauge(h_prob, d_prob, a_prob, team_h, team_a):
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=[team_h, "平局", team_a],
        y=[h_prob * 100, d_prob * 100, a_prob * 100],
        marker_color=["#2980b9", "#95a5a6", "#c0392b"],
        text=[f"{h_prob*100:.1f}%", f"{d_prob*100:.1f}%", f"{a_prob*100:.1f}%"],
        textposition="outside",
    ))
    fig.update_layout(
        title="赛果概率",
        yaxis=dict(title="概率 %", range=[0, max(h_prob, d_prob, a_prob) * 100 + 15]),
        height=300,
        margin=dict(l=20, r=20, t=30, b=20),
    )
    st.plotly_chart(fig, use_container_width=True, key="outcome_gauge")


def _render_score_heatmap(score_probs: dict[str, float], max_goals: int = 5):
    matrix = [[0.0] * (max_goals + 1) for _ in range(max_goals + 1)]
    labels = [str(i) for i in range(max_goals + 1)]

    for k, v in score_probs.items():
        parts = k.split("-")
        if len(parts) == 2:
            gh, ga = int(parts[0]), int(parts[1])
            if gh <= max_goals and ga <= max_goals:
                matrix[gh][ga] = v * 100

    fig = px.imshow(
        matrix,
        x=labels, y=labels,
        color_continuous_scale="Blues",
        text_auto=".1f",
        labels=dict(x="客队进球", y="主队进球", color="概率 %"),
        aspect="auto",
        height=400,
    )
    fig.update_layout(
        title="比分概率矩阵 (%)",
        xaxis=dict(side="bottom"),
        margin=dict(l=20, r=20, t=40, b=20),
    )
    st.plotly_chart(fig, use_container_width=True, key="score_heatmap")


def _render_xg_comparison(xg_h, xg_a, team_h, team_a):
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=[team_h, team_a],
        y=[xg_h, xg_a],
        marker_color=["#2980b9", "#c0392b"],
        text=[f"{xg_h:.2f}", f"{xg_a:.2f}"],
        textposition="outside",
    ))
    fig.update_layout(
        title="期望进球 (xG)",
        yaxis=dict(range=[0, max(xg_h, xg_a) + 0.5]),
        height=250,
        margin=dict(l=20, r=20, t=30, b=20),
    )
    st.plotly_chart(fig, use_container_width=True, key="xg_bar")


def main():
    st.title("🔄 比赛模拟")
    st.markdown("基于6维评分，使用蒙特卡洛方法模拟比赛结果。支持情景参数微调。")

    names = list_team_names()
    if len(names) < 2:
        st.warning("至少需要2支球队。请先在「名单管理」创建球队。")
        return

    col1, col2 = st.columns(2)
    with col1:
        team_h = st.selectbox("主队", names, key="sim_home")
    with col2:
        team_a = st.selectbox("客队", names, key="sim_away")

    if team_h == team_a:
        st.info("请选择两支不同的球队")
        return

    with st.spinner("加载分析数据..."):
        analysis_h = _get_analysis(team_h)
        analysis_a = _get_analysis(team_a)

    if analysis_h is None or analysis_a is None:
        st.error("球队分析数据缺失，请先在6维分析页面运行分析")
        return

    st.markdown("---")
    c1, c2, c3 = st.columns(3)
    c1.metric(f"{team_h} 综合评分", f"{analysis_h.overall_rating:.1f}")
    c2.metric(f"{team_a} 综合评分", f"{analysis_a.overall_rating:.1f}")
    diff = analysis_h.overall_rating - analysis_a.overall_rating
    c3.metric("分差", f"{diff:+.1f}")

    st.markdown("### 情景调整")
    st.caption("调整各维度参数（%），模拟不同战术场景。正数=增强，负数=削弱。")

    col_adj1, col_adj2 = st.columns(2)
    home_adjustments = {}
    away_adjustments = {}

    with col_adj1:
        st.markdown(f"**{team_h} 调整**")
        for dim in DIMENSION_ORDER:
            label = DIMENSION_LABELS.get(dim, dim)
            home_adjustments[dim] = st.slider(
                label, -30, 30, 0, 5,
                key=f"h_{dim}",
                help=f"当前 {label} 评分: {getattr(analysis_h, dim, None) and getattr(analysis_h, dim).score:.0f}",
            )

    with col_adj2:
        st.markdown(f"**{team_a} 调整**")
        for dim in DIMENSION_ORDER:
            label = DIMENSION_LABELS.get(dim, dim)
            away_adjustments[dim] = st.slider(
                label, -30, 30, 0, 5,
                key=f"a_{dim}",
            )

    presets = st.selectbox(
        "快速预设", ["无", "主队优势", "防守反击", "全攻全守", "体能劣势"],
        help="选择预设将自动调整滑块",
    )
    if presets == "主队优势":
        for dim in DIMENSION_ORDER:
            home_adjustments[dim] = 10
        st.info("主队优势预设已应用（所有维度+10%）")
    elif presets == "防守反击":
        home_adjustments["fatigue_management"] = -5
        home_adjustments["knockout_adaptability"] = 15
        away_adjustments["position_distribution"] = 10
        away_adjustments["yellow_card_risk"] = 15
        st.info("防守反击预设已应用")
    elif presets == "全攻全守":
        home_adjustments["position_distribution"] = 10
        home_adjustments["substitution_strategy"] = 15
        away_adjustments["fatigue_management"] = -10
        st.info("全攻全守预设已应用")
    elif presets == "体能劣势":
        home_adjustments["fatigue_management"] = -20
        st.info("体能劣势预设已应用")

    st.markdown("---")
    n_sims = st.slider("模拟次数", 1000, 50000, 10000, 1000, help="次数越多结果越稳定但越慢")

    if st.button("▶️ 运行模拟", type="primary", use_container_width=True):
        with st.spinner(f"正在进行 {n_sims:,} 次模拟..."):
            params = SimulationParams(
                home_adjustments={k: v for k, v in home_adjustments.items() if v != 0},
                away_adjustments={k: v for k, v in away_adjustments.items() if v != 0},
                n_simulations=n_sims,
            )
            result = run_simulation(analysis_h, analysis_a, params)

        st.markdown("---")
        st.subheader("模拟结果")

        col_r1, col_r2 = st.columns(2)

        with col_r1:
            st.metric("模拟次数", f"{result.n_simulations:,}")
            st.metric(f"{team_h} 胜率", f"{result.home_win_prob:.1%}")
            st.metric(f"平局概率", f"{result.draw_prob:.1%}")
            st.metric(f"{team_a} 胜率", f"{result.away_win_prob:.1%}")

        with col_r2:
            st.metric(f"{team_h} 期望进球", f"{result.expected_goals_home:.2f}")
            st.metric(f"{team_a} 期望进球", f"{result.expected_goals_away:.2f}")
            st.metric("最可能比分", result.most_likely_score)
            total_goals = result.expected_goals_home + result.expected_goals_away
            st.metric("总期望进球", f"{total_goals:.2f}")

        _render_outcome_gauge(result.home_win_prob, result.draw_prob,
                              result.away_win_prob, team_h, team_a)
        _render_xg_comparison(result.expected_goals_home, result.expected_goals_away,
                              team_h, team_a)

        if result.score_probs:
            _render_score_heatmap(result.score_probs)
            st.subheader("最可能比分TOP10")
            sorted_scores = sorted(result.score_probs.items(), key=lambda x: -x[1])[:10]
            cols = st.columns(5)
            for i, (score, prob) in enumerate(sorted_scores):
                h, a = score.split("-")
                with cols[i % 5]:
                    st.metric(f"{h}-{a}", f"{prob:.1%}")

        if not result.score_probs:
            st.info("高模拟次数下未统计比分分布。降低模拟次数可查看具体比分概率。")
