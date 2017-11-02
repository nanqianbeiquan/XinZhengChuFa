#coding=utf-8

import requests
from bs4 import BeautifulSoup
import MySQLdb
import sys

class gjhb(object):
    def __init__(self):
        self.failed_times = 0

    def create_cursor(self):
        self.conn = MySQLdb.connect(host='172.16.0.76',port=3306,user='guanhuaixuan',passwd='123QWEasd',db='guojia_zj',charset='utf8')
        self.cursor=self.conn.cursor()

    def insert_into_database(self,sql):
        self.cursor.execute(sql)
        self.conn.commit()

    def get_detail(self, num):
        self.create_cursor()
        if int(num) == 1 :
            url = 'http://www.mep.gov.cn/home/pgt/xzcf/index.shtml'
        else:
            url = 'http://www.mep.gov.cn/home/pgt/xzcf/index_' + str(num - 1) + '.shtml'

        headers = {'Host': 'www.mep.gov.cn',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                    'Accept-Encoding': 'gzip, deflate',
                    'Referer': 'http://www.mep.gov.cn/home/pgt/xzcf/index.shtml',
                    'Cookie': '_gscu_95520784=78575414hp42sz20; _gscs_95520784=78575414wdhg2620|pv:6; _gscbrs_95520784=1; wdcid=49a867939cbca3b7; wdlast=1478576099',
                    'Connection': 'keep-alive'}
        r = requests.session().get(url=url, headers=headers)
        soup = BeautifulSoup(r.content, 'html5lib')
        # print soup
        m = soup.find_all(class_='main_rt_list')
        for element in m[0].find_all('li'):
            n = element.a.get('href')
            title = element.a.get('title')
            # print title
            time = element.span.text
            # print time
            url_start = 'http://www.mep.gov.cn/gkml'
            try:
                url_end = n.split('gkml')[1]
                detail_addr = url_start + url_end
                # print n
                # print "####", detail_addr
                # print '*********************************'
                rr = requests.session().get(url=detail_addr, headers=headers)
                qqq = BeautifulSoup(rr.content, 'html5lib')
                detail_content = qqq.text.replace("'","\"")
                detail_content_2 = qqq.find_all('p')
                content = ''
                for ii in detail_content_2:
                    w = ii.text
                    content = content + w + '\n'
                # print content
                sql_1 = "select title from guojia_huanbao where title='%s'" % title
                yyy = self.cursor.execute(sql_1)

                if yyy == 0:
                    sql = "insert into guojia_huanbao values('%s','%s','%s','%s')" % (title,time, detail_addr, content)
                    try:
                        self.insert_into_database(sql)
                        print 'title=', title
                        print 'time=', time
                        print 'detail_addr=', detail_addr
                        print u'*********此条写入成功!*********'

                    except Exception, e:
                        print e
                        print u'写入数据库异常'
                else:
                    self.failed_times += 1
                    print u'累计失败%s' % self.failed_times
                    if self.failed_times == 10:
                        print u'累计失败10次,退出程序'
                        sys.exit()
            except Exception, e:
                print e

        print u'第%s页更新完成' % num


    def download(self):
        for num in range(1,9999999):
            gjhb().get_detail(num)

if __name__ == '__main__':
    gjhb().download()
