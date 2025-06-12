import requests
import pandas as pd
import time

def fetch_douban_data(api_type='top250', pages=3):
    """获取豆瓣电影数据"""
    base_url = {
        'top250': 'https://api.douban.com/v2/movie/top250',
        'in_theaters': 'https://api.douban.com/v2/movie/in_theaters',
        'coming_soon': 'https://api.douban.com/v2/movie/coming_soon'
    }
    
    all_movies = []
    for page in range(pages):
        params = {
            'start': page * 20,
            'count': 20,
            'apikey': '0df993c66c0c636e29ecbb5344252a4a'  # 公开API Key
        }
        
        try:
            response = requests.get(base_url[api_type], params=params, timeout=10)
            data = response.json()
            
            for movie in data['subjects']:
                movie_data = {
                    'id': movie['id'],
                    'title': movie['title'],
                    'rating': movie['rating']['average'],
                    'genres': ','.join(movie['genres']),
                    'year': movie['year'],
                    'directors': ','.join([d['name'] for d in movie['directors']]),
                    'casts': ','.join([c['name'] for c in movie['casts'][:3]]),
                    'image': movie['images']['medium']
                }
                all_movies.append(movie_data)
            time.sleep(1.5)  # 遵守API频率限制
        except Exception as e:
            print(f"获取数据失败: {e}")
    
    return pd.DataFrame(all_movies)
