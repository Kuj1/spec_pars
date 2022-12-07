import os
import time
import re
import json
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
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

API = 'dcd30132e329c316dcd003ebcb12f980'

# URL = 'https://market.yandex.ru/search?text=DF333DWYE'

captcha_img = os.path.join(os.getcwd(), 'captcha_img')
data = os.path.join(os.getcwd(), 'ya.market')
user_data = os.path.join(os.getcwd(), 'user_data')

if not os.path.exists(captcha_img):
    os.mkdir(captcha_img)

if not os.path.exists(data):
    os.mkdir(data)


options = webdriver.ChromeOptions()
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_argument(f'--user-agent={UA}')
options.add_argument('start-maximized')
options.add_argument('--headless')
options.add_argument('--enable-javascript')


def bypass_text_captcha(api, img):
    path_img = os.path.join(captcha_img, img)

    with open(path_img, "rb") as img_file:

        data = (
            ('key', (None, f'{api}')),
            ('file', img_file),
            )

        post_captcha = requests.post(f'http://rucaptcha.com/in.php', files=data, headers=HEADERS)
        id_captcha = post_captcha.text.strip().split('|')[1]
        time.sleep(5)

        res_captcha = requests.get(f'http://rucaptcha.com/res.php?key={api}&action=get&id={id_captcha}')
        result = res_captcha.text
        if result == 'CAPCHA_NOT_READY':
            while result == 'CAPCHA_NOT_READY':
                res_captcha = requests.get(f'http://rucaptcha.com/res.php?key={api}&action=get&id={id_captcha}')
                result = res_captcha.text
                time.sleep(5)
                if result != 'CAPCHA_NOT_READY':
                    result = res_captcha.text.strip().split('|')[1]
                    return result
        else:
            result = res_captcha.text.strip().split('|')[1]
            return result


def get_photo(url, id_img):
    try:
        img_resp = requests.get(url, headers=HEADERS)

        name_img = f'{id_img}.jpg'

        with open(os.path.join(captcha_img, name_img), 'wb') as file:
            file.write(img_resp.content)

    except Exception as ex:
        print(ex)


def input_elem(elem, key, key_bind):
    elem.clear()
    elem.send_keys(key, key_bind)


def bypass_captcha(driver, timeout):
    # Block of code to bypass yandex click captcha
    try:
        WebDriverWait(driver, timeout). \
            until(EC.presence_of_element_located((By.XPATH, '//input[@type="submit"]'))).click()
        print('\t[+] SmartCaptcha solved')

        # Block of code, if after click captcha goes text captcha
        try:
            img = WebDriverWait(driver, timeout). \
                until(EC.presence_of_element_located((By.CLASS_NAME, 'AdvancedCaptcha-Image')))

            if img:
                soup = BeautifulSoup(driver.page_source, 'html.parser')

                src_img = soup.find('div', class_='AdvancedCaptcha'). \
                    find('div', class_='AdvancedCaptcha-View').find('img', class_='AdvancedCaptcha-Image').get('src')
                print(f'[+] Captcha image: {src_img}')
                img_id = src_img.split('/')[-1]

                get_photo(url=src_img, id_img=img_id)
                text_captcha_result = bypass_text_captcha(api=API, img=f'{img_id}.jpg')

                enter_captcha = WebDriverWait(driver, timeout).\
                    until(EC.presence_of_element_located((By.CLASS_NAME, 'Textinput-Control')))
                input_elem(enter_captcha, text_captcha_result, Keys.ENTER)

                print('\t[+] TextCaptcha solved')
                print(f'\t\t[+] Answer: {text_captcha_result}')
            else:
                pass

        except Exception as ex:
            print('\t[+] No TextCaptcha')

    except Exception as ex:
        print('\t[+] No SmartCaptcha')


def get_articles():
    articles = list()
    with open(os.path.join(user_data, 'ya.market_article.txt'), 'r') as doc:
        for article in doc.readlines():
            mod_article = article.replace('\n', '').strip()
            articles.append(mod_article)

    return articles


def get_data():
    articles = get_articles()
    date_time = datetime.now().strftime('%d.%m.%Y_%H:%M')

    result_specs = list()
    for article in articles:
        print(f'[+] Article: {article}')
        url = 'https://market.yandex.ru/search?text='
        mod_url = f'{url}{article}'

        s = Service(f'{os.getcwd()}/chromedriver')
        driver = webdriver.Chrome(options=options, service=s)
        timeout = 5

        try:
            driver.get(mod_url)
            bypass_captcha(driver=driver, timeout=timeout)

            items_soup = BeautifulSoup(driver.page_source, 'html.parser')

            try:
                item = items_soup.find('main', attrs={'id': 'main'}).\
                    find('div', attrs={'data-test-id': 'virtuoso-item-list'}).\
                    find('div', attrs={'data-index': "0"}).find('a').get('href').strip().split('?')[0]
                item_url = f'https://market.yandex.ru{item}'
            except Exception:
                item = items_soup.find('main', attrs={'id': 'main'}). \
                    find('div', attrs={'data-test-id': 'virtuoso-item-list'}). \
                    find('div', attrs={'data-index': "1"}).find('a').get('href').strip().split('?')[0]
                item_url = f'https://market.yandex.ru{item}'
            print(f'\t[+] Go to the item page: {item_url}')

            driver.get(item_url)
            bypass_captcha(driver=driver, timeout=timeout)

            spec_soup = BeautifulSoup(driver.page_source, 'html.parser')
            spec = spec_soup.find('a', string=re.compile('Характеристики')).get('href').strip()
            spec_url = f'https://market.yandex.ru{spec}'
            print(f"\t[+] Go to the item specs page: {spec_url}")

            driver.get(spec_url)
            bypass_captcha(driver=driver, timeout=timeout)
            time.sleep(3)

            specs_soup = BeautifulSoup(driver.page_source, 'html.parser')

            specs = specs_soup.find('div', attrs={'data-auto': 'product-full-specs'}).find_all('div', class_='la3zd')

            specs_array = dict()
            try:
                for each_section_spec in specs:
                    section_specs = each_section_spec.find('div', class_='_18fxQ').find_all('dl', class_='sZB0N')
                    for each_spec in section_specs:
                        name_spec = each_spec.find('dt', class_='_1viar').find('div', class_='_2TxqA').find('span').\
                            text.strip()
                        try:
                            value_spec = each_spec.find('div', class_='cia-vs cia-cs').find('dd').text.strip()
                        except Exception:
                            value_spec = each_spec.find('div', class_='_2Yndd').find('dd').text.strip()

                        specs_array[f'{name_spec}'] = f'{value_spec}'
            except Exception:
                specs_array['Характеристик'] = 'Нет'

            result_specs.append(
                {
                    f'{article}': specs_array
                }
            )

        except Exception as ex:
            print(f'\t[-] {ex}')

        finally:
            driver.close()
            driver.quit()

    with open(os.path.join(data, f'ya.market_{date_time}.json'), 'a') as file:
        json.dump(result_specs, file, ensure_ascii=False, indent=4)


def main():
    get_data()


if __name__ == '__main__':
    main()
