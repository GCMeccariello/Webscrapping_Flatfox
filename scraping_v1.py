
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from urllib.request import Request, urlopen

from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
import numpy as np
import time
import csv
from lxml import etree


# htmlname = 'flatfox2.html'

def saveHTML(city):

    cities = {"Zurich": "https://flatfox.ch/de/search/?east=8.580500&north=47.401080&object_category=APARTMENT&object_category=HOUSE&offer_type=RENT&ordering=-price_display&south=47.317853&west=8.483802",
              "Basel": "https://flatfox.ch/de/search/?east=7.607400&north=47.576503&object_category=APARTMENT&object_category=HOUSE&offer_type=RENT&query=Basel&south=47.526936&west=7.558103",
              "Bern": "https://flatfox.ch/de/search/?east=7.478484&north=46.977448&object_category=APARTMENT&object_category=HOUSE&offer_type=RENT&query=Bern&south=46.908242&west=7.410441",
              "Winterthur": "https://flatfox.ch/de/search/?east=8.764165&north=47.536288&object_category=APARTMENT&object_category=HOUSE&offer_type=RENT&query=Winterthur&south=47.447408&west=8.675868",
              "Luzern": "https://flatfox.ch/de/search/?east=8.332481&north=47.077942&object_category=APARTMENT&object_category=HOUSE&offer_type=RENT&query=Luzern&south=47.011487&west=8.267018"}

    for c in city:
        url = cities[c]
        print(f'{c}: {cities[c]}')

        # url = 'https://flatfox.ch/de/search/?east=8.380181&north=47.098014&object_category=APARTMENT&object_category=HOUSE&ordering=date&south=47.007100&west=8.233954'
        driver = webdriver.Chrome()
        driver.get(url)

        driver.maximize_window()
        # time.sleep(2)

        for i in range(0, 50):
            if driver.find_element(by=By.XPATH, value='//*[@id="flat-search-widget"]/div/div[2]/div[2]/div[2]/button').text == 'Mehr anzeigen':
                driver.find_element(by=By.XPATH, value='//*[@id="flat-search-widget"]/div/div[2]/div[2]/div[2]/button').click()
                time.sleep(2)
            else:
                print('_______________ break _______________')
                break
            # time.sleep(2)

        with open(f'flatfox_{c}.html', 'w') as f:
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
    street = soup.find('div', class_='widget-listing-title').h2.text
    comma = 0
    for c in street:
        if c == ',':
            comma += 1

    street = soup.find('div', class_='widget-listing-title').h2.text.strip().split(sep=',')[0]

    # In some cases the streetadress is missing. therefore the sep=',' does not work.
    try:
        if comma == 2:
            zip = soup.find('div', class_='widget-listing-title').h2.text.strip().split(sep=',')[2].split()[0]
        else:
            zip = soup.find('div', class_='widget-listing-title').h2.text.strip().split(sep=',')[1].split()[0]
    except:
        street = 'no street available'
        zip = soup.find('div', class_='widget-listing-title').h2.text.strip().split(sep='-')[0].split()[0] # getting zip when street adress is missing
    try:
        if comma == 2:
            location = soup.find('div', class_='widget-listing-title').h2.text.strip().split(sep=',')[2].split()[1]
        else:
            location = soup.find('div', class_='widget-listing-title').h2.text.strip().split(sep=',')[1].split()[1]
    except:
        try:
            location = soup.find('div', class_='widget-listing-title').h2.text.strip().split(sep='-')[0].split()[1]
        except:
            location = 'NaN'

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


def room(path):
    html_text = requests.get(f'https://flatfox.ch{path}')
    soup = BeautifulSoup(html_text.content, 'html.parser')

    try:
        room = soup.find('div', class_='fui-with-sidebar fui-with-sidebar--right-sidebar').find('td', text='Anzahl Zimmer:').next_sibling.next_sibling.text.strip()
    except:
        room = 'NaN'

    return room


def area(path):
    html_text = requests.get(f'https://flatfox.ch{path}')
    soup = BeautifulSoup(html_text.content, 'html.parser')

    try:
        area = soup.find('div', class_='fui-with-sidebar fui-with-sidebar--right-sidebar').find('td', text='Wohnfläche:').next_sibling.next_sibling.text.strip()
    except:
        area = 'NaN'

    return area


def main(city):
    for c in city:
        csv_file = open(f"flatfox_{c}.csv", "w", newline='')
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(["Titel", 'Path', "Streetname", "Postalcode", "Location", "Price", 'Rooms', 'Area'])
        a = 0
        with open(f'flatfox_{c}.html', 'r') as html_file:
            content = html_file.read()
            soup = BeautifulSoup(content, 'lxml')
            div = soup.find_all('div', class_='listing-thumb')
            for d in div:
                row = []
                a = a + 1

                path = (d.find('a')['href'])
                print(f'{a} - {c}: {path}')

                titlename = title(path)
                streetname, zip, location = adress(path)
                priceamount = price(path)
                # priceamount2 = price2(path)
                roomamoount = room(path)
                areasize = area(path)

                row.append(titlename)
                row.append(path)
                row.append(streetname)
                row.append(zip)
                row.append(location)
                row.append(priceamount)
                # row.append(priceamount2)
                row.append(roomamoount)
                row.append(areasize)

                csv_writer.writerow(row)

                print(f'{a} - {c}: DONE')

        csv_file.close()

def file():
    file = pd.read_csv('flatfox_all.csv')
    # print(file)
    # print(file['Titel'])
    file2 = pd.DataFrame(file, columns=['Streetname', 'Postalcode', 'Location', 'Rooms', 'Area', 'Price'])
    file2.rename(columns = {'Streetname':'Strasse', 'Postalcode':'Postleitzahl', 'Location':'Ort', 'Rooms':'Anzahl Zimmer', 'Area':'Flaeche [m2]', 'Price':'Preis [CHF]'}, inplace=True)

    file2['Strasse'] = np.where(file2['Strasse'] == 'no street available', '', file2['Strasse'])
    file2['Preis [CHF]'] = np.where(file2['Preis [CHF]'] == 'Anfrage', '', file2['Preis [CHF]'])


    print(file2['Strasse'])

    file2.to_csv('flat.csv', index=False)



if __name__ == '__main__':
    start_time = time.time()

    city = ['Zurich', 'Basel', 'Bern', 'Winterthur', 'Luzern']
    # city1 = ['Basel']
    # saveHTML(city)
    # main(city)
    file()
    # x = "/de/wohnung/unterm-stallen-13-haus-b-4104-oberwil-bl/502721/"
    # adress(x)

    # print(cities["Zurich"])

    print(f"{(time.time() - start_time)/60} minutes")


# Zurich : https://flatfox.ch/de/search/?east=8.625334&north=47.555934&south=47.198443&west=8.447982
# Basel : https://flatfox.ch/de/search/?east=7.634148&north=47.589902&south=47.519342&west=7.554664
# Bern : https://flatfox.ch/de/search/?east=7.495550&north=47.158707&south=46.749839&west=7.294318
# Winterthur : https://flatfox.ch/de/search/?east=8.810331&north=47.533072&south=47.457945&west=8.656619
# Luzern : https://flatfox.ch/de/search/?east=8.358228&north=47.199614&south=46.903045&west=8.212001