import streamlit as st
import plotly.graph_objects as go

from data.storage import load_match, load_analysis, list_match_ids, list_team_names
from core.value_bet import compute_value_bets, model_prob_from_ratings, moneyline_vig
from components.value_bet_table import render_value_bets
from core.analysis_engine import analyze_squad
from data.storage import load_squad, save_analysis


def _get_or_run_analysis(team_name: str):
    analysis = load_analysis(team_name)
    if analysis is None:
        squad = load_squad(team_name)
        if squad:
            analysis = analyze_squad(squad)
            save_analysis(analysis)
    return analysis


def _render_prob_comparison(bets):
    fig = go.Figure()
    labels, implied, model = [], [], []
    for b in bets:
        if b.market_type == "胜平负":
            labels.append(b.selection)
            implied.append(b.implied_prob * 100)
            model.append(b.model_prob * 100)

    if labels:
        fig.add_trace(go.Bar(name="市场概率", x=labels, y=implied,
                             marker_color="#95a5a6"))
        fig.add_trace(go.Bar(name="模型概率", x=labels, y=model,
                             marker_color="#27ae60"))
        fig.update_layout(
            barmode="group",
            yaxis=dict(title="概率 %", range=[0, 80]),
            height=350,
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
        )
        st.plotly_chart(fig, use_container_width=True, key="prob_comp")


def _render_scatter(bets):
    fig = go.Figure()
    colors, sizes, texts = [], [], []
    for b in bets:
        colors.append("#27ae60" if b.expected_value > 0 else "#e74c3c")
        sizes.append(min(20, max(8, abs(b.expected_value) * 200)))
        texts.append(f"{b.selection}<br>EV: {b.expected_value * 100:+.1f}%")

    fig.add_trace(go.Scatter(
        x=[b.implied_prob * 100 for b in bets],
        y=[b.model_prob * 100 for b in bets],
        mode="markers+text",
        marker=dict(color=colors, size=sizes, opacity=0.7),
        text=[b.selection.split()[-1] if len(b.selection.split()) > 1 else b.selection
              for b in bets],
        textposition="top center",
        hovertemplate="<b>%{text}</b><br>市场: %{x:.1f}%<br>模型: %{y:.1f}%<br>EV: %{customdata}<extra></extra>",
        customdata=[f"{b.expected_value * 100:+.1f}%" for b in bets],
    ))

    max_val = max(max(b.implied_prob, b.model_prob) for b in bets) * 100 + 10
    fig.add_trace(go.Scatter(
        x=[0, max_val], y=[0, max_val],
        mode="lines", line=dict(dash="dash", color="gray"),
        showlegend=False,
    ))

    fig.update_layout(
        xaxis=dict(title="市场隐含概率 %", range=[0, max_val]),
        yaxis=dict(title="模型概率 %", range=[0, max_val]),
        height=400,
    )
    st.plotly_chart(fig, use_container_width=True, key="ev_scatter")


def main():
    st.title("🎯 交叉参考")
    st.markdown("结合6维评分和市场赔率，发现价值投注机会。")

    match_ids = list_match_ids()
    if not match_ids:
        st.info("暂无比赛数据。请先在「赔率面板」录入赔率。")
        return

    selected_mid = st.selectbox("选择比赛", match_ids, key="xref_match")
    match = load_match(selected_mid)
    if match is None:
        st.error("无法加载比赛数据")
        return

    st.subheader(f"{match.home_team} vs {match.away_team}")

    with st.spinner("正在分析两队..."):
        analysis_h = _get_or_run_analysis(match.home_team)
        analysis_a = _get_or_run_analysis(match.away_team)

    if analysis_h is None:
        st.warning(f"缺少 {match.home_team} 的分析数据，请先在6维分析页面运行分析")
        return
    if analysis_a is None:
        st.warning(f"缺少 {match.away_team} 的分析数据，请先在6维分析页面运行分析")
        return

    c1, c2, c3 = st.columns(3)
    c1.metric(f"{match.home_team} 评分", f"{analysis_h.overall_rating:.1f}")
    c2.metric(f"{match.away_team} 评分", f"{analysis_a.overall_rating:.1f}")
    diff = analysis_h.overall_rating - analysis_a.overall_rating
    c3.metric("分差", f"{diff:+.1f}",
              delta=f"{match.home_team} 领先" if diff > 0 else f"{match.away_team} 领先")

    h_prob, d_prob, a_prob = model_prob_from_ratings(analysis_h, analysis_a)
    st.markdown(f"**模型预测**: {match.home_team} {h_prob*100:.0f}% / 平 {d_prob*100:.0f}% / {match.away_team} {a_prob*100:.0f}%")

    for odds_entry in match.odds_list:
        st.markdown(f"---")
        st.markdown(f"### 来源: {odds_entry.source.value}")

        if odds_entry.moneyline:
            vig = moneyline_vig(odds_entry.moneyline)
            st.caption(f"庄家水钱: {vig}%")

        bets = compute_value_bets(
            odds_entry, analysis_h, analysis_a,
            home_team=match.home_team, away_team=match.away_team,
        )

        col_v, col_p = st.columns([3, 2])

        with col_v:
            render_value_bets(bets)

        with col_p:
            st.markdown("**概率对比**")
            _render_prob_comparison(bets)

            st.markdown("**价值散点图**")
            st.caption("点在对角线以上 = 模型比市场看好（存在价值）")
            _render_scatter(bets)
