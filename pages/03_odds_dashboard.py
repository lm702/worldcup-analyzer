import streamlit as st
from datetime import datetime

from data.storage import list_team_names, load_squad, save_match, load_match, list_match_ids
from core.models import Match, MatchOdds, MoneylineOdds, AsianHandicap, OverUnder, OddsSource
from components.odds_card import render_odds_card, render_odds_form


def _match_id_from_teams(home: str, away: str) -> str:
    return f"{home}_vs_{away}"


def main():
    st.title("💰 赔率面板")
    st.markdown("管理各场比赛的盘口赔率。")

    names = list_team_names()
    if len(names) < 2:
        st.warning("至少需要2支球队才能创建比赛。请先在「名单管理」创建球队。")
        return

    tab1, tab2 = st.tabs(["📝 录入赔率", "📋 查看已录入"])

    with tab1:
        c1, c2 = st.columns(2)
        with c1:
            home = st.selectbox("主队", names, key="odds_home")
        with c2:
            away = st.selectbox("客队", names, key="odds_away")

        if home == away:
            st.info("请选择两支不同的球队")
            return

        mid = _match_id_from_teams(home, away)
        existing = load_match(mid)

        if existing:
            st.success(f"比赛已存在: {home} vs {away}")
            for o in existing.odds_list:
                render_odds_card(o)
            if st.button("覆盖已存在赔率", type="secondary"):
                pass

        result = render_odds_form(key="odds_entry")
        if result:
            match_odds = MatchOdds(
                source=OddsSource.BET365,
                moneyline=MoneylineOdds(**result["moneyline"]),
                asian_handicap=AsianHandicap(**result["asian_handicap"]),
                over_under=OverUnder(**result["over_under"]),
                updated_at=datetime.now().isoformat(),
            )

            existing_match = load_match(mid)
            if existing_match:
                existing_match.odds_list = [o for o in existing_match.odds_list
                                            if o.source != OddsSource.BET365]
                existing_match.odds_list.append(match_odds)
                save_match(existing_match)
            else:
                match = Match(
                    match_id=mid,
                    home_team=home,
                    away_team=away,
                    odds_list=[match_odds],
                )
                save_match(match)

            st.success(f"赔率已保存: {home} vs {away}")
            st.rerun()

    with tab2:
        match_ids = list_match_ids()
        if not match_ids:
            st.info("暂无已录入的比赛")
            return

        selected_mid = st.selectbox("选择比赛", match_ids)
        match = load_match(selected_mid)
        if match:
            st.subheader(f"{match.home_team} vs {match.away_team}")
            for o in match.odds_list:
                render_odds_card(o)

            if st.button("删除此比赛", type="secondary"):
                from data.storage import MATCHES_DIR
                import os
                os.remove(MATCHES_DIR / f"{selected_mid.replace(' ', '_').replace('-', '_').replace('/', '_')}.json")
                st.success("已删除")
                st.rerun()
