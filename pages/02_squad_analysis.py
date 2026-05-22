import streamlit as st
from datetime import datetime

from data.storage import load_squad, list_team_names, save_analysis
from core.analysis_engine import analyze_squad
from components.radar_chart import render_radar_chart, render_comparison_radar
from components.comparison_chart import render_comparison_bars, render_dimension_detail


def _run_analysis(team_name: str):
    squad = load_squad(team_name)
    if squad is None:
        st.error(f"未找到球队: {team_name}")
        return None
    with st.spinner(f"正在分析 {team_name}..."):
        analysis = analyze_squad(squad)
        save_analysis(analysis)
    return analysis


def main():
    st.title("📊 6维分析")
    st.markdown("基于26人大名单数据，从6个维度自动评分球队比赛能力。")

    names = list_team_names()
    if not names:
        st.warning("尚未创建球队。请先在「名单管理」页面创建球队。")
        return

    mode = st.radio("模式", ["单队分析", "两队对比"], horizontal=True)

    if mode == "单队分析":
        col1, col2 = st.columns([2, 1])
        with col1:
            team = st.selectbox("选择球队", names, key="single_team")
        with col2:
            st.markdown("##")
            run = st.button("▶️ 运行分析", type="primary", use_container_width=True)

        if run and team:
            analysis = _run_analysis(team)
            if analysis is None:
                return

            c1, c2 = st.columns([1, 1])
            with c1:
                st.subheader(f"⚽ {team}")
                st.metric("综合评分", f"{analysis.overall_rating:.1f}")
                st.caption(f"分析时间: {analysis.analyzed_at[:16]}")
            with c2:
                st.markdown("##### 各维度评分")
                for label, dim in analysis.dimension_list():
                    color = "🟢" if dim.score >= 70 else "🟡" if dim.score >= 50 else "🔴"
                    st.markdown(f"{color} **{label}**: {dim.score:.0f}")

            render_radar_chart(analysis, f"{team} — 6维能力雷达图")

            st.markdown("---")
            st.subheader("维度详情")
            cols = st.columns(2)
            for i, (label, dim) in enumerate(analysis.dimension_list()):
                with cols[i % 2]:
                    render_dimension_detail(label, dim, team)

        elif run:
            st.warning("请先选择球队")

    else:
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            team_a = st.selectbox("球队 A", names, key="team_a")
        with col2:
            team_b = st.selectbox("球队 B", names, key="team_b")
        with col3:
            st.markdown("##")
            run = st.button("▶️ 对比分析", type="primary", use_container_width=True)

        if run:
            if team_a == team_b:
                st.warning("请选择两支不同的球队")
                return

            analysis_a = _run_analysis(team_a)
            analysis_b = _run_analysis(team_b)
            if analysis_a is None or analysis_b is None:
                return

            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric(f"{team_a} 综合", f"{analysis_a.overall_rating:.1f}")
            with c2:
                diff = analysis_a.overall_rating - analysis_b.overall_rating
                st.metric("分差",
                          f"{diff:+.1f}",
                          delta=f"{team_a} {'领先' if diff > 0 else '落后'}",
                          delta_color="normal" if diff > 0 else "inverse",
                          )
            with c3:
                st.metric(f"{team_b} 综合", f"{analysis_b.overall_rating:.1f}")

            col_r1, col_r2 = st.columns([1, 1])
            with col_r1:
                render_radar_chart(analysis_a)
            with col_r2:
                render_radar_chart(analysis_b)

            render_comparison_radar(analysis_a, analysis_b,
                                    label_a=team_a, label_b=team_b)
            render_comparison_bars(analysis_a, analysis_b,
                                   label_a=team_a, label_b=team_b)

            st.markdown("---")
            st.subheader("逐维度对比")
            cols = st.columns(2)
            for i, ((label_a, dim_a), (label_b, dim_b)) in enumerate(
                    zip(analysis_a.dimension_list(), analysis_b.dimension_list())):
                with cols[0] if i % 2 == 0 else cols[1]:
                    st.markdown(f"##### {label_a}")
                    c_a, c_b = st.columns(2)
                    c_a.metric(team_a, f"{dim_a.score:.0f}")
                    c_b.metric(team_b, f"{dim_b.score:.0f}")
                    if dim_a.score > dim_b.score:
                        st.markdown(f"<span style='color:#27ae60'>✓ {team_a} 优势 {dim_a.score - dim_b.score:.0f}分</span>",
                                    unsafe_allow_html=True)
                    elif dim_b.score > dim_a.score:
                        st.markdown(f"<span style='color:#c0392b'>✗ {team_b} 优势 {dim_b.score - dim_a.score:.0f}分</span>",
                                    unsafe_allow_html=True)
                    else:
                        st.markdown("持平")
                    st.markdown("---")
