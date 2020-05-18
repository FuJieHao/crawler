from lagou import Lagou
from zhilian import Zhilian
from boss import Boss
import time
import datetime

def do_task(city, query):
    boss = Boss(city, query)
    boss.open_url()

    lagou = Lagou(city, query)
    lagou.open_url()

    zhilian = Zhilian(city, query)
    zhilian.open_url()

def timer(margin_hour = 6, margin_min = 5):
    while True:
        while True:
            now = datetime.datetime.now()

            if now.hour % margin_hour == 0:
                break
            time.sleep(60 * margin_min)

        do_task('杭州', 'Java')
        time.sleep(60 * 60)

if __name__ == '__main__':
    timer()


