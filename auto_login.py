import ctypes
import os, sys, click, time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
import psutil
import requests

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
    time.sleep(0.5)
    if driver.current_url == 'http://202.114.177.246/srun_portal_success?ac_id=1&theme=pro':
        print("登录成功")


def logout(driver):
    el = driver.find_element(by=By.XPATH, value='//button[@id="logout"]')
    el.click()
    time.sleep(0.5)
    el = driver.find_element(by=By.XPATH, value='//button[@class="btn-confirm"]')
    el.click()
    time.sleep(0.5)
    print('已注销')


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        print('is_admin==false')
        return False


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
            if netinfo is not None and netinfo.isup:
                print("以太网重启成功")
                break
    else:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
        exit(0)


if __name__ == '__main__':
    # 初始化
    option = Options()
    option.add_argument('--headless')
    # option.add_argument('--no-sandbox')
    try:
        resp = requests.get(url, timeout=4)
    except:
        if is_admin():
            click.secho('当前为管理员权限', fg='yellow')
        else:
            print("当前为普通用户权限")
        click.secho("本地网络端口可能出现问题", fg='red')
        print('*'*20)
        print('1.重启以太网端口')
        print('其他.退出')
        print('*'*20)
        fun = input("请输入：")
        if fun == "1":
            reconnect()
        else:
            exit(1)
    driver = webdriver.Chrome(options=option)
    driver.set_page_load_timeout(10)  # 页面加载超时时间
    driver.set_script_timeout(10)  # 页面js加载超时时间
    try:
        driver.get(url)
        time.sleep(1)

        if driver.current_url == 'http://202.114.177.246/srun_portal_success?ac_id=1&theme=pro':
            print('已经登录')
            s = input("是否注销重连(y/n):")
            if s.lower() == 'y':
                logout(driver)
                login(driver)
            elif s.lower() == 'n':
                pass

        elif driver.current_url == 'http://202.114.177.246/srun_portal_pc?ac_id=1&theme=pro':
            login(driver)
    except Exception as e:
        print(e)
    finally:
        driver.quit()
