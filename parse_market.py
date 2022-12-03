import os.path
import time
import re

import undetected_chromedriver as uc
import requests
from bs4 import BeautifulSoup
from selenium.common import TimeoutException
from selenium.webdriver import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '\
                 'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'

HEADERS = {
    'user-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                 'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
}

URL = 'https://market.yandex.ru/search?text=DF333DWYE'

captcha_img = os.path.join(os.getcwd(), 'captcha_img')

if not os.path.exists(captcha_img):
    os.mkdir(captcha_img)

options = uc.ChromeOptions()
options.headless = True


def get_photo(url, id_img):
    try:
        img_resp = requests.get(url, headers=HEADERS)

        with open(os.path.join(captcha_img, f'{id_img}.jpg'), 'wb') as file:
            file.write(img_resp.content)

    except Exception as ex:
        print(ex)


def bypass_captcha(driver, timeout):
    # Block of code to bypass yandex click captcha
    try:
        WebDriverWait(driver, timeout). \
            until(EC.presence_of_element_located((By.XPATH, '//input[@type="submit"]'))).click()
        print('[+] Captcha solved')

        # Block of code, if after click captcha goes text captcha
        try:
            img = WebDriverWait(driver, timeout). \
                until(EC.presence_of_element_located((By.CLASS_NAME, 'AdvancedCaptcha-Image')))

            if img:
                soup = BeautifulSoup(driver.page_source, 'html.parser')

                src_img = soup.find('div', class_='AdvancedCaptcha'). \
                    find('div', class_='AdvancedCaptcha-View').find('img', class_='AdvancedCaptcha-Image').get('src')
                print(src_img)
                img_id = src_img.split('/')[-1]

                get_photo(url=src_img, id_img=img_id)
            else:
                pass

        except Exception as ex:
            print('[+] No SmartCaptcha')

    except Exception as ex:
        print('[+] No captcha at all')


def get_data(url):
    driver = uc.Chrome(options=options)
    timeout = 5
    driver.set_page_load_timeout(timeout)

    try:
        driver.get(url)

        bypass_captcha(driver=driver, timeout=timeout)
        # time.sleep(15)

        items_soup = BeautifulSoup(driver.page_source, 'html.parser')

        item = items_soup.find('main', attrs={'id': 'main'}).find('div', attrs={'data-test-id': 'virtuoso-item-list'}).find_all('div')[1].find('a').get('href').strip().split('?')[0]
        item_url = f'https://market.yandex.ru{item}'
        print(f'[+] Go to the item page: {item_url}')

        driver.get(item_url)
        driver.save_screenshot('fi1.png')
        # bypass_captcha(driver=driver, timeout=timeout)

        spec_soup = BeautifulSoup(driver.page_source, 'html.parser')
        spec = spec_soup.find('a', string=re.compile('Характеристики')).get('href').strip()
        spec_url = f'https://market.yandex.ru{spec}'
        print(f"[+] Go to the item specs page: {spec_url}")

        driver.get(spec_url)
        driver.save_screenshot('fi2.png')

    except TimeoutException as ex:
        driver.save_screenshot('ew.png')
        print(f'[-] {ex}')

    finally:
        driver.close()
        driver.quit()


def main():
    get_data(url=URL)


if __name__ == '__main__':
    main()
