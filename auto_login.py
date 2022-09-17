import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options

url = 'http:202.114.177.246'
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

if __name__ == '__main__':
    # 初始化
    option = Options()
    option.add_argument('--headless')
    option.add_argument('--no-sandbox')
    driver = webdriver.Chrome(options=option)
    driver.set_page_load_timeout(60)  # 页面加载超时时间
    driver.set_script_timeout(60)  # 页面js加载超时时间
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

    driver.quit()
