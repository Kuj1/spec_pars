import os
import threading
import time
import re
import json
from datetime import datetime

import undetected_chromedriver as uc
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service

UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '\
                 'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'

data = os.path.join(os.getcwd(), 'vse.instr')
user_data = os.path.join(os.getcwd(), 'user_data')
drivers_dict = dict()

if not os.path.exists(data):
    os.mkdir(data)


# options = uc.ChromeOptions()
# options.headless = True
# options.keep_alive = True


def get_articles():
    articles = list()
    with open(os.path.join(user_data, 'vse.instr_article.txt'), 'r') as doc:
        for article in doc.readlines():
            mod_article = article.replace('\n', '').strip()
            articles.append(mod_article)

    return articles


def get_data():
    articles = get_articles()
    date_time = datetime.now().strftime('%d.%m.%Y_%H:%M')

    result_specs = list()
    # s = Service(f'{os.getcwd()}/chromedriver')
    for article in articles:
        print(f'[+] Article: {article}')
        url = 'https://www.vseinstrumenti.ru/search_main.php?what='
        mod_url = f'{url}{article}'

        options = uc.ChromeOptions()
        options.headless = True
        options.keep_alive = True

        driver = uc.Chrome(options=options)

        try:
            driver.get(mod_url)

            soup = BeautifulSoup(driver.page_source, 'html.parser')

            search_page = soup.find('div', class_='search-page').find('div', attrs={'data-behavior': "product-listing"})
            item = search_page.find('div', attrs={'data-position': '1'}).find('div', class_='title')
            item_url = item.find('a').get('href')
            if item_url.startswith('https'):
                driver.get(item_url)
                time.sleep(2)
                print(f'\t[+] Go to the item page: {item_url}')
            else:
                mod_item_url = f'https://www.vseinstrumenti.ru{item_url}'
                driver.get(mod_item_url)
                time.sleep(2)
                print(f'\t[+] Go to the item page: {mod_item_url}')

            soup_image = BeautifulSoup(driver.page_source, 'html.parser')

            spec_list = soup_image.find('section', class_='product-description').\
                find('div', class_='main').find('div', class_='features spoiler').\
                find('ul', class_='dotted-list').find_all('li', class_='item')

            specs_array = dict()
            for spec in spec_list:
                spec_name = spec.find('div', class_='option').find('div', class_='title').find('span', class_='text').text.strip()

                try:
                    spec_value = spec.find('span', class_='value').text.strip()
                except Exception:
                    spec_value = spec.find('div', class_='value').text.strip()

                specs_array[f'{spec_name}'] = f'{spec_value}'

            result_specs.append(
                {
                    f'{article}': specs_array
                }
            )

        except Exception as ex:
            driver.save_screenshot('ew.png')
            print(f'\t[-] {ex}')

        finally:
            driver.close()
            driver.quit()

    with open(os.path.join(data, f'vse.instr_{date_time}.json'), 'a') as file:
        json.dump(result_specs, file, ensure_ascii=False, indent=4)


def main():
    get_data()


if __name__ == '__main__':
    main()
