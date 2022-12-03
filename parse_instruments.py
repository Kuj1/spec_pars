import undetected_chromedriver as uc
from bs4 import BeautifulSoup

UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '\
                 'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'

URL = 'https://www.vseinstrumenti.ru/search_main.php?what=DF333DWYE'

options = uc.ChromeOptions()
options.headless = True
options.keep_alive = True


def get_data(url):
    driver = uc.Chrome(options=options)

    try:
        driver.get(url)

        soup = BeautifulSoup(driver.page_source, 'html.parser')

        search_page = soup.find('div', class_='search-page').find('div', attrs={'data-behavior': "product-listing"})
        item = search_page.find_all('div', class_='product-tile grid-item')[0].find('div', class_='title')
        item_url = item.find('a').get('href')
        print(item_url)

        driver.get(item_url)

        soup_image = BeautifulSoup(driver.page_source, 'html.parser')

        spec_list = soup_image.find('section', class_='product-description').\
            find('div', class_='main').find('div', class_='features spoiler').\
            find('ul', class_='dotted-list').find_all('li', class_='item')

        for spec in spec_list:
            spec_name = spec.find('div', class_='option').find('div', class_='title').find('span', class_='text').text.strip()

            try:
                spec_value = spec.find('span', class_='value').text.strip()
            except Exception as ex:
                spec_value = spec.find('div', class_='value').text.strip()

            print(f'{spec_name}: {spec_value}')

    except Exception as ex:
        print(ex)

    finally:
        driver.close()
        driver.quit()


def main():
    get_data(url=URL)


if __name__ == '__main__':
    main()
