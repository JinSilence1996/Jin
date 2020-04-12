#! /usr/bin/env python
# coding=utf-8
'''
网络爬虫第一课
'''

import os
import traceback
from bs4 import BeautifulSoup  # 网页解析，获取数据（需要pip install）
import re  # 正则表达式，进行文字匹配
import urllib, requests, urllib.error, urllib.parse, urllib.request  # 制定URL，获取网页数据
import xlwt  # 进行excel操作（需要pip install）
import sqlite3  # 进行SQLite数据库操作


# BeautifulSoup4将复杂的HTML文档转换成一个复杂的树形结构，每个节点都是Python对象，所有对象可以归纳为4类：
# - bs4.element.Tag                 eg:bs.title, bs.a, bs.head,bs.span,...（标签及其内容）
# - bs4.element.NavigableString     eg:bs.title.string, bs.a.string, bs.head.string,....(标签内的内容）
#   不常用bs.a.attrs                字典
# - bs4.element.BeautifulSoup       eg:bs整个文件
# - bs4.element.Comment             eg:特殊的bs4.element.NavigableString，输出内容不包含注释符号(<!-- -->)
#
# 搜索：
# - find_all('a')/find('a')     只查询a标签
# - find_all(re.compile('a'))   查询含有a的标签
# - 传入函数（方法），根据函数要求来搜索  eg:find_all(foo)
# - find_all(text=re.compile('\d'))   应用正则表达式来查找包括特定文本的内容（标签里的字符串)
# - limit参数，限制查找个数
# - select('div > span')


# 影片链接
findLink = re.compile('<a href="(.*?)">', re.S)
# 影片图片
findImg = re.compile('<img.*src="(.*?)".*/>', re.S) # 让换行符包含在字符中
# 影片片名
findTitle = re.compile('<span class="title">(.*?)</span>', re.S)
# 影片评分
findRating = re.compile('<span class="rating_num" property="v:average">(.*?)</span>', re.S)
# 影片评价人数
findJudgeNum = re.compile('<span>(\d*)人评价</span>', re.S)
# 影片概况
findInq = re.compile('<span class="inq">(.*?)</span>', re.S)
# 影片相关内容
findBd = re.compile('<p class="">(.*?)</p>', re.S)

def getData(baseurl):
    '''
    根据网址爬取网页
    :param baseurl: 网址
    :return:
    '''
    datalst = []
    method = 'POST'
    for i in range(0, 250, 25):
        print(i)
        dictdata = {
            'start': str(i)
        }
        xmldata = askURL(baseurl, dictdata, method)
        # 逐一解析数据
        soup = BeautifulSoup(xmldata, "html.parser")
        movieinfolst = soup.find_all('div', {'class': 'item'})
        for movieinfo in movieinfolst:
            # print(movieinfo)
            movieinfo = str(movieinfo)
            link = ''.join(re.findall(findLink, movieinfo))
            img = ''.join(re.findall(findImg, movieinfo))
            name = ''.join(re.findall(findTitle, movieinfo)).replace('/', '')   # 去掉斜杠
            rating = ''.join(re.findall(findRating, movieinfo))
            judgenum = ''.join(re.findall(findJudgeNum, movieinfo))
            inq = ''.join(re.findall(findInq, movieinfo)).replace('。', '')      # 去掉句号。
            bd = ''.join(re.findall(findBd, movieinfo))
            bd = re.sub('\s+', ' ', bd, re.S)
            bd = re.sub('<br(\s*?)/>(\s*?)', '\n', bd, re.S)
            bd = re.sub('/', ' ', bd, re.S)
            
            # [链接, 图片, 名称, 评分, 评价人数, 概述, 相关信息]
            datalst.append([link, img, name, rating, judgenum, inq, bd.strip()])
        #
        # movienamelst = soup.find_all('span', {'class': ['title', 'other']})
        # for moviename in movienamelst:
        #     movenamestr = moviename.text.replace('/', '').strip()
        #     if movenamestr:
        #         print(movenamestr)
        #         datalst.append(movenamestr)
    datalst.insert(0, ['链接', '图片', '名称', '评分', '评价人数', '概述', '相关信息'])
    return datalst

def askURL(baseurl, dictdata, method):
    # 用户代理，表示告诉网页的服务器，我们是什么类型的机器/浏览器（本质上是告诉浏览器，我们可以接受什么水平的数据）
    # User-Agent大小写敏感，空格敏感
    headers = {
        'charset': 'utf-8',
        'User-Agent':
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/80.0.3987.163 Safari/537.36 Edg/80.0.361.111'
    }
    
    try:
        hosturl = urllib.parse.urlparse(baseurl).netloc
    except Exception as e:
        print(traceback.format_exc())
        hosturl = ''
    if hosturl:
        headers.update({'host': hosturl})
    data = bytes(urllib.parse.urlencode(dictdata), encoding='utf-8')
    request = urllib.request.Request(url=baseurl, data=data, method=method, headers=headers)
    try:
        response = urllib.request.urlopen(request, timeout=3)
        xmldata = (response.read().decode('utf-8'))
    except urllib.error.URLError as e:
        if hasattr(e, 'code'):
            print(e.code)
        xmldata = ''
    return xmldata

def saveData2Xls(savepath, datalst):
    '''
    保存数据到excel
    :param savepath:excel文件路径
    :param datalst:需要保存的数据
    :return:
    '''
    workbook = xlwt.Workbook(encoding='utf-8')
    worksheet = workbook.add_sheet('豆瓣电影TOP250',cell_overwrite_ok=True)
    for row, eachdata in enumerate(datalst):
        for col, onedata in enumerate(eachdata):
            worksheet.write(row, col, onedata)
    workbook.save(savepath)


def saveData2DB(dbpath, datalst):
    # [链接, 图片, 名称, 评分, 评价人数, 概述, 相关信息]
    delsqlstr = 'drop table if exists movie250;'
    createsqlstr = '''
        create table movie250(
            id integer primary key autoincrement,
            info_link text,
            pic_link text,
            name varchar,
            score numeric,
            rated numeric,
            instroduction text,
            info text
        );
    '''
    insertsqlstr = '''
            insert into movie250(
            info_link, pic_link, name, score, rated, instroduction,info)
             values (?,?,?,?,?,?,?)
            '''
    selectsqlstr = '''
            select * from movie250;
    '''
    conn = None
    cur = None
    try:
        conn = sqlite3.connect(dbpath, timeout=10)
        cur = conn.cursor()
        cur.execute(delsqlstr)
        conn.commit()
        cur.execute(createsqlstr)
        conn.commit()
        cur.executemany(insertsqlstr, datalst[1:])
        conn.commit()
        resultdata = cur.execute(selectsqlstr)
        print(resultdata)
    except sqlite3.Error as e:
        print(traceback.format_exc())
        print('save to db failed')
    finally:
        if cur is not None:
            cur.close()
        if conn is not None:
            conn.close()
    

def main():
    print('spider start')
    baseurl = r'https://movie.douban.com/top250'
    # 爬取网页 + 解析数据
    xmldatalst = getData(baseurl)
    # 保存数据
    savepath = os.path.join(os.getcwd(), '豆瓣电影Top250.xls')
    saveData2Xls(savepath, xmldatalst)
    saveData2DB('test.db', xmldatalst)
    print('spider end')


if __name__ == '__main__':
    main()