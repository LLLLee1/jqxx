import streamlit as st
import pandas as pd
from data_fetcher import fetch_douban_data
from recommender import MovieRecommender

# 初始化数据
@st.cache_resource
def load_data():
    return fetch_douban_data(pages=5)

# 页面布局
st.title("🎬 智能电影推荐系统")
st.markdown("基于豆瓣TOP250电影数据，分析您的观影偏好")

# 侧边栏控制
st.sidebar.header("控制面板")
selected_movies = st.sidebar.multiselect(
    "选择您喜欢的电影",
    options=load_data()['title'].tolist()
)

# 主内容区
if selected_movies:
    recommender = MovieRecommender(load_data())
    recommendations = recommender.recommend(selected_movies)
    
    st.subheader("为您推荐的电影")
    cols = st.columns(3)
    
    for idx, row in recommendations.iterrows():
        with cols[idx % 3]:
            st.image(row['image'], width=150)
            st.markdown(f"**{row['title']}** ({row['year']})")
            st.caption(f"类型: {row['genres']}")
            st.caption(f"导演: {row['directors'].split(',')[0]}")
            st.caption(f"⭐ 评分: {row['rating']}")
else:
    st.info("请在左侧选择您喜欢的电影开启推荐")
