import requests
from bs4 import BeautifulSoup
import json

header = { 'user-agent':'Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0' }

def process_news(link,mutex):

    news_format = {}

    r = requests.get(link, headers=header)

    soup = BeautifulSoup(r.text, 'html.parser')
    head = soup.find("header", class_='news-header')

    # Get news header.
    news_format['title'] = head.find("h1", class_='news-title').text

    # Get news starter.
    starter = head.find("div",class_='news-excerpt')
    if starter is not None:
        starter = starter.text
    else: starter = ''
    news_format['starter'] = starter

    # Get news date.
    news_format['date'] = head.find("time", class_='news-date').text.replace("\n","").replace("\t","").split(" ")[0]

    # Get news paragraphs.
    text = soup.find("div", class_='news-body').text
    if text is None:
        text = ''
    news_format['text'] = text

    with open('resultats.txt','a') as f:
        mutex.acquire()
        f.write("-----------------------------------------\n")
        f.write(str(news_format)+"\n")
        mutex.release()