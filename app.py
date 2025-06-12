import streamlit as st
import pandas as pd
from data_fetcher import fetch_douban_data
from recommender import MovieRecommender

# 初始化数据（增加异常处理）
@st.cache_resource
def load_data():
    try:
        data = fetch_douban_data()
        # 确保DataFrame包含必要列
        required_cols = ['id', 'title', 'rating', 'genres', 'image']
        for col in required_cols:
            if col not in data.columns:
                data[col] = None
        return data
    except Exception as e:
        st.error(f"数据加载失败: {e}")
        return get_local_backup_data()

# 页面布局优化
st.set_page_config(
    page_title="智能电影推荐系统", 
    page_icon="🎬",
    layout="wide"
)

# 状态提示区域
status_area = st.empty()

try:
    movie_data = load_data()
    # 确保标题列存在
    if 'title' in movie_data.columns and not movie_data.empty:
        title_list = movie_data['title'].tolist()
    else:
        title_list = [f"电影ID: {id}" for id in movie_data['id']] if 'id' in movie_data.columns else ["无可用数据"]
    
    # 侧边栏控制
    with st.sidebar:
        st.header("控制面板")
        selected_movies = st.multiselect(
            "选择您喜欢的电影",
            options=title_list,
            help="至少选择一部电影以生成推荐"
        )
        st.divider()
        st.caption(f"数据库: {len(movie_data)}部电影")
        if st.button("刷新数据"):
            st.cache_resource.clear()
            st.rerun()
    
    # 主内容区
    status_area.success(f"成功加载{len(movie_data)}部电影数据")
    
    if selected_movies:
        recommender = MovieRecommender(movie_data)
        
        # 获取推荐结果
        with st.spinner("正在生成推荐..."):
            recommendations = recommender.recommend(
                [m for m in selected_movies if any(m in t for t in title_list)]
            )
        
        st.subheader(f"为您推荐 {len(recommendations)} 部电影")
        
        # 分栏展示
        cols = st.columns(3)
        for idx, row in recommendations.iterrows():
            with cols[idx % 3]:
                with st.container(border=True):
                    if row['image']:
                        st.image(row['image'], width=200)
                    else:
                        st.warning("海报未加载")
                    st.markdown(f"### {row['title']} ({row['year']})")
                    st.caption(f"⭐ 评分: {row['rating']} | 类型: {row['genres']}")
                    if pd.notna(row['directors']):
                        st.caption(f"导演: {row['directors'].split(',')[0]}")
    else:
        st.info("请从左侧选择您喜欢的电影开启推荐")
        st.divider()
        
        # 显示热门电影
        st.subheader("热门电影")
        popular = movie_data.sort_values('rating', ascending=False).head(9)
        for i in range(0, len(popular), 3):
            cols = st.columns(3)
            for j in range(3):
                idx = i + j
                if idx < len(popular):
                    with cols[j]:
                        st.image(popular.iloc[idx]['image'], width=150)
                        st.caption(f"{popular.iloc[idx]['title']} ({popular.iloc[idx]['year']})")

except Exception as e:
    status_area.error(f"系统错误: {e}")
    st.exception(e)  # 显示详细错误信息
