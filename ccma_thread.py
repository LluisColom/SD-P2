import requests
from bs4 import BeautifulSoup
import json
import sys

header = { 'user-agent':'Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0' }

def process_news(link,mutex):

    news_format = {}

    r = requests.get(link, headers=header)

    soup = BeautifulSoup(r.text, 'html.parser')
    frame = soup.find("div", class_='span8')
    
    # Get news header.
    news_format['title'] = frame.find("h1", class_='titol').text

    # Get news starter.
    starter = frame.find("h2", class_='entradeta')
    if starter is not None:
        starter = starter.text
    else: starter = ''
    news_format['starter'] = starter

    # Get news date.
    news_format['date'] = frame.find("time", class_='data').text.split(" ")[0]

    # Get news paragraphs.
    frame = frame.find("div", class_='R-itemNotiCos')
    body = ''
    for parraph in frame.find_all("p"):
        body = body+"\n\n"+parraph.text

    news_format['body'] = body

    with open('resultats.txt','a') as f:
        mutex.acquire()
        f.write("-----------------------------------------\n")
        f.write(str(news_format)+"\n")
        mutex.release()

