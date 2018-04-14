#coding=utf8

import time

def strptime(string, format):
    """根据给定的时间字符串和格式返回时间元组"""
    return time.strptime(string,format)

def strftime(format, p_tuple=None):
    """根据给定的格式和"""
    return time.strftime(format,p_tuple)

def localtime(timestamp=None):
    """根据给定的时间戳参数返回时间元组"""
    return time.localtime(timestamp)

def ctime(timestamp=None):
    """根据给定的时间戳返回可读形式的时间"""
    return time.ctime(timestamp)

def sleep(secs):
    """推迟线程运行的时间，参数为秒数"""
    return time.sleep(secs)

def clock():
    """返回引用线程在cpu中运行的时间"""
    return time.clock()

def timestamp(n=10):
    """
    n=0  :原始时间戳 （小数点后两位）
    n=10 :秒级时间戳 （10位数整数，一般用这个）
    n=13 ：毫秒级时间戳 （13位数整数）
    """
    if n==10:return int(time.time())
    elif n==0: return time.time()
    elif n==13: return int(time.time()*1000)

def now_time_elements(timestamp=None):
    """
    根据时间戳打印对应的时间元组，返回数组，类似：
    [2018, 4, 14, 18, 19, 1, 5, 104, 0]
   【年     月  日  时  分  秒  周六  一年的第几天 该值决定是否为夏令时的旗帜】
   若时间戳参数未传入，则打印当前时间的时间元组
    """
    return [i for i in time.localtime(timestamp)]

def now_time(timestamp=None):
    """
    timestamp : 时间戳
    return ：返回时间戳对应的固定格式的时间 ：如 2018-04-14 21:17:50
    若未传入时间戳参数，则返回当前时间
    """
    now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))
    return now_time

def get_interval_time(t_start,t_end,_format= 'y m d H M S'):
    """
    传入开始和结束时间和输出格式，返回指定格式的时间差
    如：t_start = now_time_elements() ,t_end = now_time_elements(),_format = 'y m d H M S'
    :return [0,0,0,1,20,10] 表示两次时间的差为0年0月0日 1时20分10秒
    """
    #_format = 'y m d H M S'
    index_dict = {'y':0,'m':1,'d':2,'H':3,'M':4,'S':5}
    _inter_time = []
    for i in range(6):
        _inter_time.append(t_end[i]-t_start[i])
    inter_time = []
    for i in _format.split(' '):
        inter_time.append(_inter_time[index_dict[i]])
    del _inter_time
    return inter_time

def convert_to_stamp(strptime):
    """
    接收一个标准格式的时间，返回对应的时间戳,浮点数格式
    如：strptime = '2018-01-09 10:20'
    传入的时间参数必须为以下格式的其中一种：
    '2018-01-09 10:20',无秒数
    '2018-01-09 10:20:11',有秒数
    """
    from re import search
    secs = search('..:..:..',strptime)
    if secs:
        timeArray = time.strptime(strptime, "%Y-%m-%d %H:%M:%S")
    else:
        timeArray = time.strptime(strptime, "%Y-%m-%d %H:%M")
    return time.mktime(timeArray)