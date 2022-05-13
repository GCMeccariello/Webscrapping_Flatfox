import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import time
import csv
import os
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from urllib.request import Request, urlopen

from selenium import webdriver
from selenium.webdriver.common.by import By


def datatypes():
    """
    Changing the datatype of some columns. The datatype for prices, area etc has to be a float.
    Saving the new datatype as "clean.csv"
    """
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


def mean_price_room_plz(data):
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

            # plot_auslander(p)

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


def plot_price_room():
    """
    This function creates for every city a plot which shows the mean price per square meter for
    different amount of rooms in an appartment
    """
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


def plot_auslander_staedte(data):
    """
    This function creates one plot which shows the ausländer in percentege for every city.
    """

    anteile = []
    cities_for_plots = []

    data = data.drop_duplicates(subset=['Postleitzahl'])
    data.to_csv('why.csv')

    # plz = data[data['Ort'] == 'luzern']['Postleitzahl'].unique().dropna()
    cities = data["Ort"].unique()

    for city in cities:
        schweiz = data[data['Ort'] == city]['Schweiz'].sum()
        ausland = data[data['Ort'] == city]['Ausland'].sum()
        anteil = (ausland * 100 / (ausland + schweiz)).round(2)
        anteile.append(anteil)
        cities_for_plots.append(city)

    x = np.arange(len(cities))  # the label locations
    width = 0.75  # the width of the bars

    fig, ax = plt.subplots()
    rects1 = ax.bar(x, anteile, width, label='Price')
    # rects2 = ax.bar(x + width / 2, women_means, width, label='Women')

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('Ausländeranteil in [%]')
    ax.set_xlabel('Städte')
    ax.set_title('Ausländeranteil in den grössten Städten')
    ax.set_xticks(x, cities)
    # ax.legend()

    ax.bar_label(rects1, padding=3)
    # ax.bar_label(rects2, padding=3)
    fig.tight_layout()
    plt.savefig(f'plots/plot_auslaender.png')
    plt.show()


def plot_auslander_plz(data):
    """
    This function creates for every city a plot which shows the amount of ausländer in percantage for every postalcode.
    """

    data = data.drop_duplicates(subset=['Postleitzahl']).sort_values(by=['Postleitzahl'])

    # plz = data[data['Ort'] == 'luzern']['Postleitzahl'].unique().dropna()
    cities = data["Ort"].unique()

    for city in cities:
        # schweiz = data[data['Ort'] == city]['Schweiz'].sum()
        # ausland = data[data['Ort'] == city]['Ausland'].sum()
        # anteil = (ausland * 100 / (ausland + schweiz)).round(2)
        # anteile.append(anteil)
        # cities_for_plots.append(city)

        anteile = []
        plz_used = []
        plz = data[data["Ort"] == city]['Postleitzahl'].dropna()
        for p in plz:
            # print(f' this is the plz {p}')
            # postleitzahl = data[data['Postleitzahl'] == p]['Schweiz'].sum()
            schweiz = data[data['Postleitzahl'] == p]['Schweiz'].dropna().sum()

            # print(schweiz)
            ausland = data[data['Postleitzahl'] == p]['Ausland'].dropna().sum()

            if (schweiz != 0) or (ausland != 0):
                anteil = np.round((ausland * 100 / (ausland + schweiz)), 2)
                anteile.append(anteil)
                plz_used.append(p)
            else:
                pass


        x = np.arange(len(plz_used)) # the label locations
        width = 0.75  # the width of the bars

        fig, ax = plt.subplots()
        rects1 = ax.bar(x, anteile, width, label='Price')
        # rects2 = ax.bar(x + width / 2, women_means, width, label='Women')

        # Add some text for labels, title and custom x-axis tick labels, etc.
        ax.set_ylabel('Ausländeranteil in [%]')
        ax.set_xlabel('Postleitzahlen')
        ax.set_title(f'Ausländeranteil in {city.capitalize()}')
        if city == 'zuerich':
            ax.set_xticks(x, plz_used, rotation=90)
            ax.bar_label(rects1, padding=3, rotation=90)
            plt.ylim([0, 50])
        else:
            ax.set_xticks(x, plz_used)
            ax.bar_label(rects1, padding=3)

        # ax.legend()

        # ax.bar_label(rects2, padding=3)
        fig.tight_layout()

        plt.savefig(f'plots/plot_auslaender_{city}.png')
        plt.show()

def plot(d):
    data = pd.read_csv('results.csv')
    data = pd.DataFrame(data)

    cities = data["city"].unique()

    for c in cities:
        plzs = []
        meanprice = []

        plz = data[data["city"] == c]['plz'].dropna().unique()

        anteile = []
        plz_used = []

        for p in plz:
            durchschnittspreis = np.round(data[data['plz'] == p]['chf/m2'].dropna().mean(), 2)
            plzs.append(p)
            meanprice.append(durchschnittspreis)

            schweiz = d[d['Postleitzahl'] == p]['Schweiz'].dropna().sum()
            ausland = d[d['Postleitzahl'] == p]['Ausland'].dropna().sum()

            if (schweiz != 0) or (ausland != 0):
                anteil = np.round((ausland * 100 / (ausland + schweiz)), 2)
                anteile.append(anteil)
                plz_used.append(int(p))
            else:
                pass

        # print(meanprice)
        # plt.plot(meanprice)
        # plt.show()


        x = np.arange(len(plz_used))  # the label locations
        width = 0.75  # the width of the bars

        fig, ax = plt.subplots()
        rects1 = ax.bar(x, anteile, width, label='Price')
        # rects2 = ax.bar(x + width / 2, women_means, width, label='Women')

        # Add some text for labels, title and custom x-axis tick labels, etc.
        ax.set_ylabel('Ausländeranteil in [%]')
        ax.set_xlabel('Postleitzahlen')
        ax.set_title(f'Ausländeranteil in {c.capitalize()}')
        if c == 'zuerich':
            ax.set_xticks(x, plz_used, rotation=90)
            ax.bar_label(rects1, padding=3, rotation=90)
            plt.ylim([0, 50])
        else:
            ax.set_xticks(x, plz_used)
            ax.bar_label(rects1, padding=3)

        ax2 = ax.twinx()
        ax2.set_ylabel('Durchschnittspreis pro Fläche [CHF/m2]')
        # ax.legend()

        # ax.bar_label(rects2, padding=3)
        fig.tight_layout()
        plt.plot(meanprice, marker='o', color='red')
        plt.savefig(f'plots/plot_bar_line_{c}.png')
        plt.show()



        #
        # x = np.arange(len(plz_used))  # the label locations
        # width = 0.75  # the width of the bars
        #
        # fig, ax = plt.subplots()
        # rects1 = ax.bar(x, anteile, width, label='Price')
        # # rects2 = ax.bar(x + width / 2, women_means, width, label='Women')
        #
        # # Add some text for labels, title and custom x-axis tick labels, etc.
        # ax.set_ylabel('Ausländeranteil in [%]')
        # ax.set_xlabel('Postleitzahlen')
        # ax.set_title(f'Ausländeranteil in {c.capitalize()}')
        # if c == 'zuerich':
        #     ax.set_xticks(x, plz_used, rotation=90)
        #     ax.bar_label(rects1, padding=3, rotation=90)
        #     plt.ylim([0, 50])
        # else:
        #     ax.set_xticks(x, plz_used)
        #     ax.bar_label(rects1, padding=3)
        #
        # # ax.legend()
        #
        # # ax.bar_label(rects2, padding=3)
        # fig.tight_layout()
        #
        # plt.savefig(f'plots/plot_bar_line_{c}.png')
        # plt.show()
        #










    # plz = city[city['Postleitzahl' == 3004.0]]
    # print(city)
    # print(plzs)
    # print(meanprice)



if __name__ == '__main__':
        data = datatypes()
        # mean_price_room_plz(data)
        # mean_price_location(data)
        # pivottable()
        # plot_price_room()

        # plot_auslander_staedte(data)
        # plot_auslander_plz(data)
        plot(data)
