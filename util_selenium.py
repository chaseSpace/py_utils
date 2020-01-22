import platform
import re
import time

import selenium.webdriver.support.expected_conditions as EC
import selenium.webdriver.support.ui as ui
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

'''
Selenium 3.141
Chrome version 75.0.3770
chrome driver 75.0.3770.90
'''


class Config:
    chrome_driver_path = r'C:\chromedriver\chromedriver-75-0-3770-140.exe'
    linux_chrome_driver_path = r'/root/chromedriver'


__get_ip_url = ['http://whatismyip.akamai.com',
                'http://iiip.co']


def is_visible_by_xpath(driver, locator, timeout=10):
    # 等待元素出现
    try:
        ui.WebDriverWait(driver, timeout).until(EC.visibility_of_element_located((By.XPATH, locator)))
        return True
    except TimeoutException:
        return False


def is_visible_by_xpath_not_block(driver, locators: [], timeout=10):
    '''
    :param driver:
    :param locators: 接收多个xpath表达式，只要其中一个出现就返回对应的index，超时后一个都没有出现返回false
    :param timeout:
    :return:
    '''
    # 浏览器是非阻塞模式
    for _ in range(timeout):
        for n, loc in enumerate(locators):
            if is_visible_by_xpath(driver, locators[n].replace('<loc>', ''), timeout=1):  # 处理css表达式中预留的占位符 <loc>
                return n
        time.sleep(1)
    return False


def is_visible_by_css(driver, locator, timeout=10):
    # 等待元素出现
    try:
        ui.WebDriverWait(driver, timeout).until(EC.visibility_of_element_located((By.CSS_SELECTOR, locator)))
        return True
    except TimeoutException:
        return False


def is_visible_by_css_not_block(driver, locators: [], timeout=10):
    '''
    :param driver:
    :param locators: 接收多个css表达式，只要其中一个出现就返回对应的index，超时后一个都没有出现返回false
    :param timeout:
    :return:
    '''
    # 浏览器是非阻塞模式
    for _ in range(timeout):
        for n, loc in enumerate(locators):
            if is_visible_by_css(driver, locators[n].replace('<loc>', ''), timeout=1):  # 处理css表达式中预留的占位符 <loc>
                return n
        time.sleep(1)
    return False


def get_elem_by_css(driver, css, multi=False):
    # 获取元素都用这个方法，不用自己处理异常，最稳妥
    elem, msg = None, ''
    try:
        if multi:  # 这个是返回list
            elem = driver.find_elements_by_css_selector(css)
        else:
            elem = driver.find_element_by_css_selector(css)
        return elem, msg
    except Exception as e:
        msg = "[%s]--%s" % (e.__class__, e.args)

    return elem, msg


def get_ip(driver):
    # 获取自身外网IP-判断代理是否正常

    ip = ''
    for u in __get_ip_url:
        try:
            driver.get(u)
        except:
            continue
        driver.implicitly_wait(10)
        _ip = re.search('\d+\.\d+\.\d+\.\d+', driver.page_source)
        if _ip:
            ip = _ip.group()
            break
    return ip


def get_brower(proxy={},
               proxy_url='',
               headless=True,
               load_image=True,
               ua: str = '',
               log=print,
               page_load_timeout=30,
               set_desired_capabilities=False,
               chrome_driver_path=None):
    # 尝试3次初始化br（低概率的崩溃可能）
    for i in range(3):
        try:
            br = __get_brower(proxy=proxy,
                              proxy_url=proxy_url,
                              headless=headless,
                              load_image=load_image,
                              ua=ua,
                              log=log,
                              page_load_timeout=page_load_timeout,
                              set_desired_capabilities=set_desired_capabilities,
                              chrome_driver_path=chrome_driver_path)
            return br
        except Exception as e:
            log('[get br err]--%s --%s' % (e.__class__, e.args))
        time.sleep(1)
    # 起不来就退出程序
    exit(1)


def __get_brower(proxy={},
                 proxy_url='',
                 headless=True,
                 load_image=True,
                 ua: str = '',
                 log=print,
                 page_load_timeout=30,
                 set_desired_capabilities=False,
                 chrome_driver_path=None):
    """
    :param proxy: {"proto": "http(s)"|"socks5", "host": "127.0.0.1", "port": 8080}
    :param headless:
    :param load_image  是否加载图片，若需识别验证码, 则必须为true
    :param ua: user-agent
    :param log: log handler
    :param page_load_timeout:
    :param set_desired_capabilities 此项控制 selenium的api是否是阻塞执行,设置此项为true，page_load_timeout就没有意义了
    :param chrome_driver_path: str
    :return:
    """
    chrome_options = Options()

    ops = []

    ops.append('--headless') if headless else ...
    ops.extend([
        '--disable-gpu',
        'disable-infobars',  # 隐藏"Chrome正在受到自动软件的控制"
        'log-level=3',
        '--disable-dev-shm-usage'
    ])

    system = platform.system()
    if system == 'Linux':
        if chrome_driver_path is None:
            chrome_driver_path = Config.linux_chrome_driver_path
        if '--headless' not in ops:
            ops.append('--headless')
        ops.append('--no-sandbox')
    else:
        if chrome_driver_path is None:
            chrome_driver_path = Config.chrome_driver_path

    ops.append('user-agent=%s' % ua) if ua else ...

    for op in ops:
        chrome_options.add_argument(op)

    if not load_image:
        chrome_options.add_experimental_option('prefs', {'profile.default_content_setting_values': {'images': 2}})

    if proxy != {}:
        log('[chrome-proxy]--%s' % proxy)
        chrome_options.add_argument('proxy-server=%s://%s:%s' % (proxy['proto'], proxy['host'], proxy['port']))  # 代理
    elif proxy_url:
        log('[chrome-proxy]--%s' % proxy_url)
        chrome_options.add_argument('proxy-server=%s' % proxy_url)
    else:
        log("start browser without proxy!!!")

    dc = {}

    desired_capabilities = DesiredCapabilities.CHROME  # 修改页面加载策略
    desired_capabilities["pageLoadStrategy"] = "none"

    if set_desired_capabilities:
        dc.update(desired_capabilities)

    if system == 'Windows':
        driver = webdriver.Chrome(options=chrome_options,
                                  executable_path=chrome_driver_path,
                                  desired_capabilities=dc)
    else:
        driver = webdriver.Chrome(chrome_options=chrome_options,
                                  desired_capabilities=dc)

    driver.set_page_load_timeout(page_load_timeout)
    driver.set_script_timeout(page_load_timeout)

    # log('real_ip------%s'% get_ip(driver))

    return driver


def get_page_source(br) -> str:
    try:
        html = br.page_source
    except:
        return ''
    return html


if __name__ == '__main__':
    br = get_brower(headless=False,
                    load_image=False,
                    log=print,
                    set_desired_capabilities=True,
                    # chrome_driver_path=r'C:\Program Files\Mozilla Firefox\geckodriver.exe',
                    chrome_driver_path=r'C:\Users\LEI\Desktop\chromedriver\chromedriver-75-0-3770-140.exe'
                    )

    br.get('https://www.288365.com/?lng=10&rurl=casino.288365.com#/IP/')
    time.sleep(5)
    br.close()
