import os.path

import undetected_chromedriver as uc
import requests
from bs4 import BeautifulSoup
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

URL = 'https://market.yandex.ru/search?cvredirect=2&text=DF333DWYE'

captcha_img = os.path.join(os.getcwd(), 'captcha_img')

if not os.path.exists(captcha_img):
    os.mkdir(captcha_img)

options = uc.ChromeOptions()
options.headless = True
options.keep_alive = True
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_argument(f'--user-agent={UA}')
options.add_argument('start-maximized')
options.add_argument('--enable-javascript')


def get_photo(url, id_img):
    try:
        img_resp = requests.get(url, headers=HEADERS)

        with open(os.path.join(captcha_img, f'{id_img}.jpg'), 'wb') as file:
            file.write(img_resp.content)

    except Exception as ex:
        print(ex)


def get_data(url):
    driver = uc.Chrome(options=options)
    timeout = 3

    try:
        driver.get(url)

        # Block of code to bypass yandex click captcha
        try:
            WebDriverWait(driver, timeout).\
                until(EC.presence_of_element_located((By.XPATH, '//input[@type="submit"]'))).click()

            # Block of code, if after click captcha goes text captcha
            try:
                img = WebDriverWait(driver, timeout). \
                    until(EC.presence_of_element_located((By.CLASS_NAME, 'AdvancedCaptcha-Image')))

                if img:
                    soup = BeautifulSoup(driver.page_source, 'html.parser')

                    src_img = soup.find('div', class_='AdvancedCaptcha').\
                        find('div', class_='AdvancedCaptcha-View').find('img', class_='AdvancedCaptcha-Image').get('src')
                    print(src_img)
                    img_id = src_img.split('/')[-1]

                    get_photo(url=src_img, id_img=img_id)

            except Exception as ex:
                driver.save_screenshot('foo.png')
                print('No SmartCaptcha')

        except Exception as ex:
            print('No captcha at all')

    except Exception as ex:
        print(ex)

    finally:
        driver.close()
        driver.quit()


def main():
    get_data(url=URL)


if __name__ == '__main__':
    main()
