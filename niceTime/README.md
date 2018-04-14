## 这是一个关于时间的模块，我根据自己的习惯重新封装了`time`库，若你有兴趣可以一试~

### 包含以下time自带的方法  
=====
* strptime  
* strftime  
* localtime  
* ctime  
* sleep  
* clock  

### 下面是我新增的方法
========
* timestamp(n=10) ：轻松获取各类时间戳  

 秒级时间戳：  
```
	print niceTime.timestamp()  #1523717093
```
 原始时间戳：  
```
	print niceTime.timestamp(0) #1523717093.6
```
 毫秒级时间戳： 
```
	print niceTime.timestamp(13) #1523717093599
```

* now_time_elements(timestamp=None) ：可传入时间戳获取对应的时间，以列表格式返回
```
	timestamp = niceTime.timestamp()  
	print niceTime.now_time_elements(timestamp) #[2018, 4, 14, 18, 19, 1, 5, 104, 0]
```

* now_time(timestamp=None) ： 可传入时间戳获取对应的时间，直接返回一个友好的可读时间

```
	print niceTime.now_time() # 2018-04-14 22:51:58
```

* get_interval_time(t_start,t_end,'y m d H M S') : 轻松获取两个时间点之间的时间差,_format参数可指定返回的哪些时间元素

```
	t_start = niceTime.now_time_elements()
	niceTime.sleep(1)
	t_end = niceTime.now_time_elements()
	print niceTime.get_interval_time(t_start,t_end,_format='H M S') #[0, 0, 1]
```

* convert_to_stamp(strptime) ：传入标准格式的时间参数，返回对应的时间戳

```
	strptime = '2018-01-09 10:20:11'
	print niceTime.convert_to_stamp(strptime) # 1515464411.0
```

#### 下载后存放到python环境的`Lib/site-packages`目录即可使用

喜欢给个star把~
