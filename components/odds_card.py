import streamlit as st
from core.models import MatchOdds
from utils.formatters import fmt_odds, fmt_prob


def render_odds_card(odds: MatchOdds):
    src = odds.source.value
    st.markdown(f"**{src}**")
    updated = odds.updated_at[:16] if odds.updated_at else "—"

    cols = st.columns(4)
    cols[0].markdown(f"<small>更新</small><br>{updated}", unsafe_allow_html=True)

    if odds.moneyline:
        ml = odds.moneyline
        cols[1].markdown("**胜平负**")
        cols[1].markdown(
            f"主 {fmt_odds(ml.home_win)} / 平 {fmt_odds(ml.draw)} / 客 {fmt_odds(ml.away_win)}"
        )

    if odds.asian_handicap:
        ah = odds.asian_handicap
        cols[2].markdown("**亚洲盘口**")
        cols[2].markdown(f"{ah.line:+.1f}  主 {fmt_odds(ah.home_odds)} / 客 {fmt_odds(ah.away_odds)}")

    if odds.over_under:
        ou = odds.over_under
        cols[3].markdown("**大小球**")
        cols[3].markdown(f"大{ou.line} {fmt_odds(ou.over_odds)} / 小{ou.line} {fmt_odds(ou.under_odds)}")

    st.markdown("---")


def render_odds_form(key: str = "odds_form") -> dict:
    """渲染赔率录入表单，返回dict或None"""
    with st.form(key, clear_on_submit=False):
        st.markdown("##### 胜平负")
        c1, c2, c3 = st.columns(3)
        home_win = c1.number_input("主胜赔率", min_value=1.01, value=2.00, step=0.05, format="%.2f")
        draw = c2.number_input("平局赔率", min_value=1.01, value=3.00, step=0.05, format="%.2f")
        away_win = c3.number_input("客胜赔率", min_value=1.01, value=3.00, step=0.05, format="%.2f")

        st.markdown("##### 亚洲盘口")
        c1, c2, c3 = st.columns(3)
        ah_line = c1.number_input("盘口", value=-0.75, step=0.25, format="+.2f")
        ah_home = c2.number_input("主队水位", min_value=1.01, value=1.85, step=0.05, format="%.2f")
        ah_away = c3.number_input("客队水位", min_value=1.01, value=1.95, step=0.05, format="%.2f")

        st.markdown("##### 大小球")
        c1, c2, c3 = st.columns(3)
        ou_line = c1.number_input("大小球线", value=2.5, step=0.5, format="%.1f")
        ou_over = c2.number_input("大球赔率", min_value=1.01, value=2.05, step=0.05, format="%.2f")
        ou_under = c3.number_input("小球赔率", min_value=1.01, value=1.80, step=0.05, format="%.2f")

        submitted = st.form_submit_button("保存赔率", type="primary", use_container_width=True)

    if submitted:
        return {
            "moneyline": {"home_win": home_win, "draw": draw, "away_win": away_win},
            "asian_handicap": {"line": ah_line, "home_odds": ah_home, "away_odds": ah_away},
            "over_under": {"line": ou_line, "over_odds": ou_over, "under_odds": ou_under},
        }
    return {}
