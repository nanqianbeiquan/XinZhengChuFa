 # coding=utf-8
import requests
import MySQLdb
import logging
import time
import os
import re
from bs4 import BeautifulSoup

class ShangHaiRlzySheBaoCrawler(object):
    def __init__(self):
        self.mysql_conn()
        self.url = ''
        self.set_config()

    def set_config(self):
        self.url = 'http://www.12333sh.gov.cn/201412333/xxgk/gsgg'
        self.last_update_time = time.strftime('%Y-%m-%d %H:%M:%S')

    def mysql_conn(self):
        self.conn = MySQLdb.connect(host='172.16.0.76', port=3306, user='fengyuanhua', passwd='!@#qweASD', \
                                    db='guojia_zj', charset='utf8')
        self.cursor = self.conn.cursor()

    def run(self):
        for i in range(1, 30):
            url_first = self.url + '/index_'+str(i)+'.shtml'
            print '---------------------' + url_first
            r = requests.get(url_first)
            r.encoding = 'gbk'
            res = BeautifulSoup(r.text, 'html5lib')
            try:
                div = res.findAll('div', {'id':'subcontent'})[0]
                table = div.find('table')
                tbody = table.findAll('tbody')[3]
                print '########################################'
                tr_list = tbody.findAll('tr')
                tr_list_new = tr_list[1: len(tr_list)]
                for tr in tr_list_new:
                    td = tr.findAll('td')
                    matchchar = u'上海市社会保险事业管理中心告示'

                    if matchchar in td[0].text.strip():

                        a = td[0].find('a').encode('utf8')
                        href = a[10:41]
                        fbrq = td[1].text.strip()
                        url_second = self.url+href
                        print url_second
                        r1 = requests.get(url_second)

                        r1.encoding = 'gbk'
                        res1 = BeautifulSoup(r1.text, 'html5lib')
                        td1 = res1.findAll('td', {'id':'fontzoom'})[0]
                        p_list = td1.findAll('p')
                        title = p_list[0].text.strip()
                        p_list_new = p_list[1: -2]
                        for p in p_list_new:
                            names = p.text.strip()
                            # print i, name
                            name_list = re.split('\\s', names)
                            for name in name_list:
                                name = name.strip()
                                if name and not name.endswith(u'。'):
                                    print name
                                    sql = "INSERT into sh_rlzy VALUES('%s','%s','%s')" % (title, name, fbrq)
                                    try:
                                        self.cursor.execute(sql)
                                        self.conn.commit()
                                    except:
                                        # print sql
                                        # os._exit(1)
                                        print u'此条数据已存在!'
            except:
                pass


if __name__ == '__main__':
    Crawler = ShangHaiRlzySheBaoCrawler()
    Crawler.run()
