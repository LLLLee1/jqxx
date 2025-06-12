import streamlit as st
import pandas as pd
import time
from data_fetcher import DataManager
from recommender import SmartRecommender

# 页面配置
st.set_page_config(
    page_title="高级电影推荐系统",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化数据管理器
@st.cache_resource
def get_data_manager():
    return DataManager()

data_manager = get_data_manager()

# 初始化用户会话状态
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = {
        'liked_movies': [],
        'disliked_movies': [],
        'liked_genres': []
    }

if 'movie_data' not in st.session_state:
    with st.spinner('正在加载电影数据库...'):
        st.session_state.movie_data = data_manager.get_data()

# 侧边栏 - 用户控制面板
with st.sidebar:
    st.header("🎯 我的电影偏好")
    
    # 电影选择器
    liked_movies = st.multiselect(
        "选择您喜欢的电影",
        options=st.session_state.movie_data['title'].tolist(),
        default=st.session_state.user_profile['liked_movies'],
        key="liked_movies"
    )
    
    # 类型偏好选择
    all_genres = set()
    for genres in st.session_state.movie_data['genres']:
        all_genres.update(genres.split(', '))
    liked_genres = st.multiselect(
        "偏好的电影类型",
        options=sorted(all_genres),
        default=st.session_state.user_profile['liked_genres']
    )
    
    # 过滤选项
    st.divider()
    st.header("🔍 筛选条件")
    min_year = st.s
