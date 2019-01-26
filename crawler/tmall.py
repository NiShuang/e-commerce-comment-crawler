# -*- coding: UTF-8 -*-

import requests
import json
import time
import sys

from database import db_util, config

reload(sys)
sys.setdefaultencoding("utf-8")

class tm_crawler:
    def __init__(self):
        self.conn = db_util.get_mysql_db(config.collection_database)
        self.cursor = self.conn.cursor()

    def __del__(self):
        self.conn.close()


    def get_comment(self,product_id, seller_id, product):
        url = 'https://rate.tmall.com/list_detail_rate.htm'
        params = {
            # 'itemId': 576234268379
            # 'spuId': 1047568219
            # 'sellerId': 2300650542
            'order': 3,
            # 'currentPage': 1,
            'append': 0,
            'content': 1,
            'tagId': '',
            'posi': '',
            'picture': '',
            'groupId': '',
            'ua': config.tm['ua'],
            'needFold': 0,
            # '_ksTS': '1548141137019_1510',
            'callback': ''
        }
        headers = {
            'accept-encoding': 'gzip, deflate, br',
            'accept': '*/*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'no-cache',
            'pragma': 'no-cache',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
            'cookie': config.tm['cookie']

        }

        page = 1
        while(True):
            params['itemId'] = product_id,
            params['sellerId'] = seller_id,
            params['currentPage'] = page
            response = requests.get(url=url, params=params, headers=headers)
            data = response.text
            data = data.split('(',1)[1][:-1]
            try:
                json_object = json.loads(data, "utf-8")
            except:
                print 'error' + ':' + data

                time.sleep(60)
                continue
            comments = json_object['rateDetail']['rateList']
            print json.dumps(comments)
            if len(comments) == 0:
                break
            self.save(comments, product)
            page += 1
            time.sleep(3)



    def save(self, comments, product):
        records = []
        for comment in comments:
            record = (
                str(comment['id']),
                comment['rateContent'],
                comment['auctionSku'],
                comment['rateDate'],
                product
            )
            records.append(record)
        sql = 'INSERT IGNORE INTO comment_tmall(id,content,sku,create_time,product) VALUES (%s,%s,%s,%s,%s)'

        try:
            # 执行SQL语句
            self.cursor.executemany(sql, records)
            # 提交修改
            self.conn.commit()
        except Exception, e:
            print e.message

if __name__ == '__main__':
    product_list = [
        ('576234268379', '2300650542', 'GoPro HERO7 Black'),
        ('582824628900', '2300650542', 'GoPro HERO7 Black定制红色礼盒'),
        ('576619832841', '3989130132', 'GoPro HERO7 Black数码相机'),
        ('577602676541', '4126927072', '[相机租赁]GoPro官方租赁gopro hero'),
        ('579983391128', '3262708088', 'GoPro HERO7 BLACK 定制礼盒'),
        ('578046655549', '3881723271', '[相机租赁]GoPro HERO 7 BLACK运动'),
        ('578047716117', '4132533044', 'GoPro HERO 7 BLACK蜜月套装'),
        ('578575129762', '3262708088', 'GoPro HERO7 Black 礼盒（电池）'),
        ('577602676541', '4126927072', '[相机租赁]GoPro官方租赁gopro hero'),
        ('576843933320', '4115186725', '[相机租赁]GoPro HERO7/6/5 BLACK'),
        ('582610188977', '2300650542', 'GoPro HERO7系列')
    ]
    crawler = tm_crawler()
    for product in product_list:
        crawler.get_comment(product[0], product[1], product[2])