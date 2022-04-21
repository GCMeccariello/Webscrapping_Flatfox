
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from urllib.request import Request, urlopen

from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
import time
import csv


htmlname = 'flatfox.html'

def saveHTML():
    url = 'https://flatfox.ch/de/search/?east=8.380181&north=47.098014&object_category=APARTMENT&object_category=HOUSE&ordering=date&south=47.007100&west=8.233954'
    driver = webdriver.Chrome()
    driver.get(url)

    driver.maximize_window()
    time.sleep(2)
    for i in range(0, 10):
        driver.find_element(by=By.XPATH, value='//*[@id="flat-search-widget"]/div/div[2]/div[2]/div[2]/button').click()
        time.sleep(2)

    with open(htmlname, 'w') as f:
        f.write(driver.page_source)

    driver.quit()

def title(path):
    html_text = requests.get(f'https://flatfox.ch{path}').text
    soup = BeautifulSoup(html_text, 'lxml')

    title = soup.find('div', class_='widget-listing-title').h1.text.strip()
    return title


def adress(path):
    html_text = requests.get(f'https://flatfox.ch{path}').text
    soup = BeautifulSoup(html_text, 'lxml')

    street = soup.find('div', class_='widget-listing-title').h2.text.strip().split(sep=',')[0]

    # In some cases the streetadress is missing. therefore the sep=',' does not work.
    try:
        zip = soup.find('div', class_='widget-listing-title').h2.text.strip().split(sep=',')[1].split()[0]
    except:
        street = 'no street available'
        zip = soup.find('div', class_='widget-listing-title').h2.text.strip().split(sep='-')[0].split()[0] # getting zip when street adress is missing

    try:
        location = soup.find('div', class_='widget-listing-title').h2.text.strip().split(sep=',')[1].split()[1]
    except:
        location = soup.find('div', class_='widget-listing-title').h2.text.strip().split(sep='-')[0].split()[1]

    return street, zip, location


def price(path):
    html_text = requests.get(f'https://flatfox.ch{path}').text
    soup = BeautifulSoup(html_text, 'lxml')
    try:
        price = soup.find('div', class_='widget-listing-title').h2.text.strip().split(sep=',')[1].split(sep='-')[1].split()[1].replace("’", "")
    except:
        try:
            price = soup.find('div', class_='widget-listing-title').h2.text.strip().split(sep='-')[1].split()[1].replace("’", "")
        except:
            # some location name include a '-' for example rigi-kaltbad. Therefore the split indexing has to be on [2]
            price = soup.find('div', class_='widget-listing-title').h2.text.strip().split(sep='-')[2].split()[1].replace("’", "")

    return price


def main():
    csv_file = open("flatfox.csv", "w", newline='')
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(["Titel", "Streetname", "Postalcode", "Location", "Price"])
    a = 0
    with open(htmlname, 'r') as html_file:
        content = html_file.read()
        soup = BeautifulSoup(content, 'lxml')
        div = soup.find_all('div', class_='listing-thumb')
        for d in div:
            row = []

            path = (d.find('a')['href'])
            # print(path)

            titlename = title(path)
            streetname, zip, location = adress(path)
            priceamount = price(path)


            row.append(titlename)
            row.append(streetname)
            row.append(zip)
            row.append(location)
            row.append(priceamount)


            csv_writer.writerow(row)

            a = a+1
            print(f'{a} DONE')

    csv_file.close()

if __name__ == '__main__':
    # saveHTML()
    main()

    # x = "/de/wohnung/6356-rigi-kaltbad/590626/"
    # price(x)


