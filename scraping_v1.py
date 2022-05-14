from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
import numpy as np
import time


def saveHTML(city):
    """
    This function opens a chromedriver for the cities Zurich, Basel, Bern, Winterthur and Luzern.
    It scrolls always to the bottom of the page and clicks the button "Mehr anzeigen" until the button changes its text which means, we are at the buttom of the side.
    Finally it saves the entire html text in "flatfox_[Cityname].html"
    """

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
            #If button text is 'Mehr anzeigen' the button will be clicket. Otherwise we are on the bottom of the page. And we break out of the loop.
            if driver.find_element(by=By.XPATH, value='//*[@id="flat-search-widget"]/div/div[2]/div[2]/div[2]/button').text == 'Mehr anzeigen':
                driver.find_element(by=By.XPATH, value='//*[@id="flat-search-widget"]/div/div[2]/div[2]/div[2]/button').click()
                time.sleep(2)
            else:
                print('_______________ break _______________')
                break
        # saving for every city in separate html files.
        with open(f'flatfox_{c}.html', 'w') as f:
            f.write(driver.page_source)

        driver.quit()

def title(soup):
    """
    This functions searches the title of the appartment advertisement and returns it.
    The white spaces are already removed with the strip-function
    """
    title = soup.find('div', class_='widget-listing-title').h1.text.strip()
    return title

def adress(soup):
    """
    This functions looks for the adress of the appartment. It separates streetname, the postalcode, and location.
    """
    street = soup.find('div', class_='widget-listing-title').h2.text
    comma = 0
    # this loops counts the commas in the text. The commas are used to separate the streetnames, postalcodes and location in the announcement.
    # this is important because in some cases, the streetname is missing.
    for c in street:
        if c == ',':
            comma += 1

    street = soup.find('div', class_='widget-listing-title').h2.text.strip().split(sep=',')[0]

    # In some cases the streetadress is missing. therefore the sep=',' does not work.
    # the try and except are used when trying to split a specific part. In some cases a comma was used instead of "-".
    # All the different variations of writing style are filtered out which the conditions and the right indexing of the searched text.
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
    # finally returns streetname, postalcode and location name
    return street, zip, location


def price(soup):
    """
    This function finds the prices for the appartments. Even here are differences on the individuel pages.
    With try and except the different writing styles are found and processed accordingly.
    Additionally, all the "'" in the prices are removed. ex. 1'200 -> 1200
    """
    try:
        price = soup.find('div', class_='widget-listing-title').h2.text.strip().split(sep=',')[1].split(sep='-')[1].split()[1].replace("’", "")
    except:
        try:
            price = soup.find('div', class_='widget-listing-title').h2.text.strip().split(sep='-')[1].split()[1].replace("’", "")
        except:
            # some location name include a '-' for example rigi-kaltbad. Therefore the split indexing has to be on [2]
            price = soup.find('div', class_='widget-listing-title').h2.text.strip().split(sep='-')[2].split()[1].replace("’", "")
    # finally the price is returned.
    return price


def room(soup):
    """
    This functions looks for the amount of rooms in the appartment.
    This part was tricky because the amount of rooms was not listet always in the same row in the table.
    But changed in every announcement. Therefore the idea is to look for the text "Anzahl Zimmer:" and then two times the next sibling.
    In some cases the amount of rooms was not written, then we write 'NaN'
    """
    try:
        room = soup.find('div', class_='fui-with-sidebar fui-with-sidebar--right-sidebar').find('td', text='Anzahl Zimmer:').next_sibling.next_sibling.text.strip()
    except:
        room = 'NaN'
    # finally the amount of rooms is returned.
    return room


def area(soup):
    """
    This function looks for the area of the appartment. The same strategy as in "def rooms" was used with the "next_siblings".
    Because the area was not always on the same row in the table, but changes for every individual appartment.
    """
    try:
        area = soup.find('div', class_='fui-with-sidebar fui-with-sidebar--right-sidebar').find('td', text='Wohnfläche:').next_sibling.next_sibling.text.strip()
    except:
        area = 'NaN'
    # finally the area is returned
    return area


def main(city):
    """
    This is the main function of the entire script.
    It opens in a loop all the already saved html for all the individual cities.
    In the html file is only looked for all the a-tags which are the links to every announcement.
    The link is saved in "path" and then a request is made with that path which is saved in "soup" variable.
    The variable is given to all the function (title, adress, price, room and area)
    Finally it is written in the dataframe and saved as 'flatfox_src.csv'
    """
    df = pd.DataFrame()
    a = 0
    # iterating through all cities
    for c in city:
        # opening the corresponding html file
        with open(f'flatfox_{c}.html', 'r') as html_file:
            content = html_file.read()
            soup = BeautifulSoup(content, 'lxml')
            # searching the div with the corresponding paths to the announcements
            div = soup.find_all('div', class_='listing-thumb')
            # iterating through the divs
            for d in div:
                # saving the link to the announcement in "path"
                path = (d.find('a')['href'])
                # just a counter for the print function to take track of how many announcements were scrapped.
                a = a + 1
                # making the request to get to the individual announcement
                html_text = requests.get(f'https://flatfox.ch{path}').text
                soup = BeautifulSoup(html_text, 'lxml')

                print(f'{a} - {c}: {path}')
                # calling all function to scrape and save the findings in new variables
                titlename = title(soup)
                streetname, zip, location = adress(soup)
                priceamount = price(soup)
                roomamoount = room(soup)
                areasize = area(soup)
                # write it in the dataframe.
                df = df.append({"Titel": titlename,
                                "Path": path,
                                "Streetname": streetname,
                                "Postalcode": zip,
                                "Location": location,
                                "Price": priceamount,
                                "Rooms": roomamoount,
                                "Area": areasize}, ignore_index=True)
                # saving the dataframe to a csv file named "flatfox_src.csv" which will be cleaned in the next step.
                df.to_csv('flatfox_src.csv', index=False)
                print(f'{a} - {c}: DONE')

def cleaning():
    """
    This function opens the file "flatfox_src.csv" file and cleanes it.
    Different steps are made. Column names are changes, the position of columns are changed.
    It was also worked with numpy and not only pandas.
    After the cleaning process the file is saved as 'flatfox_stage.csv'
    """
    file = pd.read_csv('flatfox_src.csv')

    # changing order of columns and renaming it
    file2 = pd.DataFrame(file, columns=['Streetname', 'Postalcode', 'Location', 'Rooms', 'Area', 'Price'])
    file2.rename(columns = {'Streetname':'Strasse', 'Postalcode':'Postleitzahl', 'Location':'Ort', 'Rooms':'Anzahl Zimmer', 'Area':'Flaeche [m2]', 'Price':'Preis [CHF]'}, inplace=True)

    # changing "no street available" with an empty field. With numpy
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

    # changing all streets which ends with "Strasse" to "str."
    file2["Strasse"] = file2['Strasse'].replace('[sS]trasse', 'str.', regex=True)

    # some Locations are written with lowercase letters
    file2["Ort"] = file2["Ort"].str.capitalize()
    # some streets are written with lowercase letters. With 'capitalize()' would only the first word in the streetname be written Uppercase.
    # with "title()" every word in a string is capitalized.
    file2['Strasse'] = file2['Strasse'].str.title()

    # The streetname and streetnumber of this "30 Aprikosenstr." street is written visa versa.
    # This for loop below checks if the streetname is written before the streetnumber and changes the order.
    for s in file2['Strasse']:
        # splitting the streetname and number
        street = s.split(' ')
        # the try and except was used because some streets did not have a number. and therefore splitting was not possible
        try:
            # checking if first character is a letter. if street starts with an Number the order has to be swapped.
            check = street[0][0].isalpha()
            if not check:
                str = street[1]
                nr = street[0]
                oldstreet = f'{nr} {str}'
                newstreet = f'{str} {nr}'
                # swapping the text from "30 Aprikosenstr." to "Aprikosenstr. 30"
                file2['Strasse'] = file2['Strasse'].replace(oldstreet, newstreet, regex=True)
        except:
            pass

    # Calculating the price per squaremeters
    file2["Preis [CHF]"] = pd.to_numeric(file2["Preis [CHF]"], errors='coerce').astype(float)
    file2["Flaeche [m2]"] = pd.to_numeric(file2["Flaeche [m2]"], errors='coerce').astype(float)
    file2["Preis/Fläche [CHF/m2]"] = (file2["Preis [CHF]"] / file2["Flaeche [m2]"]).round(2)

    # drop all locations which are not Zürich, Basel, Winterthur, Bern or Luzern
    file2.drop(file2[(file2['Ort'] != "Zürich") & (file2['Ort'] != "Basel") & (file2['Ort'] != "Bern") & (file2['Ort'] != "Winterthur") & (file2['Ort'] != "Luzern")].index, inplace=True)
    # saving the file as "flatfox_stage.csv"
    file2.to_csv('flatfox_stage.csv', index=False)


def upload():
    """
    This function connect to the mariaDB, creates a table and uploads the files to it.
    """
    try:
        # try to connect to the DB.
        conn = mariadb.connect(
            user="admin",
            password='password',
            host='localhost',
            port=3306,
            database='testdatabase' #needs to be changed.
        )

        cur = conn.cursor()
        # after having established a connection to the mariaDB, a table is created. If table exists already, it is coing to be replaced.
        # table name needs to be changed.
        cur.execute("CREATE or REPLACE TABLE testtable12345(\
                        Strasse VARCHAR(255),\
                        Postleitzahl Int(4),\
                        Ort VARCHAR(25),\
                        Anzahl_Zimmer FLOAT,\
                        Flaeche Int(10),\
                        Preis Int(10)\
                        );")
        # Finally uploading the csv file into the database
        cur.execute("LOAD DATA LOCAL INFILE 'flatfox_stage.csv' INTO TABLE testtable12345 \
                        FIELDS TERMINATED BY ',' (\
                        Strasse, Postleitzahl, Ort, Anzahl_Zimmer, Flaeche, Preis \
                        )")
        # commiting the changes.
        conn.commit()
    # if connection fails an error arises.
    except mariadb.Error as e:
        print(f"there was an error: {e}")


if __name__ == '__main__':
    # saving the time to measure the time for the entire script.
    start_time = time.time()

    # these are the cities which are used
    city = ['Zurich', 'Basel', 'Bern', 'Winterthur', 'Luzern']

    # -------------- this four functions can be commented out if not used.
    # saving html files
    saveHTML(city)
    # the actual scrapping
    main(city)
    # cleaning the data
    cleaning()
    # uploading to mariaDB
    upload()

    # printing the running time in minutes.
    print(f"{(time.time() - start_time)/60} minutes")
