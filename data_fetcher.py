import requests
import pandas as pd
import json
import os
from datetime import datetime

class DataManager:
    def __init__(self):
        self.cache_file = "movie_cache.json"
        self.last_update = None
        
    def get_data(self, force_update=False):
        """智能数据获取：优先缓存，失败时使用备份数据"""
        # 检查缓存是否有效（每24小时更新）
        if os.path.exists(self.cache_file) and not force_update:
            cache_time = datetime.fromtimestamp(os.path.getmtime(self.cache_file))
            if (datetime.now() - cache_time).days < 1:
                return self.load_cache()
        
        try:
            data = self.fetch_from_api()
            self.save_cache(data)
            return data
        except Exception as e:
            print(f"API获取失败: {e}")
            return self.local_backup()
    
    def fetch_from_api(self):
        """从多数据源获取电影数据"""
        sources = [
            self.fetch_douban,
            self.fetch_tmdb_trending
        ]
        
        combined_df = pd.DataFrame()
        for source in sources:
            try:
                df = source()
                if not df.empty:
                    combined_df = pd.concat([combined_df, df], ignore_index=True)
                    print(f"从 {source.__name__} 获取 {len(df)} 部电影")
            except Exception as e:
                print(f"数据源错误: {e}")
        
        return combined_df.drop_duplicates(subset=['id'])
    
    def fetch_douban(self):
        """豆瓣TOP250数据"""
        url = "https://movie.douban.com/j/search_subjects"
        params = {
            'type': 'movie',
            'tag': '豆瓣高分',
            'sort': 'recommend',
            'page_limit': 50,
            'page_start': 0
        }
        
        response = requests.get(url, params=params, timeout=10, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36...'
        })
        data = response.json()
        
        movies = []
        for item in data.get('subjects', [])[:30]:  # 限制数量避免超时
            movies.append({
                'id': f"douban_{item['id']}",
                'title': item['title'],
                'rating': float(item['rate']),
                'genres': ', '.join(item.get('genres', [])),
                'year': item.get('year', ''),
                'image': item.get('cover', ''),
                'source': '豆瓣'
            })
        return pd.DataFrame(movies)
    
    def fetch_tmdb_trending(self):
        """TMDB流行电影数据"""
        API_KEY = "0ff215f4577a99b477310a7d9ea0b1d3"  # 公共API Key
        url = f"https://api.themoviedb.org/3/trending/movie/week?api_key={API_KEY}"
        
        response = requests.get(url, timeout=8)
        data = response.json()
        
        movies = []
        for item in data.get('results', [])[:30]:
            movies.append({
                'id': f"tmdb_{item['id']}",
                'title': item['title'],
                'rating': item.get('vote_average', 0),
                'genres': self.map_tmdb_genres(item.get('genre_ids', [])),
                'year': item.get('release_date', '')[:4] if item.get('release_date') else '',
                'image': f"https://image.tmdb.org/t/p/w500{item['poster_path']}" if item['poster_path'] else '',
                'source': 'TMDB'
            })
        return pd.DataFrame(movies)
    
    def map_tmdb_genres(self, genre_ids):
        """将TMDB类型ID转换为文字"""
        genre_map = {
            28: '动作', 12: '冒险', 16: '动画', 35: '喜剧', 
            80: '犯罪', 18: '剧情', 10751: '家庭', 14: '奇幻'
        }
        return ', '.join(genre_map.get(id, '') for id in genre_ids if id in genre_map)
    
    def local_backup(self):
        """本地备份数据"""
        return pd.DataFrame([
            {'id': 'backup1', 'title': '肖申克的救赎', 'rating': 9.7, 'genres': '剧情,犯罪',
             'year': '1994', 'image': 'https://example.com/poster1.jpg', 'source': '本地'},
            # 增加更多备份电影...
        ])
    
    def save_cache(self, data):
        """保存数据到缓存"""
        data.to_json(self.cache_file, orient='records')
        self.last_update = datetime.now()
    
    def load_cache(self):
        """从缓存加载数据"""
        return pd.read_json(self.cache_file)
