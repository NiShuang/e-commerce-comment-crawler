# -*- coding: UTF-8 -*-

import requests
import json
from bs4 import BeautifulSoup
import sys

from database import db_util, config

reload(sys)
sys.setdefaultencoding("utf-8")

class amazon_crawler:
    def __init__(self, domain, country):
        self.domain = domain
        self.country = country
        self.conn = db_util.get_mysql_db(config.collection_database)
        self.cursor = self.conn.cursor()

    def __del__(self):
        self.conn.close()


    def get_comment(self,product_id,product):
        url = 'https://www.' + self.domain + '/hz/reviews-render/ajax/reviews/get/ref=cm_cr_arp_d_paging_btm_'
        params = {
            'sortBy': '',
            'reviewerType': 'all_reviews',
            'formatType': '',
            'mediaType': '',
            'filterByStar': '',
            'filterByKeyword': '',
            'shouldAppend': 'undefined',
            'deviceType': 'desktop',
            'pageSize': 10,
            'scope': 'reviewsAjax3'
        }
        headers = {
            'accept-encoding': 'gzip, deflate, br',
            'accept': 'text/html,*/*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'x-requested-with': 'XMLHttpRequest',
            'origin': 'https://www.' + self.domain,
            'cache-control': 'no-cache',
            'pragma': 'no-cache',
            'content-type': 'application/x-www-form-urlencoded;charset=UTF-8',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
            'cookie': config.amazon['cookie']
        }

        page = 1
        while(True):
            params['pageNumber'] = page
            params['asin'] = product_id
            params['reftag'] = 'cm_cr_getr_d_paging_btm_' + str(page)
            response = requests.post(url=url + str(page), params=params, headers=headers)
            data = response.text
            comments = data.split('&&&')
            if len(comments) < 7:
                break
            for i in range(3):
                comments.pop(0)
            for i in range(4):
                comments.pop(-1)
            self.save(comments,product)
            page += 1



    def save(self, comments, product):
        records = []
        for comment in comments:
            temp = json.loads(comment)
            html = temp[2]
            soup = BeautifulSoup(html, 'lxml')
            title = soup.find('a', attrs={'data-hook': 'review-title'}).get_text()
            content = soup.find('span', attrs={'data-hook': 'review-body'}).get_text()
            rate = soup.find('i', attrs={'data-hook': 'review-star-rating'}).find('span').get_text()
            if self.country=='JP':
                rate = int(float(rate.split('ち')[1]))
            else :
                rate = int(float(rate.split(' ')[0]))
            create_time = soup.find('span', attrs={'data-hook': 'review-date'}).get_text()
            try:
                sku = soup.find('a', attrs={'data-hook': 'format-strip'}).get_text()
            except:
                sku = ''
            id = soup.find('div')['id']
            try:
                helpful = soup.find('span', attrs={'data-hook': 'helpful-vote-statement'}).get_text().split(' ')[0]
            except:
                helpful = 0
            try:
                helpful = int(helpful)
            except:
                helpful = 1
            record = (
                id,
                title,
                content,
                create_time,
                rate,
                sku,
                product,
                helpful,
                self.country
            )
            records.append(record)
        print records
        sql = 'INSERT IGNORE INTO comment_amazon(id, title,content,create_time,rate,sku,product,helpful,country) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)'
        self.cursor.executemany(sql, records)
        self.conn.commit()


if __name__ == '__main__':
    product_list = [
        # ('B07GDGZCCH', 'GoPro HERO7 黑色'),
        # ('B07HGCQR6X', 'GoPro Hero7 Hero 7 黑色动作相机 + GoPro 电池 + 北极星 8GB 和 16GB SDHC 内存 + 单脚架 + 弹性三脚架 + 悬浮手柄 + 硬壳 + 读卡器 + 附加卡'),
        # ('B07JHYHRJF', 'GoPro HERO7 黑色数字动作相机 4K 高清视频 12MP 照片，SanDisk 32GB Micro SD 卡，硬壳 - Gopro Hero 7 配件包'),
        # ('B07JF5Z6PS', 'GoPro HERO7 黑色 - 捆绑带 GoPro 头带 + QuickClip 、32GB Micro SDHC U3 卡、备用 Gopro 电池'),
        # ('B07J34TPG2', 'GoPro HERO7 黑色 - 捆绑 32GB SDHC 卡和自拍杆'),

        # ('B07GSVDFTQ', 'GoPro HERO7 Black'),
        # ('B07K2PTT9B', 'GoPro HERO7 Black with SanDisk 32G Memory Card Waterproof Digital Action Camera with Touch Screen 4K HD Video 12MP Photos Live Streaming Stabilisation'),
        # ('B07L8Y56QQ', 'GoPro HERO7 Black with 3-Way Arm'),
        # ('B07K84G13V', 'GoPro HERO7 Black - Waterproof Digital Action Camera with Sleeve Plus Lanyard - Black'),

        # ('B07H8YDBJ2', '【国内正品】GoPro(GoPro) HERO7 Go Pro HERO7 可视轴 Aqua 相机'),
        # ('B07HC7Q545', 'GoPro HERO7 黑色 CHDHX-701-FW'),

        ('B07HL3RNNK', 'GoPro HERO7 Black 运动摄像机防水防抖黑色 语音控制 有效像素1200万 附送包一个+32G 卡一张（新品）'),

    ]
    crawler = amazon_crawler('amazon.cn', 'CN')
    for product in product_list:
        crawler.get_comment(product[0], product[1])