import streamlit as st
import pandas as pd
from core.models import ValueBet
from utils.formatters import fmt_odds, fmt_prob, fmt_ev, fmt_kelly


def render_value_bets(bets: list[ValueBet]):
    if not bets:
        st.info("暂无价值注数据。请先录入赔率并运行分析。")
        return

    rows = []
    for b in bets:
        ev_pct = f"{b.expected_value * 100:+.1f}%"
        rows.append({
            "市场": b.market_type,
            "选项": b.selection,
            "赔率": fmt_odds(b.odds),
            "市场概率": fmt_prob(b.implied_prob),
            "模型概率": fmt_prob(b.model_prob),
            "EV": ev_pct,
            "Kelly": fmt_kelly(b.kelly_fraction),
            "推荐": b.recommendation,
        })

    df = pd.DataFrame(rows)

    def color_rec(val):
        if val == "推荐":
            return "background-color: #27ae60; color: white"
        if val == "观望":
            return "background-color: #f39c12; color: white"
        if val == "不推荐":
            return "background-color: #e74c3c; color: white"
        return ""

    def color_ev(val: str) -> str:
        try:
            v = float(val.strip("%"))
            if v > 5:
                return "color: #27ae60; font-weight: bold"
            if v > 0:
                return "color: #f39c12"
            return "color: #e74c3c"
        except ValueError:
            return ""

    styled = df.style.map(color_rec, subset=["推荐"]).map(color_ev, subset=["EV"])
    st.dataframe(styled, use_container_width=True, hide_index=True)

    pos_bets = [b for b in bets if b.expected_value > 0]
    if pos_bets:
        st.markdown("---")
        st.markdown("### ✅ 正期望值推荐")
        for b in pos_bets:
            kelly_str = fmt_kelly(b.kelly_fraction)
            st.markdown(
                f"> **{b.selection}** @ {fmt_odds(b.odds)}  "
                f"| EV {fmt_ev(b.expected_value)}  "
                f"| Kelly {kelly_str}  "
                f"| 模型概率 {fmt_prob(b.model_prob)} vs 市场 {fmt_prob(b.implied_prob)}"
            )
