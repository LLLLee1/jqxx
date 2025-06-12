import requests
import pandas as pd
import time
import json

def fetch_douban_data():
    """增强防护的豆瓣数据获取"""
    # 使用多个备份API密钥
    API_KEYS = [
        '0df993c66c0c636e29ecbb5344252a4a', 
        '0dad551ec0f84ed02907ff5c42e8ec70',
        '02646d3f59a6a9938f7d540b6f546b7a'
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
        'Accept': 'application/json',
        'Referer': 'https://movie.douban.com/',
        'Host': 'api.douban.com'
    }
    
    all_movies = []
    for page in range(0, 3):  # 只获取3页数据确保稳定
        url = f"https://api.douban.com/v2/movie/top250?start={page*25}"
        
        for key in API_KEYS:
            params = {'apikey': key}
            try:
                time.sleep(2)  # 遵守API频率限制
                response = requests.get(url, headers=headers, params=params, timeout=15)
                
                # 验证是否返回有效JSON
                try:
                    data = response.json()
                except json.JSONDecodeError:
                    continue  # 尝试下一个API密钥
                
                if 'subjects' not in data:
                    continue  # 数据格式错误
                
                for movie in data['subjects']:
                    movie_data = {
                        'id': movie.get('id', ''),
                        'title': movie.get('title', '未知电影'),
                        'rating': movie.get('rating', {}).get('average', 0),
                        'genres': ','.join(movie.get('genres', [])),
                        'year': movie.get('year', '未知年份'),
                        'directors': ','.join(d['name'] for d in movie.get('directors', [])),
                        'casts': ','.join(c['name'] for c in movie.get('casts', [])[:3]),
                        'image': movie.get('images', {}).get('medium', '')
                    }
                    all_movies.append(movie_data)
                break  # 成功获取后跳出密钥循环
            except Exception as e:
                print(f"API请求失败: {e}")
                
    # 添加本地备份数据
    if not all_movies:
        return get_local_backup_data()
    
    return pd.DataFrame(all_movies)

def get_local_backup_data():
    """本地备份数据"""
    return pd.DataFrame([
        {'id': '1292052', 'title': '肖申克的救赎', 'rating': 9.7, 'genres': '犯罪,剧情', 
         'year': '1994', 'directors': '弗兰克·德拉邦特', 'casts': '蒂姆·罗宾斯,摩根·弗里曼,鲍勃·冈顿', 
         'image': 'https://img9.doubanio.com/view/photo/s_ratio_poster/public/p480747492.webp'},
        {'id': '1291546', 'title': '霸王别姬', 'rating': 9.6, 'genres': '剧情,爱情,同性',
         'year': '1993', 'directors': '陈凯歌', 'casts': '张国荣,张丰毅,巩俐',
         'image': 'https://img9.doubanio.com/view/photo/s_ratio_poster/public/p2561716440.webp'},
        # 添加更多备份电影数据...
    ])
