import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class MovieRecommender:
    def __init__(self, movie_df):
        self.movies = movie_df
        self._build_feature_matrix()
    
    def _build_feature_matrix(self):
        """创建电影特征矩阵"""
        self.movies['features'] = self.movies['genres'] + ' ' + self.movies['directors'] + ' ' + self.movies['casts']
        self.vectorizer = TfidfVectorizer()
        self.feature_matrix = self.vectorizer.fit_transform(self.movies['features'])
    
    def recommend(self, liked_movies, top_n=10):
        """基于内容推荐"""
        # 构建用户偏好向量
        user_features = ' '.join(self.movies[self.movies['title'] == title]['features'].values[0] 
                                for title in liked_movies)
        user_vector = self.vectorizer.transform([user_features])
        
        # 计算相似度
        sim_scores = cosine_similarity(user_vector, self.feature_matrix).flatten()
        self.movies['similarity'] = sim_scores
        
        # 排除已看过的电影
        recommendations = self.movies[~self.movies['title'].isin(liked_movies)]
        return recommendations.sort_values('similarity', ascending=False).head(top_n)
