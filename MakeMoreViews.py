# pip install selenium webdriver_manager

import time
import random
# selenium 4
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager


def parameters():
    # 如何隐藏 selenium 请求 https://developer.baidu.com/article/detail.html?id=3348317
    options = webdriver.ChromeOptions()
    # chrome 无痕模式
    options.add_argument('--incognito')

    target_views = 100
    target_paths = [
        "https://www.bilibili.com/video/BV1JaqLBTEn9/?vd_source=c2ec0da465c37503711a8d961f034580", \
        "https://www.bilibili.com/video/BV17841147Lg/?spm_id_from=333.1387.upload.video_card.click&vd_source=c2ec0da465c37503711a8d961f034580"
    ]
    basic_time = 10
    floating_time = [
        20,
        10
    ]
    return (options, target_views, target_paths, basic_time, floating_time)


def chrome(chrome_options, views, paths, basic_time, floating_time):
    for i in range(views):
        print('\n')
        for j in range(len(paths)):
            try:
                # 如果出现找不到 host 的异常，有可能是 Chrome 正在更新导致的
                browserl = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
                browserl.get(paths[j])
                ctime = random.randint(basic_time, basic_time + floating_time[j])
                print('[{}] Waiting time: {}\nCurrent Web path: {}\n'.format(i, ctime, paths[j]))
                time.sleep(ctime)
                browserl.quit()
            except Exception as e:
                print(e)


if __name__ == "__main__":
    # 首次启动前若 selenium 版本不大于 4.6，则需要自己安装对应浏览器的 driver
    # 官方 ERROR 文档：https://www.selenium.dev/documentation/webdriver/troubleshooting/errors/driver_location/
    # 自动化解决方案 Webdriver Manager：https://github.com/SergeyPirogov/webdriver_manager
    chrome(*parameters())