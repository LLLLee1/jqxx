import requests
import json
import re
from urllib.parse import quote
import streamlit as st

class RealTimeMovieAPI:
    def __init__(self):
        self.sources = {
            'tmdb': {
                'api_key': '0ff215f4577a99b477310a7d9ea0b1d3',
                'search_url': 'https://api.themoviedb.org/3/search/movie?api_key={}&query={}',
                'details_url': 'https://api.themoviedb.org/3/movie/{}?api_key={}'
            },
            'douban': {
                'search_url': 'https://movie.douban.com/j/subject_suggest?q={}',
                'details_url': 'https://api.douban.com/v2/movie/subject/{}'
            }
        }
        self.platforms = {
            'iqiyi': 'https://so.iqiyi.com/so/q_{}',
            'youku': 'https://so.youku.com/search_video/q_{}',
            'tencent': 'https://v.qq.com/x/search?q={}',
            'mangguo': 'https://so.mgtv.com/so/k-{}',
            'bilibili': 'https://search.bilibili.com/all?keyword={}&from_source=web_search'
        }
    
    def get_movie_data(self, title):
        """获取电影完整信息"""
        result = {
            'title': title,
            'rating': 0.0,
            'year': '',
            'genres': '',
            'poster': '',
            'platform_links': {},
            'source': ''
        }
        
        # 尝试从TMDB获取
        tmdb_data = self._search_tmdb(title)
        if tmdb_data:
            result.update(tmdb_data)
            result['source'] = 'TMDB'
        else:
            # 从豆瓣获取
            douban_data = self._search_douban(title)
            if douban_data:
                result.update(douban_data)
                result['source'] = '豆瓣'
        
        # 生成平台链接
        if not result['platform_links']:
            result['platform_links'] = self._generate_platform_links(title)
        
        return result
    
    def _search_tmdb(self, title):
        """搜索TMDB API获取电影信息"""
        try:
            # 搜索电影
            search_url = self.sources['tmdb']['search_url'].format(
                self.sources['tmdb']['api_key'], quote(title))
            search_resp = requests.get(search_url, timeout=5)
            
            if search_resp.status_code != 200:
                return None
                
            search_data = search_resp.json()
            if not search_data['results']:
                return None
                
            # 获取最匹配的电影ID
            movie_id = search_data['results'][0]['id']
            
            # 获取详情
            details_url = self.sources['tmdb']['details_url'].format(
                movie_id, self.sources['tmdb']['api_key'])
            details_resp = requests.get(details_url, timeout=5)
            details_data = details_resp.json()
            
            # 提取所需信息
            return {
                'title': details_data['title'],
                'rating': details_data.get('vote_average', 0),
                'year': details_data.get('release_date', '')[:4],
                'genres': ', '.join([g['name'] for g in details_data.get('genres', [])]),
                'poster': f"https://image.tmdb.org/t/p/w500{details_data['poster_path']}" if details_data.get('poster_path') else ''
            }
        except Exception as e:
            st.error(f"TMDB查询错误: {e}")
            return None
    
    def _search_douban(self, title):
        """搜索豆瓣API获取电影信息"""
        try:
            # 搜索电影
            search_url = self.sources['douban']['search_url'].format(quote(title))
            search_resp = requests.get(search_url, timeout=5, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            })
            
            if search_resp.status_code != 200:
                return None
                
            search_data = search_resp.json()
            if not search_data:
                return None
                
            # 获取最匹配的电影
            best_match = search_data[0]
            
            # 获取豆瓣ID
            douban_id = best_match['id']
            
            # 获取详情（豆瓣API有时限，这里直接提取)
            return {
                'title': best_match['title'],
                'rating': float(best_match.get('rating', '0')) if best_match.get('rating') else 0.0,
                'year': best_match.get('year', ''),
                'genres': ', '.join(best_match.get('genres', [])),
                'poster': best_match.get('img', '')
            }
        except Exception as e:
            st.error(f"豆瓣查询错误: {e}")
            return None
    
    def _generate_platform_links(self, title):
        """生成各大平台的搜索链接"""
        encoded_title = quote(title)
        return {
            '爱奇艺': self.platforms['iqiyi'].format(encoded_title),
            '优酷': self.platforms['youku'].format(encoded_title),
            '腾讯视频': self.platforms['tencent'].format(encoded_title),
            '芒果TV': self.platforms['mangguo'].format(encoded_title),
            '哔哩哔哩': self.platforms['bilibili'].format(encoded_title),
            '豆瓣电影': f'https://search.douban.com/movie/subject_search?search_text={encoded_title}'
        }
    
    def get_similar_movies(self, title):
        """获取相似电影（基于关键词）"""
        # 实际应用中这里可以连接推荐算法API
        return [
            f"{title} 续集",
            f"{title} 前传",
            f"类似{title}的电影",
            f"与{title}同类型的电影"
        ]
