import streamlit as st
import json
from datetime import datetime

from core.models import Squad, Player, Position
from data.storage import save_squad, load_squad, list_team_names, delete_squad
from components.squad_table import squad_to_df, df_to_squad
from utils.constants import POSITION_LABELS, ALL_GROUPS
from data.seed_squads import all_seed_squads


def _summary_stats(squad: Squad):
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("总人数", len(squad.players))
    col2.metric("平均年龄", f"{squad.avg_age:.1f}")
    col3.metric("总出场次数", squad.total_caps)
    col4.metric("核心球员", len(squad.stars))

    cats = squad.count_by_category()
    cat_labels = {"GK": "门将", "DEF": "后卫", "MID": "中场", "FWD": "前锋"}
    cols = st.columns(4)
    for i, (cat, label) in enumerate(cat_labels.items()):
        cols[i].metric(label, cats.get(cat, 0))


def _team_selector() -> str | None:
    names = list_team_names()
    if not names:
        return None

    selected = st.selectbox(
        "选择球队",
        names,
        key="team_selector",
        placeholder="选择已有球队...",
    )
    return selected


def _new_team_form():
    with st.form("new_team_form", clear_on_submit=True):
        name = st.text_input("球队名称", placeholder="例如: Brazil")
        group = st.selectbox("小组", [""] + ALL_GROUPS)
        coach = st.text_input("主教练", placeholder="例如: Carlo Ancelotti")
        submitted = st.form_submit_button("创建空名单", type="primary")

        if submitted and name.strip():
            empty_players = [
                Player(name=f"球员{i+1}", position=Position.ST, age=25, club="")
                for i in range(26)
            ]
            squad = Squad(
                team_name=name.strip(),
                group=group,
                coach=coach,
                players=empty_players,
                updated_at=datetime.now().isoformat(),
            )
            save_squad(squad)
            st.success(f"已创建球队: {name.strip()}")
            st.rerun()
        elif submitted:
            st.warning("请填写球队名称")


def _edit_page():
    col1, col2 = st.columns([3, 1])
    with col1:
        selected = _team_selector()
    with col2:
        st.button("➕ 新建球队", on_click=lambda: st.session_state.update({"show_new_form": True}))

    if st.session_state.get("show_new_form"):
        _new_team_form()
        if st.button("取消"):
            st.session_state.show_new_form = False
            st.rerun()

    if not selected:
        if not list_team_names():
            st.info("暂无球队数据。点击「新建球队」开始创建。")
        return

    squad = load_squad(selected)
    if squad is None:
        st.error(f"无法加载球队: {selected}")
        return

    st.subheader(f"✏️ {squad.team_name}")
    with st.expander("球队信息", expanded=False):
        c1, c2, c3 = st.columns(3)
        new_group = c1.text_input("小组", value=squad.group)
        new_coach = c2.text_input("主教练", value=squad.coach)
        _summary_stats(squad)

    st.markdown("---")
    st.markdown("### 球员名单编辑")
    st.caption("在表格中直接编辑数据，修改后点击「保存名单」。增删行使用表格底部的 + / - 按钮。")

    edited_df = st.data_editor(
        squad_to_df(squad),
        column_config={
            "序号": st.column_config.NumberColumn("序号", disabled=True, width="small"),
            "姓名": st.column_config.TextColumn("姓名", width="medium", required=True),
            "位置": st.column_config.SelectColumn(
                "位置",
                options=[p.value for p in Position],
                width="small",
                required=True,
            ),
            "位置中文": st.column_config.TextColumn("位置", disabled=True, width="small"),
            "俱乐部": st.column_config.TextColumn("俱乐部", width="medium"),
            "年龄": st.column_config.NumberColumn("年龄", min_value=16, max_value=45, step=1, width="small"),
            "出场": st.column_config.NumberColumn("出场", min_value=0, step=1, width="small"),
            "进球": st.column_config.NumberColumn("进球", min_value=0, step=1, width="small"),
            "赛季评分": st.column_config.NumberColumn("评分", min_value=1.0, max_value=10.0, step=0.1, format="%.1f", width="small"),
            "定位": st.column_config.SelectColumn("定位", options=[1, 2, 3],
                help="1=首发 2=轮换 3=边缘", width="small"),
            "核心": st.column_config.CheckboxColumn("核心", width="small"),
            "伤病": st.column_config.CheckboxColumn("伤病", width="small"),
            "吃牌": st.column_config.NumberColumn("吃牌", min_value=0, step=1, width="small"),
        },
        num_rows="dynamic",
        use_container_width=True,
        height=520,
        key="squad_editor",
    )

    col_save, col_del, col_export, col_import = st.columns([1, 1, 1, 2])

    with col_save:
        if st.button("💾 保存名单", type="primary", use_container_width=True):
            try:
                new_squad = df_to_squad(
                    team_name=selected,
                    df=edited_df,
                    group=new_group if new_group else squad.group,
                    coach=new_coach if new_coach else squad.coach,
                )
                if len(new_squad.players) != 26:
                    st.error(f"名单必须恰好26名球员，当前有{len(new_squad.players)}人")
                else:
                    new_squad.updated_at = datetime.now().isoformat()
                    save_squad(new_squad)
                    st.success("✅ 名单已保存")
                    st.rerun()
            except Exception as e:
                st.error(f"保存失败: {e}")

    with col_del:
        if st.button("🗑️ 删除球队", use_container_width=True, type="secondary"):
            st.session_state.confirm_delete = selected
            st.rerun()

    if st.session_state.get("confirm_delete") == selected:
        st.warning(f"确认删除「{selected}」？此操作不可撤销。")
        c1, c2 = st.columns([1, 1])
        with c1:
            if st.button("✅ 确认删除", use_container_width=True):
                delete_squad(selected)
                st.session_state.confirm_delete = None
                st.success(f"已删除: {selected}")
                st.rerun()
        with c2:
            if st.button("❌ 取消", use_container_width=True):
                st.session_state.confirm_delete = None
                st.rerun()

    with col_export:
        if st.button("📤 导出JSON", use_container_width=True):
            squad_refresh = load_squad(selected)
            if squad_refresh:
                json_str = json.dumps(
                    squad_refresh.model_dump(mode="json"),
                    ensure_ascii=False, indent=2,
                )
                st.download_button(
                    label="下载 JSON",
                    data=json_str,
                    file_name=f"{selected.lower().replace(' ', '_')}_squad.json",
                    mime="application/json",
                    use_container_width=True,
                )

    with col_import:
        uploaded = st.file_uploader(
            "📥 导入JSON覆盖名单", type=["json"],
            help="上传符合格式的JSON名单文件，将完全覆盖当前名单",
        )
        if uploaded is not None:
            try:
                data = json.loads(uploaded.read().decode("utf-8"))
                imported = Squad(**data)
                if len(imported.players) != 26:
                    st.error(f"导入的名单有{len(imported.players)}人，必须恰好26人")
                else:
                    if st.button("确认导入覆盖"):
                        imported.updated_at = datetime.now().isoformat()
                        save_squad(imported)
                        st.success(f"已导入: {imported.team_name}")
                        st.rerun()
            except Exception as e:
                st.error(f"JSON解析失败: {e}")


def _batch_seed():
    st.markdown("---")
    with st.expander("🔄 一键导入预置球队数据"):
        st.markdown("点击下方按钮快速创建预置球队（巴西、苏格兰、瑞士、波黑）。如球队已存在则跳过。")
        if st.button("导入4支预置球队"):
            count = 0
            for squad in _seed_data():
                name = squad.team_name
                existing = load_squad(name)
                if existing:
                    st.info(f"跳过: {name} (已存在)")
                    continue
                squad.updated_at = datetime.now().isoformat()
                save_squad(squad)
                count += 1
                st.success(f"已导入: {name}")
            if count > 0:
                st.rerun()


def _seed_data() -> list[Squad]:
    return all_seed_squads()


def main():
    st.title("📋 名单管理")
    st.markdown("管理各队26人大名单，支持增删改查和JSON导入导出。")

    tab1, tab2 = st.tabs(["✏️ 编辑名单", "ℹ️ 使用说明"])
    with tab1:
        _edit_page()
        _batch_seed()
    with tab2:
        st.markdown("""
        ### 使用说明
        - **新建球队**: 点击「新建球队」按钮，填写名称后创建空白26人名单
        - **编辑球员**: 直接在表格中修改数据
        - **位置选项**: GK(门将) CB(中卫) LB(左后卫) RB(右后卫) WB(边翼卫)
          DM(防守中场) CM(中场) AM(进攻中场) LW(左边锋) RW(右边锋) ST(中锋) CF(二前锋)
        - **定位说明**: 1=首发主力 2=轮换替补 3=边缘/备选
        - **导入导出**: 支持JSON格式的名单导入导出，方便批量操作
        - **自动保存**: 修改后必须点击「保存名单」才会持久化
        """)
