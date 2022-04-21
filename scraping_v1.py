
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from urllib.request import Request, urlopen

# headers = {
#     'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.80 Safari/537.36'
# }
#
#
# html_text = requests.get('https://www.newhome.ch/de/mieten/suchen/haus-wohnung/region-luzern/liste?propertyType=100&offerType=2&location=3;4048&skipCount=0', headers=headers).text
# soup = BeautifulSoup(html_text, 'lxml')
#
# print(soup)

# with open('newhome.html', 'r') as html_file:
#     content = html_file.read()
#     soup = BeautifulSoup(content, 'lxml')
#     print(soup)
#
# li = soup.find('li', class_="objects-list__item ng-star-inserted").find('a', class_='card__link object-card__link').get('href')
# print(li)
# # soup = BeautifulSoup(html_text, 'html.parser')
#
# # print(soup)
#


url = 'https://www.newhome.ch/de/mieten/suchen/haus-wohnung/region-luzern/liste?propertyType=100&offerType=2&location=3;4048&skipCount=0'
# url = 'https://www.fool.ca/recent-headlines/'
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
req = requests.get(url, headers=headers)
# req = Request(url, verify=False, headers={'User-Agent': 'Mozilla/5.0'})
# webpage = urlopen(req).read()
print(req)


