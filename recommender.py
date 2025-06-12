import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from collections import defaultdict

class FilmRecommender:
    def __init__(self, user_history=None):
        self.user_history = user_history if user_history else []
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self._build_knowledge_base()
        
    def _build_knowledge_base(self):
        """构建电影知识库（实际应用中连接到大型数据库）"""
        # 这里简化处理，实际应用应该连接到影视数据库
        self.movies = pd.DataFrame([
            {'title': '肖申克的救赎', 'genres': '剧情,犯罪', 'keywords': '监狱,希望,自由'},
            {'title': '阿凡达', 'genres': '动作,科幻,冒险', 'keywords': '外星人,特效,3D'},
            {'title': '泰坦尼克号', 'genres': '剧情,爱情,灾难', 'keywords': '海洋,爱情,沉船'},
            {'title': '盗梦空间', 'genres': '科幻,悬疑,冒险', 'keywords': '梦境,时间,多层'},
            {'title': '星际穿越', 'genres': '科幻,冒险,剧情', 'keywords': '太空,时间,亲情'},
            {'title': '霸王别姬', 'genres': '剧情,爱情,历史', 'keywords': '京剧,同性,时代变迁'},
            {'title': '这个杀手不太冷', 'genres': '剧情,动作,犯罪', 'keywords': '杀手,女孩,复仇'},
            {'title': '千与千寻', 'genres': '动画,奇幻,冒险', 'keywords': '日本,神隐,成长'},
            {'title': '楚门的世界', 'genres': '剧情,科幻', 'keywords': '真人秀,虚假,自由'}
        ])
        
        # 提取特征
        self.movies['features'] = self.movies['genres'] + ' ' + self.movies['keywords']
        
        # 训练向量模型
        self.tfidf_matrix = self.vectorizer.fit_transform(self.movies['features'])
        self.cosine_sim = cosine_similarity(self.tfidf_matrix, self.tfidf_matrix)
        self.idx_mapping = {title: idx for idx, title in enumerate(self.movies['title'])}
    
    def recommend_for_movie(self, title, top_n=5):
        """为单部电影推荐类似影片"""
        if title not in self.idx_mapping:
            # 如果未知电影，返回通用推荐
            return self.movies.sample(top_n)['title'].tolist()
        
        idx = self.idx_mapping[title]
        sim_scores = list(enumerate(self.cosine_sim[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        sim_indexes = [i[0] for i in sim_scores[1:top_n+1]]
        return self.movies.iloc[sim_indexes]['title'].tolist()
    
    def recommend_for_user(self, titles, top_n=10):
        """基于用户观看历史推荐"""
        recommendations = defaultdict(float)
        
        # 为每部观看的电影获取推荐
        for title in titles:
            similar = self.recommend_for_movie(title, top_n=8)
            for similar_title in similar:
                recommendations[similar_title] += 1.0
                
            # 在推荐中加入一些随机性
            random_recs = self.movies.sample(3)['title'].tolist()
            for random_title in random_recs:
                recommendations[random_title] += 0.3
        
        # 排除用户已经看过的
        for title in titles:
            if title in recommendations:
                del recommendations[title]
                
        # 按权重排序
        sorted_recs = sorted(recommendations.items(), key=lambda x: x[1], reverse=True)
        return [title for title, score in sorted_recs[:top_n]]
