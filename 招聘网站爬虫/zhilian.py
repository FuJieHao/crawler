import urllib.request
import ssl
from tools import randomAgent
import pymysql
import re
import time

#https://www.zhaopin.com/
#https://sou.zhaopin.com/jobs/searchresult.ashx?jl=%E6%9D%AD%E5%B7%9E&kw=IOS&sm=0&p=1
#http://jobs.zhaopin.com/CZ365191030J00049039908.htm

ssl._create_default_https_context = ssl._create_unverified_context

class Zhilian(object):
    '''
    eg:
        zhilian = Zhilian('杭州','Java')
        zhilian.open_url()


    公有方法:
        open_url():                 指定爬虫爬取任务
        traversal(url):     遍历当前页面
            url:        当前页面的请求
        open_sub_url(link):          获取子页面的内容
            link:                子页面的url
        read_db(sql = 'select * from zhilian'):    读取数据库中的信息进行细节爬取
            sql = 'select * from zhilian': 默认读取数据库中的全部数据


    私有方法:
        __config_headers():        配置headers
        __memory(result):    将数据存储到数据库
            result:      待存入的数组
        __sub_memory(message): 将子页面数据存储到数据库
            message:             待存入的子页面数组

    '''

    def __init__(self, city, query, sort = '默认排序', CONTENT_SIZE = 60):

        self.city = urllib.request.quote(city)
        self.query = urllib.request.quote(query)
        self.CONTENT_SIZE = CONTENT_SIZE
        try:
            self.__sort = {
                            '默认排序' : '0',
                            '相关度'   : '1',
                            '首发日'   : '2'
                            }[sort]
        except KeyError:
            print('sort 值错误,改为默认排序')
            self.__sort = '0'

        self.url = 'https://sou.zhaopin.com/jobs/searchresult.ashx?jl=%s&kw=%s&sb=%s&p=1' \
                   % (self.city, self.query, self.__sort)

        self.__config_headers()

        try:
            self.conn = pymysql.connect(host = 'localhost', user = 'root', passwd = 'mac', db = 'Zhilian', charset = 'utf8')
        except Exception as err:
            print('数据库初始化失败')
            exit(1)


        #print(self.url)

    def __config_headers(self):
        agent = ('User-Agent', randomAgent())

        self.opener = urllib.request.build_opener()
        self.opener.addheaders = [agent]

    def open_url(self):

        content =  self.opener.open(self.url).read().decode('utf-8')
        match_reg = r'<span class="search_yx_tj">.*?<em>(.*?)</em>.*?</span>'
        totol_size = re.findall(match_reg, content, re.S | re.M)[0]

        page_number = int(20 if int(totol_size) / self.CONTENT_SIZE >= 20 else (int(totol_size) + self.CONTENT_SIZE) / self.CONTENT_SIZE)
        print(page_number)
        for i in range(0, page_number + 1):
            if i % 6 == 0:
                time.sleep(2)
            url = 'https://sou.zhaopin.com/jobs/searchresult.ashx?jl=%s&kw=%s&sb=%s&p=%s' \
                   % (self.city, self.query, self.__sort, str(i))
            print(url)
            self.traversal(url)

        self.read_db()

        self.conn.close()

    def traversal(self, url):
        content = self.opener.open(url).read().decode('utf-8')
        #print(content)
        match_reg = r'<td class="zwmc".*?href="(.*?)".*?target="_blank">(.*?)<a href.*?target="_blank">(.*?)</a>.*?' \
                    r'<td class="zwyx">(.*?)</td>.*?' \
                    r'<td class="gzdd">(.*?)</td>.*?' \
                    r'<li class="newlist_deatil_two">.*?学历：(.*?)</span>' \

        result = re.findall(match_reg, content, re.S | re.M)

        arr = []
        for i in range(0, len(result)):
            temp = list(result[i])
            zwmc = re.compile('</?\w+[^>]*>').sub('',temp[1])
            zwmc = re.compile('\r\n.*?\s+').sub('',zwmc)
            zwmc = re.compile('[\d.]+%').sub('',zwmc)
            temp[1] = zwmc.replace('&nbsp;', '')
            arr.append(temp)

        for i in range(0, len(arr)):
            self.__memory(arr[i])

    def open_sub_url(self, link):
        #print(link)

        content = self.opener.open(link).read().decode('utf-8')
        match_reg = r'<li><span>工作经验：</span><strong>(.*?)</strong></li>.*?<div class="tab-inner-cont">\n(.*?)工作地址'
        result = re.findall(match_reg, content, re.S | re.M)[0]
        temp = list(result)
        gwzz = temp[1].replace('<br/>', '\n')
        gwzz = gwzz.replace('</p><p>', '\n')
        gwzz = gwzz.replace('&nbsp;', '')
        gwzz = re.compile('</?\w+[^>]*>').sub('',gwzz)
        experience = temp[0]

        return experience, gwzz

    def __memory(self, result):
        #link jobtitle company salary city  education
        sql = "insert into zhilian(link, jobtitle, company, salary, city, education) " \
              "values('"+result[0]+"','"+result[1]+"','"+result[2]+"','"+result[3]+"','"+result[4]+"','"+result[5]+"')"
        try:
            self.conn.query(sql=sql)
            self.conn.commit()
        except Exception as err:
            print(self.__memory.__name__ + " " + str(err))


    def __sub_memory(self, message):

        sql = "insert into detail_zhilian(jobtitle, company, salary, city, education, experience, job_descrip) " \
              "values('"+message[0]+"','"+message[1]+"','"+message[2]+"','"+message[3]+"','"+message[4]+"','"+message[5]+"','"+message[6]+"')"
        try:
            self.conn.query(sql=sql)
            self.conn.commit()
        except Exception as err:
            print(self.__sub_memory.__name__ + " " + str(err))


    def read_db(self, sql = 'select * from zhilian'):

        cusor = self.conn.cursor()

        cusor.execute(sql)
        result = cusor.fetchall()

        for i in range(0, len(result)):
            if i % 8 == 0:
                time.sleep(2)
            row = result[i]
            link = row[1]

            try:
                experience, gwzz =  self.open_sub_url(link)
                jobtitle = row[2]
                company = row[3]
                salary = row[4]
                city = row[5]
                education = row[6]
                message = [jobtitle, company, salary, city, education, experience, gwzz]
                self.__sub_memory(message)
            except Exception as err:
                print(err)


if __name__ == '__main__':

    zhilian = Zhilian('杭州', 'Java')
    zhilian.open_url()

