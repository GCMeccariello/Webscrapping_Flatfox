
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


def saveHTML(city):

    cities = {"Zurich": "https://flatfox.ch/de/search/?east=8.572811&is_furnished=false&north=47.408009&object_category=APARTMENT&offer_type=RENT&ordering=date&south=47.332499&west=8.490712",
              "Basel": "https://flatfox.ch/de/search/?east=7.609728&is_furnished=false&north=47.576021&object_category=APARTMENT&offer_type=RENT&ordering=date&query=Basel&south=47.534973&west=7.564940",
              "Bern": "https://flatfox.ch/de/search/?east=7.478484&north=46.977448&object_category=APARTMENT&object_category=HOUSE&offer_type=RENT&query=Bern&south=46.908242&west=7.410441",
              "Winterthur": "https://flatfox.ch/de/search/?east=8.764165&north=47.536288&object_category=APARTMENT&object_category=HOUSE&offer_type=RENT&query=Winterthur&south=47.447408&west=8.675868",
              "Luzern": "https://flatfox.ch/de/search/?east=8.332481&north=47.077942&object_category=APARTMENT&object_category=HOUSE&offer_type=RENT&query=Luzern&south=47.011487&west=8.267018"}

    for c in city:
        url = cities[c]
        print(f'{c}: {cities[c]}')

        driver = webdriver.Chrome()
        driver.get(url)

        driver.maximize_window()

        for i in range(0, 50):
            if driver.find_element(by=By.XPATH, value='//*[@id="flat-search-widget"]/div/div[2]/div[2]/div[2]/button').text == 'Mehr anzeigen':
                driver.find_element(by=By.XPATH, value='//*[@id="flat-search-widget"]/div/div[2]/div[2]/div[2]/button').click()
                time.sleep(2)
            else:
                print('_______________ break _______________')
                break

        with open(f'flatfox_{c}.html', 'w') as f:
            f.write(driver.page_source)

        driver.quit()


def title(soup):
    title = soup.find('div', class_='widget-listing-title').h1.text.strip()
    return title


def adress(soup):
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


def price(soup):
    try:
        price = soup.find('div', class_='widget-listing-title').h2.text.strip().split(sep=',')[1].split(sep='-')[1].split()[1].replace("’", "")
    except:
        try:
            price = soup.find('div', class_='widget-listing-title').h2.text.strip().split(sep='-')[1].split()[1].replace("’", "")
        except:
            # some location name include a '-' for example rigi-kaltbad. Therefore the split indexing has to be on [2]
            price = soup.find('div', class_='widget-listing-title').h2.text.strip().split(sep='-')[2].split()[1].replace("’", "")

    return price


def room(soup):
    try:
        room = soup.find('div', class_='fui-with-sidebar fui-with-sidebar--right-sidebar').find('td', text='Anzahl Zimmer:').next_sibling.next_sibling.text.strip()
    except:
        room = 'NaN'

    return room


def area(soup):
    try:
        area = soup.find('div', class_='fui-with-sidebar fui-with-sidebar--right-sidebar').find('td', text='Wohnfläche:').next_sibling.next_sibling.text.strip()
    except:
        area = 'NaN'

    return area


def main(city):

    csv_file = open(f"flatfox_src.csv", "w", newline='')
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(["Titel", 'Path', "Streetname", "Postalcode", "Location", "Price", 'Rooms', 'Area'])
    a = 0
    for c in city:
        with open(f'flatfox_{c}.html', 'r') as html_file:
            content = html_file.read()
            soup = BeautifulSoup(content, 'lxml')
            div = soup.find_all('div', class_='listing-thumb')
            for d in div:
                path = (d.find('a')['href'])

                a = a + 1

                html_text = requests.get(f'https://flatfox.ch{path}').text
                soup = BeautifulSoup(html_text, 'lxml')

                print(f'{a} - {c}: {path}')

                titlename = title(soup)
                streetname, zip, location = adress(soup)
                priceamount = price(soup)
                roomamoount = room(soup)
                areasize = area(soup)

                row = []
                row.append(titlename)
                row.append(path)
                row.append(streetname)
                row.append(zip)
                row.append(location)
                row.append(priceamount)
                row.append(roomamoount)
                row.append(areasize)

                csv_writer.writerow(row)

                print(f'{a} - {c}: DONE')

    csv_file.close()

def file():
    file = pd.read_csv('flatfox_src.csv')
    # print(file)
    # print(file['Titel'])

    file2 = pd.DataFrame(file, columns=['Streetname', 'Postalcode', 'Location', 'Rooms', 'Area', 'Price'])
    file2.rename(columns = {'Streetname':'Strasse', 'Postalcode':'Postleitzahl', 'Location':'Ort', 'Rooms':'Anzahl Zimmer', 'Area':'Flaeche [m2]', 'Price':'Preis [CHF]'}, inplace=True)

    # changing "no street available" with an empty field.
    file2['Strasse'] = np.where(file2['Strasse'] == 'no street available', '', file2['Strasse'])
    # changing "Anfrage" with an empty field
    file2['Preis [CHF]'] = np.where(file2['Preis [CHF]'] == 'Anfrage', '', file2['Preis [CHF]'])

    # taking out "m2"
    file2["Flaeche [m2]"] = file2["Flaeche [m2]"].str.rsplit().str[0]

    # changing "1/2" with ".5"
    file2["Anzahl Zimmer"] = file2["Anzahl Zimmer"].str.replace(" ½", ".5", regex=True)

    # "Lucerne" to "Luzern"
    file2["Ort"] = file2["Ort"].replace('Lucerne', 'Luzern')
    # "Zurich" to "Zürich"
    file2["Ort"] = file2["Ort"].replace('Zurich', 'Zürich')

    # some Locations are written with lowercase letters
    file2["Ort"] = file2["Ort"].str.capitalize()

    file2.drop(file2[(file2['Ort'] != "Zürich") & (file2['Ort'] != "Basel") & (file2['Ort'] != "Bern") & (file2['Ort'] != "Winterthur") & (file2['Ort'] != "Luzern")].index, inplace=True)

    file2.to_csv('flatfox_stage.csv', index=False)



if __name__ == '__main__':
    start_time = time.time()

    city = ['Zurich', 'Basel', 'Bern', 'Winterthur', 'Luzern']

    # saveHTML(city)
    # main(city)
    file()

    print(f"{(time.time() - start_time)/60} minutes")
