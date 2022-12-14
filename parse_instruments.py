import os
import json
import time
from datetime import datetime

import undetected_chromedriver as uc
from bs4 import BeautifulSoup

UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '\
                 'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'

data = os.path.join(os.getcwd(), 'vse.instr')
user_data = os.path.join(os.getcwd(), 'user_data')
drivers_dict = dict()

if not os.path.exists(data):
    os.mkdir(data)


def get_articles():
    articles = list()
    with open(os.path.join(user_data, 'articles.txt'), 'r', encoding='utf-8') as doc:
        for article in doc.readlines():
            mod_article = article.replace('\n', '').strip()
            articles.append(mod_article)

    return articles


def get_data():
    articles = get_articles()

    result_specs = list()

    for article in articles:
        print(f'[+] Article: {article}')
        url = 'https://spb.vseinstrumenti.ru/search_main.php?what='
        mod_url = f'{url}{article}'

        options = uc.ChromeOptions()
        options.headless = True

        driver = uc.Chrome(options=options)

        with driver:
            try:
                driver.get(mod_url)

                soup = BeautifulSoup(driver.page_source, 'html.parser')

                try:
                    item_url = soup.find('div', class_='gfDJWv').\
                        find_all('div', attrs={'data-qa': "products-tile-horizontal"})[0].\
                        find('div', class_='elqw79').find_all('a')[0].get('href')
                except Exception:
                    print(f'\t[-] {article} Not found')

                if item_url.startswith('https'):
                    driver.get(item_url)
                    print(f'\t[+] Go to the item page: {item_url}')
                else:
                    mod_item_url = f'https://spb.vseinstrumenti.ru{item_url}'
                    driver.get(mod_item_url)
                    time.sleep(2)
                    print(f'\t[+] Go to the item page: {mod_item_url}')

                soup_image = BeautifulSoup(driver.page_source, 'html.parser')

                try:
                    item_name = soup_image.find('div', class_='content-heading').find('h1').text.strip()
                except Exception:
                    item_name = '?????? ????????????????'

                mid_specs_array = dict()

                try:
                    spec_list = soup_image.find('section', class_='product-description').\
                        find('div', class_='main').find('div', class_='features spoiler').\
                        find('ul', class_='dotted-list').find_all('li', class_='item')
                    for spec in spec_list:
                        spec_name = spec.find('div', class_='option').find('div', class_='title').find('span', class_='text').text.strip()

                        try:
                            spec_value = spec.find('span', class_='value').text.strip()
                        except Exception:
                            spec_value = spec.find('div', class_='value').text.strip()

                        mid_specs_array[f'{spec_name}'] = f'{spec_value}'
                except Exception:
                    mid_specs_array['??????????????????????????'] = '??????'

                mid_description_array = list()

                try:
                    description_item = soup_image.find('div', attrs={'itemprop': 'description'}).find_all('p')

                    for i in description_item:
                        description = i.text.replace('&nbsp;', '').strip()
                        mid_description_array.append(description)
                except Exception:
                    mid_description_array.append('?????? ????????????????')

                try:
                    brand_item = soup_image.find('div', class_='brand').find('img').get('alt')
                except Exception:
                    brand_item = '?????? ????????????'

                try:
                    homeland = soup_image.find_all('ul', class_='unordered-list')[0].find_all('li')[0].\
                        find('span').text.split('???')[0].strip()
                except Exception:
                    homeland = '?????? ????????????'

                try:
                    manufacturer = soup_image.find_all('ul', class_='unordered-list')[0].find_all('li')[1].\
                        find('span').text.split('???')[0].strip()
                except Exception:
                    manufacturer = '?????? ??????????????????????????'

                mid_equipment_array = list()

                try:
                    equipments_item = soup_image.find('div', class_='equipment spoiler').\
                        find('div', attrs={'data-selector': 'product-equipment'}).find('ul').find_all('li')

                    for i in equipments_item:
                        equipment = i.text.strip()
                        mid_equipment_array.append(equipment)
                except Exception:
                    mid_equipment_array.append('?????? ????????????????????????')

                mid_wrapper_array = list()

                try:
                    wrappers_item = soup_image.find_all('ul', class_='unordered-list')[1].find_all('li')

                    for i in wrappers_item:
                        wrapper_desc = i.text.strip()
                        mid_wrapper_array.append(wrapper_desc)
                except Exception:
                    mid_wrapper_array.append('?????? ???????????????????? ???? ????????????????')

                mid_advantages_array = list()

                try:
                    mob_item_url = f'https://m.vseinstrumenti.ru/' \
                                   f'{item_url.replace("https://www.vseinstrumenti.ru/", "").strip()}'
                    driver.get(mob_item_url)
                    time.sleep(1)

                    soup_mob_image = BeautifulSoup(driver.page_source, 'html.parser')
                except Exception as ex:
                    print(f'\t[-] {ex}')

                if homeland == '?????? ????????????':
                    try:
                        homeland = soup_mob_image.find('div', class_='good-description').\
                            find('ul', class_='countryList').find_all('li')[0].text.split('???')[0].strip()
                    except Exception:
                        homeland = '?????? ????????????'

                if manufacturer == '?????? ??????????????????????????':
                    try:
                        manufacturer = soup_mob_image.find('div', class_='good-description').\
                            find('ul', class_='countryList').find_all('li')[1].text.split('???')[0].strip()
                    except Exception:
                        manufacturer = '?????? ??????????????????????????'

                try:
                    advantages = soup_mob_image.find('div', class_='good-description').\
                        find('div', class_='text-block').find_all('div')[1].find('ul').find_all('li')

                    for i in advantages:
                        advantage = i.text.strip()
                        mid_advantages_array.append(advantage)
                except Exception:
                    mid_advantages_array.append('?????? ??????????????????????')

                result_specs.append(
                    {
                        f'{article}': {
                            '????????????????': item_name,
                            '??????????': brand_item,
                            '????????????': homeland,
                            '????????????????????????': manufacturer,
                            '????????????????????????': mid_equipment_array,
                            '????????????????????????????????????????': mid_wrapper_array,
                            '????????????????': mid_description_array,
                            '????????????????????????????': mid_specs_array,
                            '????????????????????????': mid_advantages_array,
                        }
                    }
                )

            except Exception as ex:
                print(f'\t[-] {ex}')

    return result_specs


def main():
    date_time = datetime.now().strftime('%d-%m-%Y_%H-%M')
    result = get_data()

    with open(os.path.join(data, f'vse_instr_{date_time}.json'), 'a', encoding='utf-8') as file:
        json.dump(result, file, ensure_ascii=False, indent=4, )

    with open(os.path.join(data, f'vse.instr_{date_time}.txt'), 'a', encoding='utf-8') as file:
        for i in result:
            file.write(f'{i}\n')


if __name__ == '__main__':
    main()
