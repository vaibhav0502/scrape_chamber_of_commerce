import sys
import requests
from bs4 import BeautifulSoup
from lxml import etree
from exception import CustomException
from logger import logging

def return_dom(link):
    try:
        page = requests.get(link)

        soup = BeautifulSoup(page.content, "html.parser")
        dom = etree.HTML(str(soup))
        return soup, dom
    except Exception as e:
        logging.error(CustomException(e, sys))
        return None, None

def return_href(dom, xp):
    try:
        results = dom.xpath(xp)
        link_lists = [link.get("href") for link in results]
        return link_lists
    except Exception as e:
        logging.error(CustomException(e, sys))
        return []

def get_business_directory():
    try:
        URL = "https://www.eastmeadowchamber.com/list/"
        soup, dom = return_dom(URL)

        xp = '//div[@id="gz-ql"]/ul/li/a'
        business_directory_link = return_href(dom, xp)
        
        return business_directory_link
    except Exception as e:
        logging.error(CustomException(e, sys))
        return []


def get_category(link):
    try:
        soup, dom = return_dom(link)
        
        xp = '//div[@class="row gz-cards gz-results-cards"]/div//div[@class="card-header"]/a'
        cat_link_lists = return_href(dom, xp)
        cat = ""
        try:
            cat = dom.xpath('//div[@class="flex-grow-1 gz-pagetitle"]/h1')[0].text
        except:
            pass

        return cat, cat_link_lists
    except Exception as e:
        logging.error(CustomException(e, sys))
        return '', []


def get_text(soup_, class_):
    try:
        txt = soup_.find(class_=class_).text
        if txt:
            return txt.strip().replace('\n', ' ')
        return None
    except Exception as e:
        logging.error(CustomException(e, sys))
        return None


def get_website(soup_, class_):
    try:
        txt = soup_.find(class_=class_).find('a')['href']
        if txt:
            return txt.strip()
        return None
    except Exception as e:
        logging.error(CustomException(e, sys))
        return None


def get_data(link):
    try:
        soup, dom = return_dom(link)
        company = get_text(soup, class_="gz-pagetitle")
        address = get_text(soup, class_="list-group-item gz-card-address")
        city = get_text(soup, class_="gz-address-city")
        phone = get_text(soup, class_="list-group-item gz-card-phone")
        email = get_text(soup, class_="list-group-item gz-card-email")
        name = get_text(soup, class_="gz-member-repname")
        website = get_website(soup, class_="list-group-item gz-card-website")

        data = {
            "company": company,
            "address": address,
            "city": city,
            "phone": phone,
            "email": email,
            'website':website,
            "name": name,
            "source_link":link
        }
        return data
    except Exception as e:
        logging.error(CustomException(e, sys))
        return {}

logging.info("START SCRAPING")
business_directory_link = get_business_directory()

logging.info(f"Scrape data for following links {business_directory_link}")

data_json = {}
i = 0

for bkl, link in enumerate(business_directory_link):
    cat, category_link_lists = get_category(link)
    data_json[cat] = {}
    i = 0

    logging.info(f"START:: Scraping for category {cat} and link {link}")
    for category_link in category_link_lists:
        logging.info(f"START:: Scraping for link {category_link}")
        data = get_data(category_link)
        data['category'] = cat
        data_json[cat][i] = data
        i+=1
    logging.info(f"END:: Scraping for category {cat}")

    if bkl == 3:
        break

logging.info("END SCRAPING")

import json
with open("sample.json", "w") as outfile:
    json.dump(data_json, outfile, indent=4)

logging.info("Dump data to json file")

