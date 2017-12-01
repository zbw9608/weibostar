# -*- coding: utf-8 -*-
from __future__ import division   #解决语言编码问题
import sys
import re
import os
import random
import time
import datetime

reload(sys)
sys.setdefaultencoding('utf-8')
from selenium import webdriver
executable_path = '/home/zbw/pycharm-2016.1.4/geckodriver'
browser = webdriver.Firefox(executable_path=executable_path)# 启动浏览器
# browser.get('http://www.gdufs.edu.cn/')

def login():
    """
    进行微博的手动登陆
    :return: null
    """
    browser.get("http://weibo.com/")
    while True:
        flag = raw_input('继续请输入Y，否则按任意键')
        if flag.upper() == 'Y':
            break

def movie_id():
    '''
    找到每个id名对应的电影名字
    :return: 电影id对应电影名字典
    '''
    name_id = {}
    for i in range(2010,2018):
        with open('/home/zbw/PycharmProjects/weibo/data/MovieData/' + str(i) + '.json', 'r') as f:
            content = f.read()
        id_pattern = re.compile('\"id\":(\d+)')
        id_list = re.findall(id_pattern,content)
        name_pattern = re.compile('\"MovieName\":(\S+)')
        name_list = re.findall(name_pattern,content)
        for j in range(len(id_list)):
            name_id[id_list[j]] = name_list[j]
    return name_id

def movie_actor():
    '''
    通过文件名id找到对应的电影，文件里的明星则为该部电影的主创
    :return:电影的相关主演字典
    '''
    name_id = movie_id()
    movie_actor = {}
    for i in range(2010,2018):
        path = '/home/zbw/PycharmProjects/weibo/data/MovieActorData/' + str(i) + '/'
        file_list = os.listdir(path)
        for j in file_list:
            file_path = path + j
            actor_list = []
            # print file_path
            with open(file_path, 'r') as f:
                lines = f.readlines()
                for line in lines:
                    string = line.split('	')
                    actor = string[0]
                    actor_list.append(actor)
                # print actor_list
            movie_actor[name_id[j]] = actor_list
    return movie_actor

def add_all(number_list):
    result = 0
    for each in number_list:
        result += int(each)
    if len(number_list) == 0:
        result = 0
    else:
        result = int(result / len(number_list))
    return result

def time_process(time_list):
    time_line = []
    day = {}
    result = 0
    for each in time_list:
        tokens = each.split(' ')
        time_line.append(tokens[0])
    i = 0
    for items in time_line:
        # print items
        if u'今天' in items:
            day[i] = datetime.datetime(2017, 11, 14)
        elif u'月' in items:
            tokens1 = items.split('月')
            day[i] = datetime.datetime(2017, int(tokens1[0]), int(tokens1[1].replace('日', '')))
        else:
            tokens2 = items.split('-')
            day[i] = datetime.datetime(int(tokens2[0]), int(tokens2[1]), int(tokens2[2]))
        # print day[i]
        i += 1

    for j in range(len(day)):
        if j == (len(day) - 1):
            break
        result += (day[j] - day[j + 1]).days
    if len(day) == 0:
        result = 0
    else:
        result = int(result / len(day))
    return result

def actor_getWeiboUrl(actor_name):
    '''
    得到主创的微博主页
    :param actor_name: 演员名
    :return:
    '''
    url = 'https://weibo.cn/n/' + actor_name
    browser.get(url)
    html = browser.page_source
    with open('/home/zbw/PycharmProjects/weibo/data/starHtml/' + actor_name + '.txt', 'w') as fw:
        fw.write(html)
    if u'此用户不存在或更改了名字' in html:
        print actor_name + '用户不存在'
        info = actor_name + ',null'
    elif u'<span class="cmt">共' in html:
        print actor_name + '用户名字没找对'
        info = actor_name + ',null'
    elif u'抱歉，未找到' in html:
        print actor_name + '用户名字没找到'
        info = actor_name + ',null'
    elif u'转发' and u'评论' and u'赞' in html:
        fans_pattern = re.compile('fans">' + u'粉丝' + '\[(\d+)\]</a>')
        fans_result = re.findall(fans_pattern,html)

        follows_pattern = re.compile('follow">' + u'关注' + '\[(\d+)\]</a>')
        follows_result = re.findall(follows_pattern,html)

        weibo_pattern = re.compile('<span class="tc">' + u'微博' + '\[(\d+)\]</span>')
        weibo_result = re.findall(weibo_pattern,html)

        repost_pattern = re.compile('=0">' + u'转发' + '\[(\d+)\]</a>')
        repost_each = add_all(re.findall(repost_pattern,html))

        comment_pattern = re.compile('"cc">' + u'评论' + '\[(\d+)\]</a>')
        comment_each = add_all(re.findall(comment_pattern,html))

        good_pattern = re.compile(u'赞' + '\[(\d+)\]</a>')
        good_each = add_all(re.findall(good_pattern,html))

        time_pattern = re.compile('"ct">(.*?)' + u'&nbsp;来')
        time_each = time_process(re.findall(time_pattern,html))

        info = actor_name + ',' + fans_result[0] + ',' + follows_result[0] + ',' + weibo_result[0] + ',' \
               + str(repost_each) + ',' + str(comment_each) + ',' + str(good_each) + ',' + str(time_each)
    else:
        print actor_name + '被微博误伤了'
        info = actor_name + ',null'
    return info

if __name__ == '__main__':
    login()
    movie_star = movie_actor()
    moviename_id = movie_id()
    for i in range(2010,2018):
        path = '/home/zbw/PycharmProjects/weibo/data/MovieActorData/' + str(i) + '/'
        file_list = os.listdir(path)# 爬取文件夹中的各个文件
        # print file_list
        for j in file_list:
            star_list = movie_star[moviename_id[j]]
            print moviename_id[j]
            if os.path.exists('/home/zbw/PycharmProjects/weibo/data/weiboActor/' + str(i) + '/' + moviename_id[j] + '.txt'):
                continue
            else:
                with open('/home/zbw/PycharmProjects/weibo/data/weiboActor/' + str(i) + '/' + moviename_id[j] + '.txt', 'w') as f:
                    for they in star_list:
                        n = random.randint(1, 6)
                        time.sleep(n)
                        f.write(actor_getWeiboUrl(they) + '\n')