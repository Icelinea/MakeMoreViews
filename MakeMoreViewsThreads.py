# pip install selenium webdriver_manager

import sys  # 3.12.7 | packaged by Anaconda, Inc. | (main, Oct  4 2024, 13:17:27) [MSC v.1929 64 bit (AMD64)]
import threading
import time
import random
# selenium 4
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium_stealth import stealth
import redis


# Hyper-Parameters
exit_event = threading.Event()
thread_num = 1
debug_mode = True


def proxy_pool():
    try:
        r = redis.StrictRedis(
            host='127.0.0.1', 
            port=6379, 
            db=0, 
            password=None, # 如果设置了密码请填写字符串
            decode_responses=True
        )

        # 获取所有代理 (ProxyPool 默认使用有序集合 'proxies')
        # zrevrangebyscore 获取分数最高的 IP（确保 IP 质量最好）
        # 我们取分数在 100 到 10 之间的所有 IP
        proxies = r.zrevrangebyscore('proxies', 100, 10)

        if not proxies:
            raise AttributeError(f"Proxies Not Found")
        else:
            return proxies
    except Exception as e:
        print(f"\n-----\nRedis Database Exception: {e}\n-----\n")
        return None


def parameters(mode="PC"):
    """
    mode: PC, Android, iOS
    """
    assert mode in ["PC", "Android", "iOS"], "Invaild Access Mode"

    # 如何隐藏 selenium 请求 https://developer.baidu.com/article/detail.html?id=3348317
    options = webdriver.ChromeOptions()

    # 动态 IP 池
    options.add_argument(f'--proxy-server={proxy_pool()}')

    # chrome 无痕模式
    options.add_argument('--incognito')

    # 基础反检测配置
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    # 修改 User-Agent 字符串
    # Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/118.0
    # Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36
    if mode == "PC":
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36')
    elif mode == "Android":
        options.add_argument('user-agent=Mozilla/5.0 (Linux; Android 13; SM-S901B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36 BiliApp/7.20.0')
    elif mode == "iOS":
        options.add_argument('user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 BiliApp/7.20.0')
    else:
        assert False

    # 使用无头浏览器模式, 完全隐藏图形界面和某些用户交互特征 (似乎非常有效？)
    options.add_argument('--headless')

    # 禁用 Chrome 效能/休眠模式
    options.add_argument('--disable-background-networking')
    options.add_argument('--disable-background-timer-throttling')
    options.add_argument('--disable-backgrounding-occluded-windows')
    options.add_argument('--disable-breakpad')
    options.add_argument('--disable-client-side-phishing-detection')
    options.add_argument('--disable-component-update')
    options.add_argument('--disable-default-apps')
    options.add_argument('--disable-dev-shm-usage') # 防止内存溢出
    options.add_argument('--no-sandbox')

    # 每个线程需要访问的次数
    target_views = 1000
    # 目标网站
    target_paths = [
        "https://www.bilibili.com/video/BV1U3Q4BnEWT/?spm_id_from=333.1007.top_bar.click", \
        "https://www.bilibili.com/video/BV1U3Q4BnEWT/?spm_id_from=333.337.search-card.all.click", \
    ]
    # 基础等待时间
    basic_time = 5
    # 浮动等待间隔
    floating_time = [
        5,
        5,
        # 5
    ]

    assert len(target_paths) == len(floating_time) # 对应关系
    return (options, mode, target_views, target_paths, basic_time, floating_time)


class myThread(threading.Thread):
    def __init__(self, id, configs):
        threading.Thread.__init__(self)
        self.id = id
        self.configs = configs

    def run(self):
        chrome(self.id, *self.configs)


def chrome(thread_id, chrome_options, current_mode, views, paths, basic_time, floating_time):
    # 如果出现"找不到 host"的异常，有可能是 Chrome 正在更新导致的
    browserl = None

    try:
        for i in range(views):
            for j in range(len(paths)):
                # 检查退出标志
                if exit_event.is_set():
                    print("Thread-{} exit due to system call.".format(thread_id))
                    return

                try:
                    browserl = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)

                    # 使用 stealth 抹除硬件指纹 (绕过 Canvas/WebGL/WebDriver 等高级设备 ID 检测)
                    stealth(browserl,
                        languages=["zh-CN", "zh"],
                        vendor="Google Inc.",
                        platform="Win32",
                        webgl_vendor="Intel Inc.",
                        renderer="Intel Iris OpenGL Engine",
                        fix_hairline=True,
                    )

                    # 调整浏览器窗口大小和位置 - 潜在识别点
                    if current_mode == "PC":
                        length = random.randint(1280, 1920)
                        width = random.randint(720, 1080)
                        x = random.randint(-400, 400)
                        y = random.randint(-200, 200)
                        browserl.set_window_size(length, width)
                        browserl.set_window_position(x, y)

                    browserl.get(paths[j])  # (?) 添加默认关闭浏览器声音功能
                    ctime = random.randint(basic_time, basic_time + floating_time[j])

                    if debug_mode:
                        if current_mode == "PC":
                            print('[{}]\t[THREAD-{}] [ROUND-{}] Waiting time: {} s\nWindow pixels: {}*{} || Windows position: {},{}\nCurrent Web path: {}'.format(current_mode, thread_id, i, ctime, length, width, x, y, paths[j]))
                        elif current_mode == "Android":
                            print('[{}]\t[THREAD-{}] [ROUND-{}] Waiting time: {} s\nCurrent Web path: {}'.format(current_mode, thread_id, i, ctime, paths[j]))
                        elif current_mode == "iOS":
                            print('[{}]\t[THREAD-{}] [ROUND-{}] Waiting time: {} s\nCurrent Web path: {}'.format(current_mode, thread_id, i, ctime, paths[j]))
                        else:
                            assert False
                        
                    # 分段睡眠 + 检查退出标志
                    for _ in range(ctime):
                        if exit_event.is_set(): break
                        time.sleep(1)
                except Exception as e:
                    print("[THREAD-{}] [Exception] {}".format(thread_id, e))
                finally:
                    if browserl:
                        browserl.quit()
                    browserl = None # 显式重置
    finally:
        if browserl:
            browserl.quit()
        browserl = None

if __name__ == "__main__":
    # 首次启动前若 selenium 版本不大于 4.6，则需要自己安装对应浏览器的 driver
    # 官方 ERROR 文档：https://www.selenium.dev/documentation/webdriver/troubleshooting/errors/driver_location/
    # 自动化解决方案 Webdriver Manager：https://github.com/SergeyPirogov/webdriver_manager
    # Salty Fish 大佬的帖子 https://im.salty.fish/index.php/archives/revengr-bilibili-352.html 研究 B 站风控底层机制
    # chrome(0, *parameters())

    threads = []
    # create
    for i in range(thread_num):
        if thread_num - 2 > 0 and i == thread_num - 2:
            threads.append(myThread(i, parameters("iOS")))
        elif thread_num - 1 > 0 and i == thread_num - 1:
            threads.append(myThread(i, parameters("Android")))
        else:
            threads.append(myThread(i, parameters("PC")))
    # start
    for i in range(thread_num):
        threads[i].start()
    print("\n\n----- START -----\n\n")
    try:
        while any(t.is_alive() for t in threads):
            for t in threads:
                t.join(timeout=0.1)
    except:
        print("\n\n----- Closing all sub-threads -----\n\n")
        exit_event.set()
    finally:
        for t in threads:
            if t.is_alive():
                t.join()
        print("\n\n----- Program Safely Exit ------\n\n")