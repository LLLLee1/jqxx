import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import re

class SmartRecommender:
    def __init__(self, movie_data):
        self.movies = movie_data
        self._prepare_features()
    
    def _prepare_features(self):
        """创建增强型特征"""
        # 合并关键特征
        self.movies['features'] = (
            self.movies['title'] + ' ' + 
            self.movies['genres'] + ' ' +
            self.movies['year'].astype(str)
        )
        
        # 创建TF-IDF矩阵
        self.tfidf = TfidfVectorizer(stop_words='english')
        self.tfidf_matrix = self.tfidf.fit_transform(self.movies['features'])
        
        # 计算相似度矩阵
        self.cosine_sim = linear_kernel(self.tfidf_matrix, self.tfidf_matrix)
    
    def get_direct_recommendations(self, movie_title, n=5):
        """基于内容直接推荐"""
        idx = self.movies.index[self.movies['title'] == movie_title].tolist()[0]
        sim_scores = list(enumerate(self.cosine_sim[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        sim_indexes = [i[0] for i in sim_scores[1:n+1]]
        return self.movies.iloc[sim_indexes]
    
    def hybrid_recommend(self, preferences, n=10):
        """混合推荐算法"""
        recommendations = pd.DataFrame()
        
        # 类型偏好加权
        for genre_weight in [0.7, 1.0, 1.3]:  # 不同权重尝试
            genre_recs = self.movies.copy()
            for genre in preferences['liked_genres']:
                genre_recs['genre_match'] = genre_recs['genres'].apply(
                    lambda x: 1 if genre in x else 0
                )
                genre_recs['weight'] += genre_weight * genre_recs['genre_match']
            
            recommendations = pd.concat([recommendations, genre_recs.sort_values('weight', ascending=False).head(n//3)])
        
        # 直接推荐合并
        for movie in preferences['liked_movies']:
            if movie in self.movies['title'].values:
                recs = self.get_direct_recommendations(movie, n//3)
                recommendations = pd.concat([recommendations, recs])
        
        # 去重和排序
        recommendations = recommendations.drop_duplicates('id')
        recommendations = recommendations.sort_values(
            ['weight', 'rating'], ascending=[False, False]
        ).head(n)
        
        return recommendations
    
    def filter_recommendations(self, recs, filters):
        """应用用户过滤器"""
        # 年份过滤
        if filters['min_year']:
            recs = recs[recs['year'].astype(int) >= int(filters['min_year'])]
        # 评分过滤
        if filters['min_rating']:
            recs = recs[recs['rating'] >= float(filters['min_rating'])]
        # 类型过滤
        if filter
