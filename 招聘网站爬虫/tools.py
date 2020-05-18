import random
import uuid
import urllib.request

#用户代理池构建
USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36",
    "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
    "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
    "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
    "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
    "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",
    "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.11 TaoBrowser/2.0 Safari/536.11",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.71 Safari/537.1 LBBROWSER",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; LBBROWSER)",
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E; LBBROWSER)",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.84 Safari/535.11 LBBROWSER",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E)",
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.89 Safari/537.1",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.89 Safari/537.1",
    "Mozilla/5.0 (iPad; U; CPU OS 4_2_1 like Mac OS X; zh-cn) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8C148 Safari/6533.18.5",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:2.0b13pre) Gecko/20110307 Firefox/4.0b13pre",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:16.0) Gecko/20100101 Firefox/16.0",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11",
    "Mozilla/5.0 (X11; U; Linux x86_64; zh-CN; rv:1.9.2.10) Gecko/20100922 Ubuntu/10.10 (maverick) Firefox/3.6.10"
]

city = {
    '全国' : '100010000',
    '北京' : '101010100',
    '上海' : '101020100',
    '广州' : '101280100',
    '深圳' : '101280600',
    '杭州' : '101210100',
    '天津' : '101030100',
    '西安' : '101110100',
    '苏州' : '101190400',
    '武汉' : '101200100',
    '厦门' : '101230200',
    '长沙' : '101250100',
    '成都' : '101270100',
    '重庆' : '101040100',
    '东莞' : '101281600',
    '佛山' : '101280800',
    '中山' : '101281700',
    '珠海' : '101280700',
    '哈尔滨' : '101050100',
    '长春' : '101060100',
    '沈阳' : '101070100',
    '石家庄' : '101090100',
    '太原' : '101100100',
    '济南' : '101120100',
    '郑州' : '101180100',
    '南京' : '101190100',
    '无锡' : '101190200',
    '合肥' : '101220100',
    '福州' : '101230100',
    '南昌' : '101240100',
    '贵阳' : '101260100',
    '昆明' : '101290100',
    '南宁' : '101300100',
    '海口' : '101310100'
}

usually_citys = ['北京', '上海', '深圳', '广州', '杭州', '成都', '南京', '武汉', '西安', '厦门', '长沙', '苏州', '天津']

all_citys = ['安庆', '澳门特别行政区', '鞍山', '阿克苏',  '阿拉善盟', '安顺', '安阳',
             '北京', '保定', '北海', '包头', '蚌埠', '宝鸡', '滨州', '亳州', '百色', '保山', '白山', '本溪', '白银', '毕节', '巴中',
             '成都', '长沙', '重庆', '常州', '长春', '沧州', '常德', '滁州', '承德', '郴州', '赤峰', '潮州', '昌吉', '池州', '朝阳',
             '东莞', '大连', '德州', '东营', '德阳', '达州', '大理', '大庆', '丹东', '大同', '德宏', '定西', '迪庆',
             '恩施', '鄂尔多斯',
             '佛山', '福州', '阜阳', '抚顺', '抚州', '防城港', '阜新',
             '广州', '贵阳', '桂林', '赣州', '广元', '贵港', '高雄', '甘孜藏族自治州', '广安',
             '杭州', '合肥', '哈尔滨', '惠州', '海口', '呼和浩特', '湖州', '邯郸', '菏泽', '淮安', '黄冈', '衡水', '衡阳', '河源', '黄石', '黄山', '汉中', '贺州', '呼伦贝尔', '淮北', '河池', '怀化', '淮南', '葫芦岛', '红河', '鹤壁', '海西',
             '济南', '嘉兴', '金华', '江门', '济宁', '揭阳', '荆州', '吉安', '吉林', '晋中', '九江', '晋城', '焦作', '景德镇', '酒泉', '锦州', '鸡西',
             '昆明', '开封', '克拉玛依',
             '廊坊', '兰州', '临沂', '洛阳', '柳州', '拉萨', '连云港', '聊城', '丽水', '乐山', '泸州', '临汾', '龙岩', '漯河', '六安', '丽江', '莱芜', '林芝', '六盘水', '凉山彝族自治州', '辽阳', '吕梁', '娄底', '来宾',
             '绵阳', '梅州', '马鞍山', '眉山', '茂名', '牡丹江',
             '南京', '宁波', '南昌', '南宁', '南通', '南充', '南阳', '宁德', '内江', '南平',
             '莆田', '濮阳', '盘锦', '平顶山', '平凉', '攀枝花', '萍乡',
             '青岛', '泉州', '秦皇岛', '清远', '衢州', '曲靖', '黔东南', '齐齐哈尔', '庆阳', '黔西南', '黔南', '钦州',
             '日照',
             '上海', '深圳', '苏州', '沈阳', '石家庄', '绍兴', '汕头', '三亚', '上饶', '韶关', '汕尾', '商丘', '十堰','宿迁', '三明', '邵阳', '三沙', '遂宁', '随州', '三门峡', '宿州', '松原', '石嘴山', '商洛', '山南',
             '天津', '太原', '唐山', '台州', '泰安', '泰州', '台北', '天水', '通辽', '铜仁', '铜陵', '台中',
             '武汉', '无锡', '温州', '乌鲁木齐', '潍坊', '芜湖', '威海', '梧州', '渭南', '武威', '文山', '乌兰察布',
             '西安', '厦门', '徐州', '西宁', '香港特别行政区', '咸阳', '新乡', '襄阳', '邢台', '湘潭', '咸宁', '信阳', '许昌', '新余', '宣城', '孝感', '忻州', '新北', '湘西土家族苗族自治州', '兴安盟', '锡林郭勒盟',
             '烟台', '扬州', '银川', '盐城', '宜昌', '宜宾', '岳阳', '宜春', '永州', '榆林', '阳江', '益阳', '玉林', '营口', '运城', '云浮', '阳泉', '伊犁', '雅安', '鹰潭', '延边', '玉溪',
             '郑州', '珠海', '中山', '肇庆', '淄博', '镇江', '湛江', '株洲', '漳州', '遵义', '驻马店', '资阳', '张家口', '张家界', '长治', '中卫', '周口', '舟山', '昭通', '枣庄']

def randomAgent():
    thisua = random.choice(USER_AGENTS)
    return thisua

# uuid4通过伪随机数得到uuid，是有一定概率重复的
def getUuid():
    return str(uuid.uuid4())

def getCookie():
    return "JSESSIONID=" + getUuid() + ";" + "user_trace_token=" + getUuid() + "; LGUID=" + getUuid() + "; index_location_city=" + urllib.request.quote(random.sample(usually_citys, 1)[0]) + "; " "SEARCH_ID=" + getUuid() + '; _gid=GA1.2.717841549.1514043316; ' '_ga=GA1.2.952298646.1514043316; ' 'LGSID=' + getUuid() + "; " "LGRID=" + getUuid() + "; "

def getCityNumber(cityName):
    return city[cityName]

def write_file(array,file):
    arr_str = ','.join(array)
    with open(file, 'w') as f:
        f.write(arr_str)

def read_file(file):
    try:
        with open(file, 'r') as f:
            array = f.read().split(',')
            return array
    except FileNotFoundError as err:
        print(err)
        exit(0)
