import ctypes
import os, sys, click, time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
import psutil
import requests
import json
import re
import asyncio
import aioconsole

url = 'http://202.114.177.246'
username = '用户名'
password = '密码'
company = "运营商"


def login(driver):
    el = driver.find_element(by=By.XPATH, value='//input[@id="username" and @class="input-box"]')
    el.clear()
    el.send_keys(username)
    el = driver.find_element(by=By.XPATH, value='//input[@id="password" and @class="input-box"]')
    el.clear()
    el.send_keys(password)
    el = driver.find_element(by=By.XPATH, value='//select[@id="domain"]')
    sl = Select(el)
    sl.select_by_visible_text(company)
    el = driver.find_element(by=By.XPATH, value='//button[@id="login-account"]')
    el.click()
    time.sleep(0.8)
    if re.search(r'srun_portal_success', driver.current_url) is not None:
        print("登录成功")
    else:
        click.secho("登录失败", fg='red')
        t = input("是否删除账户密码信息(y/n):")
        if t == 'y':
            config_path = get_configfile_path()
            if os.path.exists(config_path):
                os.remove(config_path)
                click.secho("已删除配置文件al-config.json", fg='red')
            else:
                print('配置文件不存在')
        click.secho("按任意键退出")
        click.getchar()


def logout(driver):
    el = driver.find_element(by=By.XPATH, value='//button[@id="logout"]')
    el.click()
    time.sleep(0.8)
    el = driver.find_element(by=By.XPATH, value='//button[@class="btn-confirm"]')
    el.click()
    time.sleep(0.8)
    if re.search(r'srun_portal_pc', driver.current_url) is not None:
        print('已注销')
    else:
        click.secho('注销失败', fg='red')


# 判断当前的用户权限
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        print('is_admin==false')
        return False


# 断开重连以太网
def reconnect():
    if is_admin():
        disable_cmd = 'netsh interface set interface 以太网 disabled'
        os.system(disable_cmd)
        print('以太网接口关闭')
        disable_cmd = 'netsh interface set interface 以太网 enabled'
        os.system(disable_cmd)
        click.secho("正在重连，请稍等...", fg='green')
        while True:
            netinfo = psutil.net_if_stats().get('以太网')
            # 当以太网连接上后跳出循环等待
            if netinfo is not None and netinfo.isup:
                print("以太网重启成功")
                break
    else:
        # 用管理员权限重新运行（新开一个窗口）
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
        # 关闭当前的窗口
        sys.exit(0)


def get_configfile_path() -> str:
    filename = 'al-config.json'
    # 判断是冻结exe还是脚本
    if hasattr(sys, 'frozen'):
        p = os.path.dirname(sys.executable)
    else:
        p = os.path.dirname(__file__)
    return os.path.join(p, filename)


def init_param():
    global username, password, company
    config_path = get_configfile_path()
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            j = json.load(f)
        username = j.get('username')
        company = j.get('company')
        password = j.get('password')
    else:
        click.secho('未找到配置文件', fg='yellow')
        print("请按照提示创建配置文件")
        while True:
            user = input('请输入用户名:')
            pwd = input('请输入密码:')
            com = input('请输入运营商(校园网/中国移动/中国联通/中国电信):')
            print('*' * 20)
            print(f"用户名:{user}\n密码:{pwd}\n运营商:{com}")
            flag = input('是否保存(y/n):')
            if flag == 'y':
                username = user
                password = pwd
                company = com
                break
        # 保存为json文件
        jsonstr = {'username': username, 'password': password, 'company': company}
        with open(config_path, 'w') as f:
            json.dump(jsonstr, f)
        click.secho(config_path, fg='green')

async def input_func(loop):
    t = loop.create_task(aioconsole.ainput('是否注销重连(y/n,5s后默认为否):'))
    try:
        await asyncio.wait_for(t, timeout=5)
        value = t.result()
    except asyncio.TimeoutError as _:
        value = 'n'
    return value
if __name__ == '__main__':

    init_param()
    # 初始化
    option = Options()
    option.add_argument('--headless')
    loop = asyncio.get_event_loop()
    try:
        resp = requests.get(url, timeout=4)
    except:
        if is_admin():
            click.secho('当前为管理员权限', fg='yellow')
        else:
            print("当前为普通用户权限")
        click.secho("无法访问目标网站", fg='red')
        print('*' * 20)
        print('1.重启以太网端口')
        print('其他.退出')
        print('*' * 20)
        fun = input('请输入:')
        if fun == "1":
            reconnect()
        else:
            sys.exit(1)
    driver = webdriver.Chrome(options=option)
    driver.set_page_load_timeout(10)  # 页面加载超时时间
    driver.set_script_timeout(10)  # 页面js加载超时时间
    try:
        driver.get(url)
        time.sleep(0.8)
        # 处理已经已经登录的情况
        if re.search(r'srun_portal_success', driver.current_url) is not None:
            click.secho('已经登录', fg='green')
            # 使用异步操作，实现定时输入
            s = loop.run_until_complete(input_func(loop))
            if s.lower() == 'y':
                logout(driver)
                login(driver)
            elif s.lower() == 'n':
                pass
        # 未登录情况
        elif re.search(r'srun_portal_pc', driver.current_url) is not None:
            login(driver)
    except Exception as e:
        print(e)
    finally:
        # 释放资源
        loop.close()
        driver.quit()
