import urllib.request
import urllib.parse
import ssl
import json
import pymysql
import time
import re
import hashlib
from tools import randomAgent,getCookie,all_citys,read_file,write_file

#示例网址
#https://www.lagou.com/jobs/list_Java?city=杭州

ssl._create_default_https_context = ssl._create_unverified_context

class Lagou(object):
    '''
    eg:
        lagou = Lagou('杭州','Java')
        lagou.open_url()


    公有方法:
        open_url():                 指定爬虫爬取任务
        traversal(req):     遍历当前页面
            req:        当前页面的请求
        open_sub_url(link):          获取子页面的内容
            link:                子页面的url
        read_db(sql = 'select * from lagou'):    读取数据库中的信息进行细节爬取
            sql = 'select * from lagou': 默认读取数据库中的全部数据


    私有方法:
        __config_headers():        配置headers
        __memory(message):    将数据存储到数据库
            message:      待存入的字典
        __sub_memory(result): 将子页面数据存储到数据库
            result:             待存入的子页面元组

    '''
    def __init__(self, city, query):

        if city in all_citys:
            self.city = city
        else:
            print("输入的城市信息有误,已自动切换至全国")
            self.city = '全国'

        self.__city = self.city
        self.__query = query
        self.city = urllib.request.quote(self.city)
        self.query = urllib.request.quote(query)

        self.referer_url = 'https://www.lagou.com/jobs/list_%s?city=%s' % (self.query, self.city)
        self.__config_headers()

        try:
            self.conn = pymysql.connect(host = 'localhost', user = 'root', passwd = 'mac', db = 'Lagou', charset = 'utf8')
        except Exception as err:
            print('数据库初始化失败')
            exit(1)

    def __config_ip_agent(self):

        secret = 'c4cde019e8fc9b17b747c1360d36a3df'
        orderno = 'DT20180423200540GTXBKZRV'

        ip_port = 'dynamic.xiongmaodaili.com:8088'
        timestamp = str(int(time.time()))
        txt = 'orderno=' + orderno + ',' + 'secret=' + secret + ',' + 'timestamp=' + timestamp
        txt = txt.encode()

        md5_string = hashlib.md5(txt).hexdigest()
        sign = md5_string.upper()

        self.__auth = "sign=" + sign + "&" + "orderno=" + orderno + "&" + "timestamp=" + timestamp

        self.__proxy = {"http": "http://" + ip_port, "https": "https://" + ip_port}


    def __config_headers(self):

        #self.__headers = {'Proxy-Authorization' : self.__auth,
                          #'User-Agent' : randomAgent(),
                          #'Referer' : self.referer_url,
                          #'cookie' : getCookie()}
        agent  = ('User-Agent', randomAgent())
        referer = ('Referer', self.referer_url)
        cookie = ("cookie", getCookie())
        self.opener = urllib.request.build_opener()
        self.opener.addheaders = [agent, referer, cookie]

    def open_url(self):
        url = 'https://www.lagou.com/jobs/positionAjax.json?city=%s' % (self.city)
        page_number = 1
        postdata = urllib.parse.urlencode({
            'first' : 'true',
            'pn' : page_number,
            'kd' : self.query
        }).encode('utf-8')
        try:
            req = urllib.request.Request(url, postdata)
            js = json.loads(self.opener.open(req).read().decode('utf-8'))
            #print(js)
            totalCount = js['content']['positionResult']['totalCount']
            resultSize = js['content']['positionResult']['resultSize']
            if totalCount == 0 and resultSize == 0:
                print('暂时没有符合该搜索条件的职位')
                exit(1)
            else:
                page_number = int((totalCount if totalCount % resultSize == 0 else (totalCount + resultSize)) / resultSize)
                for i in range(1, page_number + 1):
                    postdata = urllib.parse.urlencode({
                        'first' : 'true',
                        'pn' : i,
                        'kd' : self.query
                    }).encode('utf-8')
                    req = urllib.request.Request(url, postdata)
                    self.traversal(req)
                self.read_db()
                self.conn.close()
                #print(page_number)
        except Exception as err:
            print(self.open_url.__name__ + " " + str(err))
            self.conn.close()

    def traversal(self, req):
        js = json.loads(self.opener.open(req).read().decode('utf-8'))
        resultSize = js['content']['positionResult']['resultSize']
        result = js['content']['positionResult']['result']
        for i in range(0, resultSize):
            message = {}
            link = 'https://www.lagou.com/jobs/' + str(result[i]['positionId']) + '.html'
            positionName = result[i]['positionName']
            workYear = result[i]['workYear']
            education = result[i]['education']
            salary = result[i]['salary']
            companyShortName = result[i]['companyShortName']
            message['link'] = link
            message['positionName'] = positionName
            message['workYear'] = workYear
            message['education'] = education
            message['salary'] = salary
            message['companyShortName'] = companyShortName
            self.__memory(message)
        self.conn.commit()

    def __memory(self, message):
        sql = "insert into lagou(link, jobtitle, experience, education, salary, company) " \
              "values('"+message['link']+"','"+message['positionName']+"','"+message['workYear']+"','"+message['education']+"','"+message['salary']+"','"+message['companyShortName']+"')"
        try:
            self.conn.query(sql=sql)
        except Exception as err:
            print(self.__memory.__name__ + " " + str(err))

    def read_db(self, sql = 'select * from lagou'):

        try:
            cursor = self.conn.cursor()

            cursor.execute(sql)
            results = cursor.fetchall()

            flag = read_file('./bendi.txt')
            if flag[0] == '':
                start = '0'
            else:
                start = flag[0]

            start = int(start)
            if start >= (len(results) - 1):
                print('执行完毕')
                exit(0)

            for i in range(start, len(results) - 1):
                if i % 8 == 0:
                    time.sleep(2)
                row = results[i]
                link = row[1]
                try:
                    city, brief_info, job_descrip = self.open_sub_url(link, i)

                    jobtitle = row[2]
                    experience = row[3]
                    education = row[4]
                    salary = row[5]
                    company = row[6]
                    result = [jobtitle, experience, education, salary, city, company, brief_info, job_descrip]
                    self.__sub_memory(result)
                except TypeError as err:
                    print(err)

        except Exception as err:
            print(self.read_db.__name__ + " " + str(err))


    def open_sub_url(self, link, i):

        try:
            content =  self.opener.open(link).read().decode('utf-8')
            match_reg = r'<dd class="job_request">.*?<span>(.*?)</span>.*?<ul class="position-label clearfix">(.*?)</ul>.*?<dd class="job_bt">\s+(.*?)\s+</dd>'
            result =  re.findall(match_reg, content, re.S | re.M)
            if len(result) != 0:
                result = result[0]
                print(len(result))
                city = result[0].replace('/','')[:-1]

                print(city)
                brief_info = re.findall(r'<li class="labels">(.*?)</li>', result[1], re.S | re.M)
                brief_info = ','.join(brief_info)
                #print(brief_info)

                job_descrip = re.compile('</?\w+[^>]*>').sub('',result[2])
                job_descrip = job_descrip.replace('&nbsp;','')
                job_descrip = job_descrip.replace('&amp;','')
                #print(job_descrip)
                return city, brief_info, job_descrip
            else:
                #print(content)
                print('正则表达式没有匹配到结果(因为反爬措施或别的状况)')
                write_file([str(i)], './bendi.txt')
                time.sleep(20)
                lagou = Lagou(self.__city, self.__query)
                lagou.read_db()

        except Exception as err:
            print(self.open_sub_url.__name__ + " " + str(err))



    def __sub_memory(self, result):

        sql = "insert into detail_lagou(jobtitle, experience, education, salary, city, company, brief_intro, job_descrip) " \
              "values('"+result[0]+"','"+result[1]+"','"+result[2]+"','"+result[3]+"','"+result[4]+"','"+result[5]+"','"+result[6]+"','"+result[7]+"')"
        try:
            self.conn.query(sql=sql)
            self.conn.commit()
        except Exception as err:
            print(self.__sub_memory.__name__ + " " + str(err))

if __name__ == '__main__':

    lagou = Lagou("杭州", 'Java')
    lagou.open_url()






