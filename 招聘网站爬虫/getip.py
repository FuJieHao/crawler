import urllib.request
import json
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

#http://www.xiongmaodaili.com/freeproxy
url = 'http://www.xiongmaodaili.com/xiongmao-web/api/glip?secret=c4cde019e8fc9b17b747c1360d36a3df&orderNo=GL201804202055021tuDwa4n&count=20&isTxt=0'
def get_array(url):
    ip_js = json.loads(urllib.request.urlopen(url).read().decode('utf-8'))
    ip_arr = ip_js['obj']

    array = []
    for i in range(0, len(ip_arr)):

        array.append(str(ip_arr[i]['ip']) + ':' + str(ip_arr[i]['port']))
    return array


#检测ip是否可用
def confirm_ip(ip):
    #配置proxy
    proxy = {'http' : 'http://%s' % ip}
    proxy_handler = urllib.request.ProxyHandler(proxy)
    opener = urllib.request.build_opener(proxy_handler)

    test_url = 'http://httpbin.org/ip'
    try:
        opener.open(test_url,timeout=10).read()
        return ip
    except Exception as err :
        print(err)
        return None

def ip_pool():
    array = get_array(url)
    ip_array = []

    for i in range(0, len(array)):
        ip = confirm_ip(array[i])
        if ip != None:
            ip_array.append(ip)
    return ip_array
