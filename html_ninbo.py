#coding=utf-8

import MySQLdb
import os
from bs4 import BeautifulSoup
import time

class html_ninbo(object):
    def __init__(self):
        self.update_time = time.strftime("%Y-%m-%d")
        self.field = [{'nsrsbh': u'纳税人识别号,税务登记号,NSRSBH'}, {'nsrmc': u'企业名称,纳税人名称,企业或单位名称,NSRMC'},
                      {'fddbr': u'法定代表人(负责人)姓名,法人代表或负责人姓名,法人（业主）姓名,法人（负责人、业主）'},
                      {'zjzl': u'种类'}, {'zjhm': u'号码'},
                      {'jydz': u'生产经营地址,经营地点'},
                      {'rdrq': u'非正常户认定日期'}]


    def mysql_conn(self):
        '''
        通信MySQL
        '''
        self.conn = MySQLdb.connect(host='172.16.0.76', port=3306, user='fengyuanhua', passwd='!@#qweASD', \
                                    db='taxplayer', charset='utf8')
        self.cursor = self.conn.cursor()


    def insert_into_database(self,sql):
        self.cursor.execute(sql)
        self.conn.commit()


    def get_field_info(self, tr_title, fields):
        match_fields = []
        td = tr_title.findAll('td')
        for i in range(len(td)):
            val = td[i].text.strip()
            for fds in range(len(fields)):
                match_field = fields[fds].values()[0]
                match_key = fields[fds].keys()[0]
                # print val
                # print match_field, match_key
                if match_field == u'号码':
                    if u'证件号码' in val or u'身份证号码' in val:
                        match_fields.append({match_key: i})
                elif match_field == u'种类':
                    if u'证件种类' in val or u'证件类型' in val:
                        match_fields.append({match_key: i})
                elif val in match_field and val:
                    match_fields.append({match_key: i})
        return match_fields


    def get_filename_list_1(self):
        """
        返回宁波市,filename为htm的列表
        1为非正常户
        """
        self.mysql_conn()
        sql_1 = "SELECT * FROM taxplayer_filename where region='宁波市' AND title like '%非正常户%' \
        AND filename LIKE '%htm%'"
        list_nums_1 = self.cursor.execute(sql_1)
        if list_nums_1 == 0:
            print u'没有找到'
            os._exit(1)
        else:
            filename_list_1 = self.cursor.fetchmany(list_nums_1)
            return filename_list_1


    def get_filename_list_2(self):
        """
        返回宁波市,filename为htm的列表
        2为欠税信息
        """
        self.mysql_conn()
        sql_2 = "SELECT * FROM taxplayer_filename where region='宁波市' AND title not like '%非正常户%' \
        AND filename LIKE '%htm%'"
        list_nums_2 = self.cursor.execute(sql_2)
        if list_nums_2 == 0:
            print u'没有找到'
            os._exit(1)
        else:
            filename_list_2 = self.cursor.fetchmany(list_nums_2)
            return filename_list_2


    def get_filename_path_list_1(self):
        '''
        返回返回宁波市,filename为htm的path 列表
        1为非正常户
        '''
        filename_path_list_1 = []
        fbrq_list_1 = []
        filename_list_1 = html_ninbo().get_filename_list_1()
        for i in filename_list_1:
            # print i[4]
            filename_path = r'D:\All_files\ZheJiang\savehtml' + '\\' + i[4]
            filename_path_list_1.append(filename_path)
            fbrq = i[2]
            fbrq_list_1.append(fbrq)
            # print filename_path
        return filename_path_list_1, fbrq_list_1


    def get_filename_path_list_2(self):
        '''
        返回返回宁波市,filename为htm的path 列表
        2为欠税信息
        '''
        filename_path_list_2 = []
        fbrq_list_2 = []
        filename_list_2 = html_ninbo().get_filename_list_2()
        for i in filename_list_2:
            # print i[4]
            filename_path = r'D:\All_files\ZheJiang\savehtml' + '\\' + i[4]
            filename_path_list_2.append(filename_path)
            fbrq = i[2]
            fbrq_list_2.append(fbrq)
            # print filename_path
        return filename_path_list_2, fbrq_list_2


    def get_detail_1(self):
        '''
        获取字段详情
        并且输入MySQL
        '''
        self.mysql_conn()
        province = u'浙江省'
        region = u'宁波市'
        last_update_time = self.update_time
        filename_path_list_1 = html_ninbo().get_filename_path_list_1()[0]
        fbrq_list_1 = html_ninbo().get_filename_path_list_1()[1]
        for i in range(len(filename_path_list_1)):
            path = filename_path_list_1[i]
            fbrq = fbrq_list_1[i]
            print path
            print '##############################################################'
            htmlfile = open(path, 'r')  # 以只读的方式打开本地html文件
            htmlpage = htmlfile.read()
            soup = BeautifulSoup(htmlpage, "html.parser")
            # print soup
            try:
                tbody = soup.find_all('tbody')
                # print tbody
                all_tr = tbody[0].find_all('tr')
                # print all_tr
                tr_title = all_tr[0]
                fields = self.field
                match_fields = html_ninbo().get_field_info(tr_title,fields)
                print match_fields
                for ii in range(1,len(all_tr)):
                    all_td = all_tr[ii].find_all('td')
                    field_keys = 'province,region,last_update_time'
                    val = "'" + province.encode('utf8') + "','" + region.encode('utf8') + "','" + self.update_time + "'"
                    for everyment in match_fields:
                        key = everyment.keys()[0]
                        # print 'key', key
                        field_keys += ',' + key
                        i_value = everyment.values()[0]
                        values = all_td[i_value].text.strip()
                        val += ",'" + values.encode('utf8') + "'"
                        # print 'values', values
                    if 'rdrq' not in field_keys:
                        field_keys += ',rdrq'
                        val += ",'" + fbrq.encode('utf8') + "'"
                    if 'fbrq' not in field_keys:
                        field_keys += ',fbrq'
                        val += ",'" + fbrq.encode('utf8') + "'"
                    sql = 'insert into taxplayer_abnormal_html (' + field_keys + ') values (' + val + ')'
                    # print sql
                    try:
                        self.insert_into_database(sql)
                        print 'sql=', sql
                        # print u'******此条写入成功!******'
                    except Exception, e:
                        print e
                        print u'写入数据库异常'
            except Exception, e:
                print e


    def get_detail_2(self):
        '''
        获取字段详情
        并且输入MySQL
        '''
        self.mysql_conn()
        province = u'浙江省'
        region = u'宁波市'
        last_update_time = self.update_time
        filename_path_list_2 = html_ninbo().get_filename_path_list_2()[0]
        print filename_path_list_2
        fbrq_list_2 = html_ninbo().get_filename_path_list_2()[1]
        for i in range(len(filename_path_list_2)):
            path = filename_path_list_2[i]
            fbrq = fbrq_list_2[i]
            print 'path:', path
            print '##############################################################'
            htmlfile = open(path, 'r')  # 以只读的方式打开本地html文件
            htmlpage = htmlfile.read()
            soup = BeautifulSoup(htmlpage, "html.parser")


if __name__ == '__main__':
    # html_ninbo().get_detail_1()
    html_ninbo().get_detail_2()
    print u'1 结束'
    print '######################################################################################################'
