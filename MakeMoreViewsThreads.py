# pip install selenium webdriver_manager

import sys  # 3.12.7 | packaged by Anaconda, Inc. | (main, Oct  4 2024, 13:17:27) [MSC v.1929 64 bit (AMD64)]
import threading
import time
import random
# selenium 4
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager


# Hyper-Parameters
thread_num = 6


def parameters():
    # 如何隐藏 selenium 请求 https://developer.baidu.com/article/detail.html?id=3348317
    options = webdriver.ChromeOptions()
    # chrome 无痕模式
    options.add_argument('--incognito')
    # 修改 User-Agent 字符串
    # Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/118.0
    # Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36')
    # 使用无头浏览器模式, 完全隐藏图形界面和某些用户交互特征 (似乎非常有效？)
    options.add_argument('--headless')

    # 每个线程需要访问的次数
    target_views = 100
    # 目标网站
    target_paths = [
        "https://www.bilibili.com/video/BV1JaqLBTEn9/?vd_source=c2ec0da465c37503711a8d961f034580", \
        "https://www.bilibili.com/video/BV17841147Lg/?spm_id_from=333.1387.upload.video_card.click&vd_source=c2ec0da465c37503711a8d961f034580", \
        # "https://cn.bing.com/", \
    ]
    # 基础等待时间
    basic_time = 5
    # 浮动等待间隔
    floating_time = [
        5,
        5
    ]

    assert len(target_paths) <= len(floating_time) # 对应关系
    return (options, target_views, target_paths, basic_time, floating_time)


class myThread(threading.Thread):
    def __init__(self, id, configs):
        threading.Thread.__init__(self)
        self.id = id
        self.configs = configs

    def run(self):
        chrome(self.id, *self.configs)


def chrome(thread_id, chrome_options, views, paths, basic_time, floating_time):
    # 如果出现"找不到 host"的异常，有可能是 Chrome 正在更新导致的
    for i in range(views):
        for j in range(len(paths)):
            try:
                browserl = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
                # 调整浏览器窗口大小和位置 - 潜在识别点
                length = random.randint(1280, 1920)
                width = random.randint(720, 1080)
                x = random.randint(-400, 400)
                y = random.randint(-200, 200)
                browserl.set_window_size(length, width)
                browserl.set_window_position(x, y)

                browserl.get(paths[j])
                ctime = random.randint(basic_time, basic_time + floating_time[j])

                print('\n[THREAD-{}] [ROUND-{}] Waiting time: {} s\nWindow pixels: {}*{} || Windows position: {},{}\nCurrent Web path: {}'.\
                      format(thread_id, i, ctime, length, width, x, y, paths[j]))
                
                time.sleep(ctime)
                browserl.quit()
            except Exception as e:
                print(e)


if __name__ == "__main__":
    # 首次启动前若 selenium 版本不大于 4.6，则需要自己安装对应浏览器的 driver
    # 官方 ERROR 文档：https://www.selenium.dev/documentation/webdriver/troubleshooting/errors/driver_location/
    # 自动化解决方案 Webdriver Manager：https://github.com/SergeyPirogov/webdriver_manager
    # Salty Fish 大佬的帖子 https://im.salty.fish/index.php/archives/revengr-bilibili-352.html 研究 B 站风控底层机制
    # chrome(0, *parameters())

    threads = []
    # create
    for i in range(thread_num):
        threads.append(myThread(i, parameters()))
    # start
    for i in range(thread_num):
        threads[i].start()
    print("\n\n----- START -----\n\n")