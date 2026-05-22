import streamlit as st

st.set_page_config(
    page_title="2026世界杯推演系统",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.sidebar.markdown(
    "<h1 style='text-align: center; font-size: 1.5rem;'>⚽ 2026世界杯<br>推演系统</h1>",
    unsafe_allow_html=True,
)
st.sidebar.markdown("---")

pages = {
    "📋 名单管理": "pages/01_squad_manager",
    "📊 6维分析": "pages/02_squad_analysis",
    "💰 赔率面板": "pages/03_odds_dashboard",
    "🎯 交叉参考": "pages/04_cross_reference",
    "🔄 比赛模拟": "pages/05_match_simulation",
}

selected = st.sidebar.radio("导航", list(pages.keys()), label_visibility="collapsed")

st.sidebar.markdown("---")
st.sidebar.caption("v1.0 | 数据存储于本地 JSON")

page_path = pages[selected]

try:
    module = __import__(page_path.replace("/", "."), fromlist=["main"])
    if hasattr(module, "main"):
        module.main()
    else:
        st.info(f"页面「{selected}」正在开发中...")
except Exception as e:
    st.error(f"页面加载失败: {e}")
