import sys
import traceback
from collections import OrderedDict
from datetime import datetime
from time import sleep
import pandas as pd

import requests
from config import *


class data_spider:
    def __init__(self):
        self.headers = {
            "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36"
        }
        self.cookie = {'Cookie': weibo_config['cookie']}  # 微博cookie，可填可不填 if you wanna collect your own weibo data, you should use the cookie after signing in
        self.user = {}  # 存储目标微博用户信息 user information
        self.got_count = 0  # 存储爬取到的微博数
        self.weibo = []  # 存储爬取到的所有微博信息
        self.weibo_id_list = []  # 存储爬取到的所有微博id
        self.comments = [] # 存储爬取到的所有评论
        self.mysql_config = weibo_config['mysql_config']


    def spider_weibo(self):
        self.get_user_info()
        page = 1
        is_end = False
        since_id = ''
        wrote_count = 0
        while not is_end:
            is_end, since_id = self.get_one_page(page, since_id)
            self.weibo_to_mysql(wrote_count)
            wrote_count = self.got_count
            page += 1
        self.to_csv()

    def get_user_info(self):
        url = 'https://weibo.com/ajax/profile/info?uid=%s' %weibo_config['user_id']
        r = requests.get(url, cookies=self.cookie)
        js = r.json()
        if js['ok']:
            info = js['data']['user']
            user_info = {}
            user_info['id'] = weibo_config['user_id']
            user_info['screen_name'] = info.get('screen_name', '')
            user_info['gender'] = info.get('gender', '')
            user_info['statuses_count'] = info.get('statuses_count', 0)
            user_info['followers_count'] = info.get('followers_count', 0)
            user_info['friends_count'] = info.get('friends_count', 0)
            user_info['description'] = info.get('description', '')
            user_info['profile_url'] = info.get('profile_url', '')
            user_info['profile_image_url'] = info.get('profile_image_url', '')
            user_info['avatar_hd'] = info.get('avatar_hd', '')
            user_info['mbrank'] = info.get('mbrank', 0)
            user_info['verified'] = info.get('verified', False)
            user_info['verified_type'] = info.get('verified_type', 0)
            user_info['verified_reason'] = info.get('verified_reason', '')
            user = self.standardize_info(user_info)
            self.user = user


    def standardize_info(self, weibo):
        """标准化信息，去除乱码"""
        for k, v in weibo.items():
            if 'bool' not in str(type(v)) and 'int' not in str(type(v)) \
                    and 'list' not in str(type(v)) and 'long' not in str(type(v))\
                    and 'datetime.datetime' not in str(type(v)):
                weibo[k] = v.replace(u"\u200b", "").encode(
                    sys.stdout.encoding, "ignore").decode(sys.stdout.encoding)
        return weibo


    def get_one_page(self, page, since_id):
        """获取一页的全部微博"""
        try:
            js = self.get_weibo_json(page, since_id)
            since_id = js['data']['since_id']
            if js['ok'] and js['data']['list'] != []: #determine whether reach the last page 判断是否到达最后一页。最后一页的list为空列表
                weibos = js['data']['list']
                for weibo_info in weibos:
                    wb = self.parse_weibo(weibo_info)
                    if wb:
                        if wb['id'] in self.weibo_id_list:
                            continue
                        self.weibo.append(wb)
                        self.weibo_id_list.append(wb['id'])
                        self.got_count += 1
                        print(u'\n{}已获取第{}页微博"{}"{}'.format(
                            '*' * 10,
                            page,
                            wb['text'][:8],
                            '*' * 10))
                print(u'{}已获取{}({})的第{}页全部的微博{}'.format('-' * 30,
                                                        self.user['screen_name'],
                                                        self.user['id'],
                                                        page,
                                                        '-' * 30))
                sleep(3)
                return False, since_id
            else: #得到空列表，返回is_end = True 和 since_id = ''
                return True, since_id

        except Exception as e:
            print("Error: ", e)
            traceback.print_exc()


    def parse_weibo(self, weibo_info):
        weibo = OrderedDict()
        if weibo_info.get('title'): # 去除"置顶"和"赞过"(爬他人微博时用到）
            return
        if weibo_info['user']:
            weibo['user_id'] = weibo_info['user']['id']
            weibo['screen_name'] = weibo_info['user']['screen_name']
        else:
            weibo['user_id'] = ''
            weibo['screen_name'] = ''
        weibo['id'] = weibo_info['id']
        weibo['mblogid'] = weibo_info['mblogid']
        weibo['text'] = weibo_info['text_raw']
        weibo['pics'] = self.get_pics(weibo_info)
        weibo['video_url'] = self.get_video_url(weibo_info)
        weibo['location'] = weibo_info.get('region_name','')
        weibo['created_at'] = datetime.strptime(
            weibo_info['created_at'], '%a %b %d %H:%M:%S %z %Y')
        weibo['created_at'] = weibo['created_at'].replace(tzinfo=None)
        weibo['source'] = weibo_info['source']
        weibo['attitudes_count'] = weibo_info.get('attitudes_count', 0)
        weibo['comments_count'] = weibo_info.get('comments_count', 0)
        if weibo['comments_count'] > 0:
            weibo['comments'] = self.get_comments(weibo_info)
        else:
            weibo['comments'] = ''
        weibo['reposts_count'] = weibo_info.get('reposts_count', 0)
        if weibo_info.get('isLongText'):
            weibo['text'] = self.get_long_text(weibo_info)
        if weibo_info.get('retweeted_status'):
            if weibo_info.get('retweeted_status')['isLongText']:
                weibo['retweet_content'] = self.get_long_text(weibo_info.get('retweeted_status'))
            else:
                weibo['retweet_content'] = weibo_info.get('retweeted_status')['text_raw']
        else:
            weibo['retweet_content'] = ''
        return self.standardize_info(weibo)


    def get_comments(self,weibo_info):
        url = 'https://weibo.com/ajax/statuses/buildComments?is_reload=1&id=%s&is_show_bulletin=2&is_mix=0&count=20&type=feed&uid=7415065856' %  weibo_info['id']
        r = requests.get(url, cookies=self.cookie)
        js = r.json()
        comments = []
        def get_all_comment(info):
            for i, data in enumerate(info):
                comments.append(str(i+1) + '. ')
                comments.append(data["user"]["screen_name"] + ": " + data["text_raw"] + "/")
                if data.get('comments',""):
                    get_all_comment(data['comments'])
                else:
                    return
        get_all_comment(js['data'])
        return "--".join(comments)


    def get_long_text(self,weibo_info):
        url = 'https://weibo.com/ajax/statuses/longtext?id=%s' % weibo_info['mblogid']
        try:
            r = requests.get(url, cookies=self.cookie)
            js = r.json()
            return js['data'].get('longTextContent','')
        except:
            print('敏感信息')
            return weibo_info['text_raw']


    def get_pics(self, weibo_info):
        """获取微博原始图片url"""
        if weibo_info.get('pic_ids'):
            pic_list = []
            pic_info = weibo_info['pic_infos']
            for id in weibo_info['pic_ids']:
                pic_list.append(pic_info[id]['original']['url'])
            pics = ','.join(pic_list)
        else:
            pics = ''
        return pics


    def get_live_photo(self, weibo_info):
        """获取live photo中的视频url"""
        live_photo_list = []
        if weibo_info.get('pic_ids'):
            pic_info = weibo_info['pic_infos']
            for id in weibo_info['pic_ids']:
                if pic_info[id]['type'] == 'livephoto':
                    live_photo_list.append(pic_info[id]['video'])
            return ','.join(live_photo_list)


    def get_video_url(self, weibo_info):
        """获取微博视频url"""
        video_url = ''
        video_url_list = []
        if weibo_info.get('page_info'):
            if weibo_info['page_info'].get('media_info') and weibo_info[
                    'page_info'].get('object_type') == 'video':
                media_info = weibo_info['page_info']['media_info']
                video_url = media_info.get('mp4_720p_mp4')
                if not video_url:
                    video_url = media_info.get('mp4_hd_url')
                    if not video_url:
                        video_url = media_info.get('mp4_sd_url')
                        if not video_url:
                            video_url = media_info.get('stream_url_hd')
                            if not video_url:
                                video_url = media_info.get('stream_url')
        if video_url:
            video_url_list.append(video_url)
        live_photo_list = self.get_live_photo(weibo_info)
        if live_photo_list:
            video_url_list += live_photo_list
        return ';'.join(video_url_list)


    def get_weibo_json(self, page, since_id):
        """获取网页中微博json数据"""
        if since_id != '':
            params = {
                'page': page,
                'feature': 0,
                'since_id': since_id
            }
        else:  # 第一页的url没有since_id这个参数
            params = {
                'page': page,
                'feature': 0
            }
        url = 'https://weibo.com/ajax/statuses/mymblog?uid=%s' % weibo_config['user_id']
        r = requests.get(url, params=params, cookies=self.cookie)
        return r.json()


    def weibo_to_mysql(self, wrote_count):
        """将爬取的微博信息写入MySQL数据库"""
        mysql_config = {
        }
        info_list = self.weibo[wrote_count:]
        # 在'weibo'表中插入或更新微博数据
        self.mysql_insert(mysql_config, 'weibo', info_list)
        print(u'%d条微博写入MySQL数据库完毕' % self.got_count)


    def mysql_insert(self, mysql_config, table, data_list):
        """向MySQL表插入或更新数据"""
        import pymysql

        if len(data_list) > 0:
            keys = ', '.join(data_list[0].keys())
            values = ', '.join(['%s'] * len(data_list[0]))
            if self.mysql_config:
                mysql_config = self.mysql_config
            connection = pymysql.connect(**mysql_config)
            cursor = connection.cursor()
            sql = """INSERT INTO {table}({keys}) VALUES ({values}) ON
                     DUPLICATE KEY UPDATE""".format(table=table,
                                                    keys=keys,
                                                    values=values)
            update: str = ','.join([
                " {key} = values({key})".format(key=key)
                for key in data_list[0]
            ])

            sql += update
            try:
                cursor.executemany(
                    sql, [tuple(data.values()) for data in data_list])
                connection.commit()
            except Exception as e:
                connection.rollback()
                print('Error: ', e)
                traceback.print_exc()
            finally:
                connection.close()

    def to_csv(self):
        df1 = pd.DataFrame(self.weibo)
        df1.to_csv('myweibo.csv')
        df2 = pd.DataFrame(self.user, index=[0])
        df2.to_csv('myweibo_userinfo.csv')


if __name__ == "__main__":
    data_spider = data_spider()
    data_spider.spider_weibo()