import requests
import pandas as pd
import os
from datetime import datetime
import time
import json
import urllib.parse

class DataManager:
    def __init__(self):
        self.cache_file = "movie_cache.json"
        self.last_update = None
        self.platform_apis = {
            'iqiyi': 'https://pcw-api.iqiyi.com/search/v2/videolists?query={}',
            'youku': 'https://search.youku.com/search.html?keyword={}',
            'qq': 'https://v.qq.com/x/search?q={}',
            'mgtv': 'https://so.mgtv.com/so/k-{}'
        }
        
    def get_data(self, force_update=False):
        """智能数据获取：优先缓存，失败时使用备份数据"""
        # 检查缓存是否有效（每24小时更新）
        if os.path.exists(self.cache_file) and not force_update:
            cache_time = datetime.fromtimestamp(os.path.getmtime(self.cache_file))
            if (datetime.now() - cache_time).days < 1:
                return self.load_cache()
        
        try:
            data = self.fetch_from_api()
            # 为每部电影添加平台链接
            data['platform_links'] = data['title'].apply(self.get_movie_platform_links)
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
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
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
                'image': f"https://image.tmdb.org/t/p/w500{item['poster_path']}" if item.get('poster_path') else '',
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
    
    def get_movie_platform_links(self, title):
        """为电影获取各大平台链接"""
        encoded_title = urllib.parse.quote(title)
        
        # 为每个平台生成链接
        links = {
            '豆瓣': f'https://search.douban.com/movie/subject_search?search_text={encoded_title}',
            '爱奇艺': self.platform_apis['iqiyi'].format(encoded_title),
            '优酷': self.platform_apis['youku'].format(encoded_title),
            '腾讯视频': self.platform_apis['qq'].format(encoded_title),
            '芒果TV': self.platform_apis['mgtv'].format(encoded_title)
        }
        
        # 添加一个通用搜索引擎链接作为后备
        links['全网搜索'] = f'https://www.baidu.com/s?wd={encoded_title}+电影'
        
        return links
    
    def local_backup(self):
        """本地备份数据"""
        backup_data = pd.DataFrame([
            {'id': 'backup1', 'title': '肖申克的救赎', 'rating': 9.7, 'genres': '剧情,犯罪',
             'year': '1994', 'image': 'https://img9.doubanio.com/view/photo/s_ratio_poster/public/p480747492.webp', 'source': '本地'},
            {'id': 'backup2', 'title': '霸王别姬', 'rating': 9.6, 'genres': '剧情,爱情,同性',
             'year': '1993', 'image': 'https://img9.doubanio.com/view/photo/s_ratio_poster/public/p2561716440.webp', 'source': '本地'},
            {'id': 'backup3', 'title': '阿甘正传', 'rating': 9.5, 'genres': '剧情,爱情',
             'year': '1994', 'image': 'https://img1.doubanio.com/view/photo/s_ratio_poster/public/p2372307693.webp', 'source': '本地'},
            {'id': 'backup4', 'title': '泰坦尼克号', 'rating': 9.4, 'genres': '剧情,爱情,灾难',
             'year': '1997', 'image': 'https://img2.doubanio.com/view/photo/s_ratio_poster/public/p457760035.webp', 'source': '本地'},
            {'id': 'backup5', 'title': '这个杀手不太冷', 'rating': 9.4, 'genres': '剧情,动作,犯罪',
             'year': '1994', 'image': 'https://img1.doubanio.com/view/photo/s_ratio_poster/public/p511118051.webp', 'source': '本地'},
        ])
        
        # 为本地备份数据也添加平台链接
        backup_data['platform_links'] = backup_data['title'].apply(self.get_movie_platform_links)
        return backup_data
    
    def save_cache(self, data):
        """保存数据到缓存"""
        data.to_json(self.cache_file, orient='records')
        self.last_update = datetime.now()
    
    def load_cache(self):
        """从缓存加载数据"""
        data = pd.read_json(self.cache_file)
        # 确保平台链接存在
        if 'platform_links' not in data.columns:
            data['platform_links'] = data['title'].apply(self.get_movie_platform_links)
        return data
