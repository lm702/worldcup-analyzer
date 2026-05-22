import streamlit as st
import pandas as pd
from core.models import Player, Position, Squad
from utils.constants import POSITION_LABELS


def squad_to_df(squad: Squad) -> pd.DataFrame:
    rows = []
    for i, p in enumerate(squad.players):
        rows.append({
            "序号": i + 1,
            "姓名": p.name,
            "位置": p.position.value,
            "位置中文": POSITION_LABELS.get(p.position.value, p.position.value),
            "俱乐部": p.club,
            "年龄": p.age,
            "出场": p.caps,
            "进球": p.goals,
            "赛季评分": p.season_rating,
            "定位": p.depth_rank,
            "核心": p.is_star,
            "伤病": p.is_injured,
            "吃牌": p.yellow_cards_24,
        })
    return pd.DataFrame(rows)


def df_to_squad(team_name: str, df: pd.DataFrame, group: str = "", coach: str = "") -> Squad:
    players = []
    for _, row in df.iterrows():
        pos_str = str(row.get("位置", "ST"))
        try:
            pos = Position(pos_str)
        except ValueError:
            pos = Position.ST
        players.append(Player(
            name=str(row.get("姓名", "")),
            position=pos,
            club=str(row.get("俱乐部", "")),
            age=int(row.get("年龄", 25)),
            caps=int(row.get("出场", 0)),
            goals=int(row.get("进球", 0)),
            season_rating=float(row.get("赛季评分", 6.5)),
            depth_rank=int(row.get("定位", 2)),
            is_star=bool(row.get("核心", False)),
            is_injured=bool(row.get("伤病", False)),
            yellow_cards_24=int(row.get("吃牌", 0)),
        ))
    return Squad(team_name=team_name, group=group, coach=coach, players=players)


def render_editor(squad: Squad, key: str = "editor") -> tuple[bool, pd.DataFrame]:
    df = squad_to_df(squad)
    display_cols = ["序号", "姓名", "位置", "俱乐部", "年龄", "出场", "赛季评分", "定位", "核心", "伤病"]

    edited = st.data_editor(
        df[display_cols],
        column_config={
            "序号": st.column_config.NumberColumn("序号", disabled=True, width="small"),
            "姓名": st.column_config.TextColumn("姓名", width="medium"),
            "位置": st.column_config.SelectColumn(
                "位置",
                options=[p.value for p in Position],
                width="small",
            ),
            "俱乐部": st.column_config.TextColumn("俱乐部", width="medium"),
            "年龄": st.column_config.NumberColumn("年龄", min_value=16, max_value=45, width="small"),
            "出场": st.column_config.NumberColumn("出场", min_value=0, width="small"),
            "赛季评分": st.column_config.NumberColumn("评分", min_value=1.0, max_value=10.0, step=0.1, width="small"),
            "定位": st.column_config.SelectColumn("定位", options=[1, 2, 3], width="small"),
            "核心": st.column_config.CheckboxColumn("核心", width="small"),
            "伤病": st.column_config.CheckboxColumn("伤病", width="small"),
        },
        num_rows="dynamic",
        use_container_width=True,
        key=key,
        height=600,
    )

    return True, edited
