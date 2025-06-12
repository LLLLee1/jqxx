import streamlit as st
import time
import random
import pandas as pd
from api_service import RealTimeMovieAPI
from recommender import FilmRecommender

# 初始化服务
api_service = RealTimeMovieAPI()
recommender = FilmRecommender()

# 配置页面
st.set_page_config(
    page_title="影视数据库直连推荐系统",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化会话状态
if 'user_history' not in st.session_state:
    st.session_state.user_history = []

if 'current_recommendations' not in st.session_state:
    st.session_state.current_recommendations = []

if 'movie_input' not in st.session_state:
    st.session_state.movie_input = ""

# 用户输入区域 - 顶部标题
st.title("🎬 影视数据库直连推荐系统")
st.markdown("输入您喜欢的电影，系统实时连接各大影视平台为您推荐")

# 主布局
col1, col2 = st.columns([1, 2])

with col1:
    # 用户输入面板
    with st.container(border=True):
        st.subheader("添加您喜欢的电影")
        
        # 电影输入 - 使用安全的session_state访问方式
        movie_title = st.text_input(
            "输入电影名称:",
            placeholder="例如：肖申克的救赎",
            value=st.session_state.movie_input,
            key="new_movie_input"
        )
        
        # 添加按钮
        if st.button("添加到列表", type="primary", use_container_width=True):
            if movie_title and movie_title.strip():
                # 更新session_state的正确方式
                st.session_state.movie_input = movie_title.strip()
                
                # 添加到历史记录
                if st.session_state.movie_input not in st.session_state.user_history:
                    st.session_state.user_history.append(st.session_state.movie_input)
                    
                    # 重置输入框
                    st.session_state.new_movie_input = ""
                    st.rerun()
        
        # 历史记录
        if st.session_state.user_history:
            st.markdown("---")
            st.subheader("您的观影历史")
            for idx, title in enumerate(st.session_state.user_history):
                movie_col, btn_col = st.columns([4, 1])
                movie_col.markdown(f"• {title}")
                if btn_col.button("X", key=f"del_{idx}"):
                    st.session_state.user_history.remove(title)
                    st.rerun()

# 推荐结果展示区
with col2:
    # 推荐生成区域
    if st.session_state.user_history:
        # 生成推荐按钮
        if st.button("生成推荐", type="primary", use_container_width=True):
            with st.spinner("正在连接到影视平台获取推荐..."):
                # 模拟连接多个平台
                for platform in ["TMDB", "豆瓣", "爱奇艺", "腾讯视频"]:
                    time.sleep(0.5)
                    st.toast(f"连接到 {platform}...", icon="🔍")
                
                # 实际生成推荐
                recommendations = recommender.recommend_for_user(
                    st.session_state.user_history
                )
                
                # 获取电影详情
                detailed_recs = []
                for title in recommendations:
                    # 确保不添加重复的推荐
                    if not any(rec.get('title') == title for rec in st.session_state.current_recommendations):
                        movie_data = api_service.get_movie_data(title)
                        if movie_data:  # 确保数据获取成功
                            detailed_recs.append(movie_data)
                
                # 更新推荐列表
                st.session_state.current_recommendations = detailed_recs
                
                if detailed_recs:
                    st.success(f"成功获取 {len(detailed_recs)} 条推荐！")
                else:
                    st.warning("未能获取推荐，请尝试其他电影")
    
    # 显示推荐结果
    if st.session_state.current_recommendations:
        st.subheader("为您推荐以下电影:")
        
        # 电影分组显示
        recs = st.session_state.current_recommendations[:6]  # 只显示前6个
        
        # 第一行
        cols = st.columns(3)
        for idx in range(3):
            if idx < len(recs):
                movie = recs[idx]
                with cols[idx]:
                    display_movie_card(movie)
        
        # 第二行
        if len(recs) > 3:
            cols = st.columns(3)
            for idx in range(3, 6):
                if idx < len(recs):
                    movie = recs[idx]
                    with cols[idx - 3]:
                        display_movie_card(movie)
    
    else:
        st.info("请添加您喜欢的电影后点击【生成推荐】")
        
        # 显示电影搜索示例 - 使用安全的回调函数
        st.markdown("### 热门电影搜索示例")
        examples = st.columns(3)
        sample_movies = ["肖申克的救赎", "阿凡达", "霸王别姬", "盗梦空间", "星际穿越", "泰坦尼克号"]
        for i, movie_title in enumerate(sample_movies):
            with examples[i % 3]:
                # 使用回调函数安全设置输入
                if st.button(movie_title, 
                           use_container_width=True, 
                           key=f"sample_{i}",
                           on_click=lambda m=movie_title: set_movie_input(m)):
                    pass

def display_movie_card(movie):
    """显示电影卡片组件"""
    with st.container(border=True, height=350):
        # 电影海报
        if movie.get('poster'):
            st.image(movie['poster'], use_column_width=True)
        else:
            st.warning("无海报可用")
        
        # 电影信息
        st.markdown(f"#### {movie.get('title', '未知电影')}")
        if movie.get('year'):
            st.caption(f"年份: {movie['year']}")
        if movie.get('rating'):
            st.caption(f"评分: ⭐ {movie['rating']:.1f}")
        if movie.get('source'):
            st.caption(f"数据来源: {movie['source']}")
        
        # 观看平台链接
        if movie.get('platform_links'):
            st.markdown("**观看平台:**")
            # 显示前3个平台
            platforms = list(movie['platform_links'].keys())[:3]
            links = list(movie['platform_links'].values())[:3]
            
            for platform, link in zip(platforms, links):
                st.markdown(f"- [{platform}]({link})", unsafe_allow_html=True)
        
        # 添加到历史按钮
        if st.button("添加到我的电影", 
                   key=f"add_{movie.get('title', 'unknown')}", 
                   use_container_width=True,
                   on_click=lambda t=movie.get('title', '未知电影'): add_to_history(t)):
            pass

def add_to_history(movie_title):
    """安全地添加到历史记录"""
    if movie_title and movie_title not in st.session_state.user_history:
        st.session_state.user_history.append(movie_title)

def set_movie_input(movie_title):
    """安全地设置输入值"""
    st.session_state.new_movie_input = movie_title
