# -*- coding: utf-8 -*-
# @Time     : 2019/7/7 0:42
# @Author   : LEI
# @IDE      : PyCharm
# @PJ_NAME  : db_utils

import pymysql


class LMysql:

    def __init__(self,  host='127.0.0.1',
                        charset='utf8',
                        user='',
                        pwd='',
                        db='',
                        port=3306,
                        autocommit=False):

        self.conn = pymysql.connect(host=host, user=user, password=pwd, database=db, charset=charset, port=port)
        self.autocommit = autocommit
        self.conn.autocommit(autocommit)
        self.cursor = self.conn.cursor()

    def __enter__(self):
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.autocommit is False:
            self.conn.commit()
        self.cursor.close()
        self.conn.close()


def fetchall_dict(cursor, name_replace={}):
    "Return all rows from a cursor as a dict"
    "name_replace 应用于名字替换的, 比如 name_replace = {'name':'jj', 'age':'年龄'}, 那么会把结果中name age的名称替换成指代名称"
    columns = [col[0] for col in cursor.description]

    ret = [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

    if len(name_replace) < 1:
        return ret

    ret_lst = []
    for item in ret:
        tmp = item
        for n in name_replace:
            orig_name = n
            replace_name = name_replace[n]

            if orig_name in tmp:
                tmp[replace_name] = tmp[orig_name]
                del tmp[orig_name]
        ret_lst.append(tmp)

    return ret_lst