# -*- coding: UTF-8 -*-

import requests
import json
import time
import sys

from database import db_util, config

reload(sys)
sys.setdefaultencoding("utf-8")

class jd_crawler:
    def __init__(self):
        self.conn = db_util.get_mysql_db(config.collection_database)
        self.cursor = self.conn.cursor()

    def __del__(self):
        self.conn.close()


    def get_comment(self,product_id):
        url = 'https://sclub.jd.com/comment/productPageComments.action'
        params = {
            'callback': '',
            'productId': product_id,
            'score': 0,
            'sortType': 5,
            # 'page': 0,
            'pageSize': 10,
            'isShadowSku': 0,
            'rid': 0,
            'fold': 1
        }
        headers = {
            'accept-encoding': 'gzip, deflate, br',
            'accept': '*/*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'no-cache',
            'pragma': 'no-cache',
            'referer': 'https://item.jd.com/' + str(product_id) + '.html',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
            'cookie': config.jd['cookie']
        }

        page = 0
        while(True):
            params['page'] = page
            response = requests.get(url=url, params=params, headers=headers)
            data = response.text
            # print data
            try:
                json_object = json.loads(data, "utf-8")
            except:
                print data
                time.sleep(60)
                continue
            comments = json_object['comments']
            print json.dumps(comments)
            if len(comments) == 0:
                break
            self.save(comments)
            page += 1
            time.sleep(3)



    def save(self, comments):
        records = []
        for comment in comments:
            record = (
                str(comment['id']),
                comment['content'],
                comment['referenceName'],
                comment['score'],
                comment['usefulVoteCount'],
                comment['uselessVoteCount'],
                comment['creationTime']
            )
            try:
                record += (comment['afterUserComment']['hAfterUserComment']['content'],)
            except:
                record += (None,)
            records.append(record)
        sql = 'INSERT IGNORE INTO jd_comment(id,content,product,score,useful_count,useless_count,create_time,after_user_comment) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)'

        try:
            # 执行SQL语句
            self.cursor.executemany(sql, records)
            # 提交修改
            self.conn.commit()
        except Exception, e:
            print e.message

if __name__ == '__main__':
    product_list = [
        # 100001138215,
        # 100001329898,
        # 33253067074,
        40519300990,
        34626543140,
        33363834831,
        100002393624,
        33429246705
        # 33573560575
    ]
    crawler = jd_crawler()
    for product in product_list:
        crawler.get_comment(product)