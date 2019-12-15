# -*- coding: utf-8 -*-
# @Time     : 2019/8/4 20:18
# @Author   : LEI
# @IDE      : PyCharm
# @PJ_NAME  : db_utils_test


from Utils.db_utils import LMysql

with LMysql(user='root', pwd='123',db='main')as mysql:
    # 建表 fake_colleges 假大学表
    sql = '''
           create table fake_colleges (
           id int auto_increment primary key,
           name VARCHAR(50) NOT NULL,
           province VARCHAR(50) COMMENT '所在地' NOT NULL,
           description VARCHAR(200) DEFAULT '',
           tags VARCHAR(50) DEFAULT '' COMMENT '标签，如<旧名|冒名>'
           ) ENGINE=innodb DEFAULT CHARSET=utf8;
           '''

    for n,s in enumerate([sql, ]):
        mysql.execute(s)
        print('ok-',n)
