

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

import os
import matplotlib.pyplot as plt


def datatypes():
    data = pd.read_csv('df_after_dropping.csv')
    data = pd.DataFrame(data)

    data.drop(data[(data['Ort'] != "zuerich") & (data['Ort'] != "basel") & (data['Ort'] != "bern") & (
                data['Ort'] != "winterthur") & (data['Ort'] != "luzern")].index, inplace=True)

    List = ["Strasse", "Letter", "Ort", "Anzahl Zimmer"]
    col = [column for column in data.columns if column not in List]
    for integer in col:
        data[integer] = pd.to_numeric(data[integer], errors='coerce').astype('Int64')

    data.to_csv('clean.csv', index=False)
    return data


def mean_price_plz(data):
    """
    This function calculates the mean price per square meter for the cities Zürich, Bern, Basel, Winterthur and Lucerne.
    It also takes into consideration how many rooms the appartment have and the postalcodes.
    ex: Lucerne, 6003, 1 room, mean_price/m2
        Lucerne, 6003, 1.5 room, mean_price/m2
        etc.
    So there is an iteration through the cities, postalcodes and amount of rooms.
    """
    data = data.sort_values('Postleitzahl')
    cities = data["Ort"].unique()

    df = pd.DataFrame()
    for c in cities:
        plz = data[data["Ort"] == c]['Postleitzahl'].unique().dropna()

        for p in plz:
            rooms = data[(data['Ort'] == c) & (data['Postleitzahl'] == p)]['Anzahl Zimmer'].unique()
            nan_array = np.isnan(rooms)
            not_nan_array = ~ nan_array
            rooms = rooms[not_nan_array]
            rooms.sort()

            for r in rooms:
                abc = data[(data['Ort'] == c) & (data['Postleitzahl'] == p) & (data['Anzahl Zimmer'] == r)]
                mean_price = abc["Preis CHF"].mean()
                mean_area = abc['Flaeche m2'].mean()
                mean_per_area = mean_price / mean_area

                df = df.append({'city':c , 'plz':p , 'rooms':r, 'chf/m2':mean_per_area }, ignore_index=True)
                df.to_csv('results.csv', index=False)

    print(df)

def mean_price_location(data):
    """
    This function calculates the mean price per square meter for the cities Zürich, Bern, Basel, Winterthur and Lucerne.
    It does not distinguish between the individual postalcodes, but it takes into consideration the amount of rooms.
    ex. Lucerne, 1 room, mean_price/m2
        Lucerne, 1.5 room, mean_price/2
        etc.
    """
    cities = data["Ort"].unique()

    df = pd.DataFrame()
    for c in cities:
        # plz = data[data["Ort"] == c]
        # print(plz)
        # plz.to_csv('a.csv', index=False)

        rooms = data[data['Ort'] == c]['Anzahl Zimmer'].unique()
        nan_array = np.isnan(rooms)
        not_nan_array = ~ nan_array
        rooms = rooms[not_nan_array]
        rooms.sort()
        print(rooms)

        for r in rooms:
            abc = data[(data['Ort'] == c) & (data['Anzahl Zimmer'] == r)]
            mean_price = abc["Preis CHF"].mean()
            mean_area = abc['Flaeche m2'].mean()
            mean_per_area = mean_price / mean_area

            df = df.append({'city': c, 'rooms': r, 'chf/m2': mean_per_area}, ignore_index=True)
            df.to_csv('results_ohne_plz.csv', index=False)

def pivottable():
    data = pd.read_csv('results_ohne_plz.csv')
    data = pd.DataFrame(data)

    data['chf/m2'] = data['chf/m2'].round(2)

    datapivot = data.pivot_table(values='chf/m2', index='city', columns='rooms',)
    datapivot.to_csv('result_pivot_table.csv')


def plots():
    data = pd.read_csv('results_ohne_plz.csv')
    data = pd.DataFrame(data)

    data['chf/m2'] = data['chf/m2'].round(2)
    print(data)

    cities = []
    for c in data['city']:
        cities.append(c)
    cities = list(dict.fromkeys(cities))

    for city in cities:
        name = f'd_{city}'
        name = data[data['city'] == city]
        rooms = []
        for r in name['rooms']:
            rooms.append(r)
        print(rooms)
        price = []
        for p in name['chf/m2']:
            price.append(p)
        print(price)

        x = np.arange(len(rooms))  # the label locations
        width = 0.75  # the width of the bars

        fig, ax = plt.subplots()
        rects1 = ax.bar(x, price, width, label='Price')
        # rects2 = ax.bar(x + width / 2, women_means, width, label='Women')

        # Add some text for labels, title and custom x-axis tick labels, etc.
        ax.set_ylabel('Durchschnittspreis/m2 in [CHF]')
        ax.set_xlabel('Anzahl Zimmer')
        ax.set_title(city)
        ax.set_xticks(x, rooms)
        # ax.legend()

        ax.bar_label(rects1, padding=3)
        # ax.bar_label(rects2, padding=3)
        fig.tight_layout()
        plt.savefig(f'plots/plot_{city}.png')
        plt.show()


if __name__ == '__main__':
        # data = datatypes()
        # mean_price_plz(data)
        # mean_price_location(data)
        # pivottable()
        plots()


