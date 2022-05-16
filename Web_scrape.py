import re
from time import sleep
import pandas as pd
from requests_html import HTMLSession
from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException

details_dict = {"Product Name": [""], "Star rating": [""], "Review Rating": [""], "Was Price": [""],
                "Current price": [""], "Product Description": [""], "ASIN Number": [""], "Product URL": [""]}

counter = 0


def get_product_title(soup):
    elements = soup.find_all("span", class_="a-size-medium a-color-base a-text-normal")
    # print(elements)
    title_list = list()
    for element in elements:
        title_list.append(element.text)
    return title_list


def get_Product_urls(soup):
    elements = soup.find_all("h2", class_="a-size-mini a-spacing-none a-color-base s-line-clamp-2")
    # print(elements)
    links_list = list()
    for element in elements:
        links = element.find_all("a")
        for link in links:
            links_list.append("www.amazon.in" + link["href"])
    return links_list


def get_star_rating(soup):
    elements = soup.find_all("span", class_="a-icon-alt")
    # print(elements)
    star_list = [0]
    if (len(elements) != 0):
        star_list = list()
        for element in elements:
            star_list.append(element.text)
    return star_list


def get_review_rating(soup):
    elements = soup.find_all("span", class_="a-size-base s-underline-text")
    # print(elements)
    review_list = ['0']
    if (len(elements) != 0):
        review_list = list()
        for element in elements:
            review_list.append(element.text)
    return review_list


def get_was_price(soup):
    elements = soup.find_all("span", class_="a-price a-text-price")
    # print(elements)
    wprice_list = ["0"]
    if (len(elements) != 0):
        wprice_list = list()
        for element in elements:
            wprice_list.append(element.text)
    return wprice_list


def get_current_price(soup):
    elements = soup.find_all("span", class_="a-price-whole")
    # print(elements)
    price_list = ["0"]
    if (len(elements) != 0):
        price_list = list()
        for element in elements:
            price_list.append(element.text)
    return price_list


def get_asin_number(links_list):
    asin_list = [link.split('/')[3] for link in links_list]
    return asin_list


def get_sel_driver(links):
    link = "/" + links.split('/')[2] + "/" + links.split('/')[3]
    opt = Options()

    opt.add_argument("--disable-infobars")
    opt.add_argument("--disable-extensions")
    opt.add_argument('--log-level=OFF')
    # opt.add_argument('--silent')

    opt.add_experimental_option('excludeSwitches', ['enable-logging'])

    url = "https://www.amazon.in" + link
    driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=opt)
    driver.minimize_window()
    # Website URL
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()
    return soup


def get_product_details(links_list):
    product_details = list()
    for links in links_list:
        soup = get_sel_driver(links)
        elements = soup.find("ul", class_="a-unordered-list a-vertical a-spacing-mini")
        try:
            product_details.append(elements.text)
        except:
            product_details.append(None)

    return product_details


def Scrape(pages):
    print(pages)
    list_of_pages = [str(x) for x in range(1, pages + 1)]
    print(list_of_pages)
    global details_dict
    global counter
    s = HTMLSession()
    key_list = details_dict.keys()
    page = "1"
    for page in list_of_pages:
        product_name_list = list()
        while (len(product_name_list) == 0):
            URL = "https://www.amazon.in/s?k=laptops&i=computers&page=" + page
            r = s.get(URL)
            soup = BeautifulSoup(r.text, "html.parser")
            # print(soup)
            product_name_list = get_product_title(soup)
            if (len(product_name_list) == 0):
                sleep(5)
        elements = soup.find_all("div", {"data-asin": True, "data-component-type": "s-search-result"})
        counter = 0
        # print("#####################################################################"+str(len(elements)))
        print(f"page {page} contains {len(elements)} items")

        for x in elements:
            extract(x)
        for x in key_list:
            print(str(x) + ": " + str(len(details_dict[x])))
    return details_dict


def extract(x):
    # for x in elements:
    global counter
    counter += 1
    global details_dict
    product_name_list = get_product_title(x)
    details_dict["Product Name"].extend(product_name_list)
    star_rating = get_star_rating(x)
    details_dict["Star rating"].extend(star_rating)
    review_rating = get_review_rating(x)
    details_dict["Review Rating"].extend(review_rating)
    was_price = get_was_price(x)
    details_dict["Was Price"].extend(was_price)
    current_price = get_current_price(x)
    details_dict["Current price"].extend(current_price)
    links_list = get_Product_urls(x)
    details_dict["Product URL"].extend(links_list)
    asin_number = get_asin_number(links_list)
    details_dict["ASIN Number"].extend(asin_number)
    product_details = get_product_details(links_list)
    details_dict["Product Description"].extend(product_details)
    print(f"element {counter} done sucessfully")
    # print(details_dict)


def convert_to_xlsx(data):
    df = pd.DataFrame.from_dict(data=data)
    df.to_excel('/home/akash/Desktop/AMAZON_BS4/extracted_data.xlsx')

    # get_detail_dict(details_dict,links_list)

    # record_dict=dict()


if __name__ == "__main__":
    def get_page():
        try:
            page = int(input("Enter amount of pages to scrape"))
            return page
        except:
            print("Enter valid page number")
            get_page()

    data = Scrape(get_page())
    convert_to_xlsx(data)

# details_dict = {"Product Name": [], "Star rating": [], "Review Rating": [], "Was Price": [],
#                     "Current price": [], "Product Description": [], "ASIN Number": [], "Product URL": []}
# get_detail_dict(details_dict)
