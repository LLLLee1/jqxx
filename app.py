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
    min_year = st.slider("最小年份", 1950, 2025, 2000)
    min_rating = st.slider("最低评分", 0.0, 10.0, 7.0, 0.5)
    selected_genres = st.multiselect("包含类型", options=sorted(all_genres))
    
    # 推荐控制
    st.divider()
    st.header("⚙️ 推荐设置")
    rec_count = st.slider("推荐数量", 5, 30, 15)
    if st.button("生成推荐", type="primary", use_container_width=True):
        # 更新用户偏好
        st.session_state.user_profile = {
            'liked_movies': liked_movies,
            'liked_genres': liked_genres,
            'disliked_movies': []
        }
        st.session_state.filters = {
            'min_year': min_year,
            'min_rating': min_rating,
            'genres': selected_genres
        }
        st.rerun()
    
    if st.button("🔄 刷新数据库", use_container_width=True):
        st.session_state.movie_data = data_manager.get_data(force_update=True)
        st.rerun()
    
    st.caption(f"数据库: {len(st.session_state.movie_data)}部电影")
    st.caption(f"最后更新: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}")

# 主界面
st.title("🎬 智能电影推荐引擎")
st.subheader(f"为您个性化精选好电影", divider="blue")

# 推荐结果展示区
if 'user_profile' in st.session_state and st.session_state.user_profile['liked_movies']:
    with st.spinner('正在分析您的偏好并生成推荐...'):
        # 初始化推荐器
        recommender = SmartRecommender(st.session_state.movie_data)
        
        # 生成推荐
        recommendations = recommender.hybrid_recommend(
            st.session_state.user_profile, 
            n=rec_count
        )
        
        # 应用筛选
        if 'filters' in st.session_state:
            recommendations = recommender.filter_recommendations(
                recommendations, st.session_state.filters
            )
    
    # 显示推荐结果
    if len(recommendations) > 0:
        st.success(f"为您找到 {len(recommendations)} 部符合您品味的电影")
        
        # 分列展示
        cols = st.columns(3)
        for idx, row in recommendations.iterrows():
            col = cols[idx % 3]
            with col:
                with st.container(border=True, height=450):
                    if row['image']:
                        st.image(row['image'], use_column_width=True)
                    else:
                        st.warning("无可用海报")
                    
                    st.markdown(f"**{row['title']}** ({row['year']})")
                    st.caption(f"⭐ {row['rating']} | {row['source']}")
                    st.caption(f"类型: {row['genres']}")
                    
                    # 交互按钮
                    btn_cols = st.columns([3,1])
                    with btn_cols[0]:
                        if st.button("查看详情", key=f"detail_{row['id']}", use_container_width=True):
                            st.session_state.selected_movie = row
                    with btn_cols[1]:
                        if st.button("❤️", key=f"like_{row['id']}", use_container_width=True):
                            if row['title'] not in st.session_state.user_profile['liked_movies']:
                                st.session_state.user_profile['liked_movies'].append(row['title'])
                                st.rerun()
    else:
        st.warning("未找到符合筛选条件的电影，请尝试放宽筛选条件")
else:
    # 默认展示 - 电影探索界面
    st.info("在左侧设置您的电影偏好并点击【生成推荐】开始探索")
    
    # 展示热门电影分类
    st.subheader("🎉 热门电影分类", divider="green")
    
    genre_cols = st.columns(4)
    popular_genres = ["动作", "喜剧", "科幻", "剧情"]
    for i, genre in enumerate(popular_genres):
        with genre_cols[i]:
            st.subheader(f"#{genre}")
            genre_movies = st.session_state.movie_data[
                st.session_state.movie_data['genres'].str.contains(genre)
            ].sort_values('rating', ascending=False).head(3)
            
            for _, movie in genre_movies.iterrows():
                with st.expander(f"{movie['title']} ({movie['year']})"):
                    if movie['image']:
                        st.image(movie['image'], width=150)
                    st.caption(f"评分: {movie['rating']}")
                    if st.button("添加到偏好", key=f"add_{movie['id']}"):
                        if movie['title'] not in st.session_state.user_profile['liked_movies']:
                            st.session_state.user_profile['liked_movies'].append(movie['title'])
                            st.rerun()

# 电影详情弹窗
if 'selected_movie' in st.session_state:
    movie = st.session_state.selected_movie
    with st.popover(f"🎥 {movie['title']} 详情", use_container_width=True):
        st.header(movie['title'])
        col1, col2 = st.columns([1,2])
        with col1:
            st.image(movie['image'] if movie['image'] else "", width=200)
        with col2:
            st.subheader(f"({movie['year']}) | ⭐ {movie['rating']}")
            st.caption(f"来源: {movie['source']}")
            st.write(f"**类型**: {movie['genres']}")
            st.write(f"**推荐理由**: 与您喜欢的'{st.session_state.user_profile['liked_movies'][0]}'有相似风格")
            
            if st.button("加入我的收藏", type="primary"):
                if movie['title'] not in st.session_state.user_profile['liked_movies']:
                    st.session_state.user_profile['liked_movies'].append(movie['title'])
                    st.rerun()
