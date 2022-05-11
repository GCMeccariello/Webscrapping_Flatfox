

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



def datatypes():
    data = pd.read_csv('df_after_dropping.csv')
    data = pd.DataFrame(data)

    data.drop(data[(data['Ort'] != "zuerich") & (data['Ort'] != "basel") & (data['Ort'] != "bern") & (
                data['Ort'] != "winterthur") & (data['Ort'] != "luzern")].index, inplace=True)

    List = ["Strasse", "Letter", "Ort", "Anzahl Zimmer"]
    col = [column for column in data.columns if column not in List]
    for integer in col:
        data[integer] = pd.to_numeric(data[integer], errors='coerce').astype('Int64')

    # print(data.dtypes)
    data.to_csv('clean.csv', index=False)
    return data


def analyse(data):
    """
    idee:
    1. filter nach Stadt. (loop Zh bis Lu
    1.2 filter nach postleizahl (6000, 6003 etc)
    2. Filter nach Anzahl zimmer. (loop 1.0 bis 7.0)
        Danach mean(quadratmeter) und mean(Preis)
    3. Preis / quadratmeter

    """

    data = data.sort_values('Postleitzahl')
    cities = data["Ort"].unique()
    # rooms = data['Anzahl Zimmer'].unique()
    # rooms.sort()

    for c in cities:
        plz = data[data["Ort"] == c]['Postleitzahl'].unique().dropna()
        # print(plz)

        # print(f'{c}: {plz}')


        for p in plz:
            rooms = data[(data['Ort'] == c) & (data['Postleitzahl'] == p)]['Anzahl Zimmer'].unique()
            nan_array = np.isnan(rooms)
            not_nan_array = ~ nan_array
            rooms = rooms[not_nan_array]
            rooms.sort()

            # print(rooms)

            for r in rooms:
                # print(f'city: {c}, plz: {p}, zimmer: {r}')

                abc = data[(data['Ort'] == c) & (data['Postleitzahl'] == p) & (data['Anzahl Zimmer'] == r)]
                mean_price = abc["Preis CHF"].mean()
                mean_area = abc['Flaeche m2'].mean()
                mean_per_area = mean_price / mean_area
                # abc.to_csv(f'{c}_{p}_{r}.csv', index = False)
                # print(f'appartments: {abc} in {p} and room size {r}______________________')

                print(f'city: {c}, plz: {p}, zimmer: {r}, preis: {mean_price}, area: {mean_area}, price per m2: {mean_per_area} ')

                csv_file = open(f"results.csv", "w", newline='')
                csv_writer = csv.writer(csv_file)
                csv_writer.writerow(["City", 'PLZ', "1.0", "1.5", "2.0", "2.5", '3.', '3.5', '4.', '4.5', '5.', '5.5', '6.', '6.5'])

                row = []
                row.append(c)
                row.append(p)
                row.append(r)


                csv_writer.writerow(row)


                csv_file.close()



    # mean_price = d_luzern_6003_1_0["Preis CHF"].mean()
    # print(mean_price)
    #         d_luzern_6003.to_csv(f'Lu_{plz}.csv', index=False)




if __name__ == '__main__':
        data = datatypes()
        analyse(data)
