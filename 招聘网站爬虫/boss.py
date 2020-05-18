import urllib.request
from tools import getCityNumber,randomAgent
import re
import time
import ssl
import pymysql
import hashlib
import requests

#示例网址
#https://www.zhipin.com/c101210100/h_100010000/?query=iOS&page=1

#关闭ssl安全验证
ssl._create_default_https_context = ssl._create_unverified_context
#忽略requests的警告
requests.packages.urllib3.disable_warnings()
#增加重试链接次数
requests.adapters.DEFAULT_RETRIES = 5


class Boss(object):
    '''
    eg:
        boss = Boss('杭州','Java')
        boss.open_url()
    公有方法:
        open_url():                 指定爬虫爬取任务
        traversal(page_number):     循环爬取网页
            page_number:        待爬取的页数
        open_sub_url(url):          获取子页面的内容
            url:                子页面的url
        read_db(sql = 'select * from boss'):    读取数据库中的信息进行细节爬取
            sql = 'select * from boss': 默认读取数据库中的全部数据
        get_info():                 查看类内公有属性


    私有方法:
        __config_ip_agent():        配置ip代理
        __memory(message_tuple):    将数据存储到数据库
            message_tuple:      待存入的元组
        __sub_memory(result): 将子页面数据存储到数据库
            result:             待存入的子页面元组

    '''
    def __init__(self, city, query, CONTENT_SIZE = 30):
        self.CONTENT_SIZE = CONTENT_SIZE
        try:
            self.city = getCityNumber(city)
        except KeyError as err:
            print('没有您要查找的地区',err,',已为您自动改为全国')
            self.city = getCityNumber('全国')

        self.query = urllib.request.quote(query)
        self.url = 'https://www.zhipin.com/c%s/h_%s/?query=%s&page=1' % (self.city, getCityNumber('全国'), self.query)

        self.__config_ip_agent()
        try:
            self.conn = pymysql.connect(host = 'localhost', user = 'root', passwd = 'mac', db = 'Boss', charset = 'utf8')
        except Exception as err:
            print('数据库初始化失败')
            exit(1)

    def __config_ip_agent(self):

        secret = 'c4cde019e8fc9b17b747c1360d36a3df'
        orderno = 'DT20180423185056pK2Iqhve'

        ip_port = 'dynamic.xiongmaodaili.com:8088'
        #proxy = {'http' : 'http://%s' % ip_port}

        timestamp = str(int(time.time()))
        txt = 'orderno=' + orderno + ',' + 'secret=' + secret + ',' + 'timestamp=' + timestamp
        txt = txt.encode()

        md5_string = hashlib.md5(txt).hexdigest()
        sign = md5_string.upper()

        auth = "sign=" + sign + "&" + "orderno=" + orderno + "&" + "timestamp=" + timestamp

        self.__proxy = {"http": "http://" + ip_port, "https": "https://" + ip_port}
        self.__headers = {"Proxy-Authorization" : auth,
                          'User-Agent' : randomAgent()}

    def open_url(self):

        try:

            r = requests.get(url=self.url, headers=self.__headers, proxies=self.__proxy, verify=False,allow_redirects=False)
            content = r.content.decode('utf-8')
            count_url = r"(?<=data-rescount=\").+?(?=\")|(?<=data-rescount=\').+?(?=\')"
            total = re.findall(count_url, content,  re.I|re.S|re.M)[0]
            page_number = int((int(total) if int(total) % self.CONTENT_SIZE == 0 else (int(total) + self.CONTENT_SIZE)) / self.CONTENT_SIZE)
            page_number = 10 if page_number > 10 else page_number

            self.traversal(page_number)

            self.read_db()
            #print(content)
            self.conn.close()

        except Exception as err:
            print(self.open_url.__name__ + " " + str(err))
            self.conn.close()

    def open_sub_url(self, url):

        self.__headers['User-Agent'] = randomAgent()
        try:
            r = requests.get(url=url, headers=self.__headers, proxies=self.__proxy, verify=False,allow_redirects=False)
            #print(r.status_code)
            if r.status_code == 200:
                content = r.content.decode('utf-8')

                match_reg = r'<div id="main">.*?<div class="info-primary">.*?' \
                        r'<div class="name"><h1>(.*?)</h1>.*?<span class="badge">(.*?)</span></div>.*?' \
                        r'<p>城市：(.*?)<em class="vline"></em>经验：(.*?)<em class="vline"></em>学历：(.*?)</p>.*?' \
                        r'<div class="job-tags">\s+(.*?)\s+</div>.*?' \
                        r'<h3>职位描述</h3>.*?<div class="text">\s+(.*?)\s+</div>'
                result =  re.findall(match_reg, content, re.S | re.M)[0]

                self.__sub_memory(list(result))
        except Exception as err:
            print(self.open_sub_url.__name__ + " " + str(err))

    def read_db(self, sql = 'select * from boss'):

        try:
            cursor = self.conn.cursor()

            cursor.execute(sql)
            results = cursor.fetchall()
            for i in range(0, len(results) - 1):
                if i % 4 == 0:
                    time.sleep(1)

                row = results[i]
                link = row[1]
                self.open_sub_url(link)
        except Exception as err:
            print(self.read_db.__name__ + " " + str(err))

    def traversal(self, page_number):

        for i in range(1, page_number + 1):
            try:
                self.__headers['User-Agent'] = randomAgent()
                url = self.url[:-1] + str(i)
                r = requests.get(url=url, headers=self.__headers, proxies=self.__proxy, verify=False,allow_redirects=False)
                content = r.content.decode('utf-8')
                match_reg = r'<div class="job-list">(.*?)<div class="page">'
                match_str = re.findall(match_reg,content,re.S|re.M)[0]
                #print(match_str)
                res_reg = r'<li>.*?<a href="(.*?)".*?<div class="job-title">(.*?)</div>.*?<span class="red">(.*?)</span>.*?<a href=.*?>(.*?)</a>.*?</li>'
                res_list = re.findall(res_reg,match_str,re.S|re.M)
                for message_tuple in res_list:
                    self.__memory(message_tuple=list(message_tuple))
                if (i % (int(page_number / 2)) == 0) :
                    time.sleep(2)
            except Exception as err:
                print(self.traversal.__name__ + " " + str(err))
        self.conn.commit()



    def __memory(self, message_tuple):
        message_tuple[0] = 'https://www.zhipin.com/' + message_tuple[0]
        sql = "insert into boss(link, jobtitle, salary, company) " \
              "values('"+message_tuple[0]+"','"+message_tuple[1]+"','"+message_tuple[2]+"','"+message_tuple[3]+"')"
        try:
            self.conn.query(sql=sql)
        except Exception as err:
            print(self.__memory.__name__ + " " + str(err))

    def __sub_memory(self, result):

        jobtitle    = result[0]
        salary      = result[1]
        city        = result[2]
        experience  = result[3]
        education   = result[4]
        brief_intro = result[5]
        brief_intro = brief_intro.replace('<span>','')
        brief_intro = brief_intro.replace('</span>',',')[:-1]
        job_descrip = result[6]
        job_descrip = job_descrip.replace('<br/><br/>', '\n')
        job_descrip = job_descrip.replace('<br/>', '\n')

        sql = "insert into detail_boss(jobtitle, salary, city, experience, education, brief_intro, job_descrip) " \
              "values('"+jobtitle+"','"+salary+"','"+city+"','"+experience+"','"+education+"','"+brief_intro+"','"+job_descrip+"')"
        try:
            self.conn.query(sql=sql)
            self.conn.commit()
        except Exception as err:
            print(self.__sub_memory.__name__ + " " + str(err))

    def get_info(self):
        print(self.city)
        print(self.query)
        print(self.CONTENT_SIZE)
        print(self.url)


if __name__ == '__main__':

    boss = Boss('杭州','Java')
    boss.open_url()

