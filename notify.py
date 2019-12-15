import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import requests, time

"""
钉钉通知
可以用来打日志、特殊通知使用
"""

my_hook = "https://oapi.dingtalk.com/robot/send?access_token=524ccba75d03ccf7" \
          "f2c346bc9f087a558629d7d5e24fd70023732fa97cdcec19"


class Ding:
    def __init__(self, prefix='', web_hook=my_hook):
        self.prefix = prefix
        self._hook = web_hook

    def notify(self, *args):
        if len(args) == 0:
            return

        msg_item = {
            'msgtype': 'text',
            'text': {'content': f'时间: {time.strftime("%Y-%m-%d %H:%M:%S")} \n'
                                f'类型: {"暂无"} \n'
                                f'主体: {self.prefix} \n'
                                f'信息: {"".join([str(i) for i in args])}'}
        }

        headers = {'content-type': 'application/json; charset=utf-8'}
        r = requests.post(self._hook, headers=headers, json=msg_item, verify=False)
        # print(self.hook, r.text)


if __name__ == '__main__':
    print(not (None or None))
    d = Ding('HH')
    i = 0
    while i < 10000:
        d.notify(f'你好{i}')
        i += 1
        time.sleep(1)
