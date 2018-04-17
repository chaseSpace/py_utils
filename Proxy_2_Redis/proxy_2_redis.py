# -*- coding: utf-8 -*-
# @Time     : 2018/4/16 21:41
# @Author   : LEI
# @IDE      : PyCharm
# @PJ_NAME  : proxy_2_redis
import redis
import requests
try:
    import niceTime
except Exception:
    import time as niceTime

######################
"""必要配置"""
#获取代理IP的url
proxy_url = 'http://dev.kuaidaili.com/api/getproxy/?orderid=952388528527534&num=20&b_pcchrome=1&b_pcie=1&b_pcff=1&protocol=1&method=1&an_an=1&an_ha=1&sp1=1&sp2=1&quality=1&format=json&sep=1'
#redis中代理IP池存储的key名
list_key = 'proxy_list'
#当IP池内IP数小于多少时添加新的IP
lower = 10
#redis中使用过的IP数量存储的key名
used_ip_number_key = 'used_ip_number'
########################

def init_redis():
    """初始化redis的连接"""
    pool = redis.ConnectionPool(host='127.0.0.1', port=6379)
    r = redis.Redis(connection_pool=pool)
    return r

def download_proxy_ip(ip_url):
    """从平台获取一定数量的代理ip"""
    data = requests.get(ip_url).json()
    if data.get('data').get('count')>0:
        #解析data后必须返回包含代理IP的列表：['11.11.11.11:80',]
        _list = data.get('data').get('proxy_list')
        return set(_list)

def lpush(r,ip_list):
    """将代理ip加入redis中的ip_list"""
    n=0
    for i in range(len(ip_list)):
        a = r.lpush(list_key,ip_list.pop())
        if a:
            n+=1
    if n>1:
        print '成功push了%s个ip'% n
    else:
        print 'push操作失败'
    return n

def store_used_ip_number(r,key,number):
    """将使用过的ip数量存入redis"""
    r.set(key,number)


if __name__ == '__main__':
    """启动redis后，可直接运行本程序"""
    r = init_redis()
    used_ip_number = r.get(used_ip_number_key)
    while 1:
        number = r.llen(list_key)
        if number < lower:
            print 'redis中IP数量少于10个，正在添加新的IP'
            list_ = download_proxy_ip(proxy_url)
            added = lpush(r,list_)
            used_ip_number= (int(used_ip_number) if used_ip_number else 0) + added
            print "到目前为止一共提取了%s个IP" % used_ip_number
            store_used_ip_number(r,used_ip_number_key,used_ip_number)
        else:
            print 'IP充足，剩余%s个'%number
            niceTime.sleep(1)