# Web scraping libraries.
import requests
from bs4 import BeautifulSoup

# System libraries.
import sys
import json

# Http header.
header = { 'user-agent':'Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0' }

def process_news(link):

    news_format = {}
    r = requests.get(link, headers=header)
    soup = BeautifulSoup(r.text, 'html.parser')
    frame = soup.find("div", class_='col-lg-6 px-0 order-2 order-lg-1')

    # Get news header.
    news_format['title'] = frame.find("div", class_='title-opening-section').text

    # Get news starter.
    news_format['starter'] = frame.find("div", class_='description').text

    # Get news date.
    frame = soup.find("div", class_='info-date')
    news_format['date'] = frame.find("span", class_='date').text

    # Get news paragraphs.
    frame = soup.find("div", id='fragment-0-wuyi')
    body = ''
    for parraph in frame.find_all("p"):
        body = body+"\n\n"+parraph.text
    news_format['body'] = body


def get_links():

    # We create HTML parser.
    r = requests.get('https://www.diaridebarcelona.cat/search?q='+sys.argv[1], headers=header)
    soup = BeautifulSoup(r.text, 'html.parser')

    # Get the number of pages in the website.
    frame = soup.find(lambda tag: tag.name == 'li' and tag.get('class') == ['first'])
    if frame is not None:
        pages = frame.find("a").get('href')
        pages = pages.split("=")[-1]
    else:
        pages = 0  

    count = 0
    for i in range(int(pages)+1):
        r = requests.get('https://www.diaridebarcelona.cat/search?q='+sys.argv[1]+'&start='+str(i), headers=header)
        soup = BeautifulSoup(r.text, 'html.parser')

        for news in soup.find_all(class_='col-sm-6 col-lg-3 mb-20px mb-lg-30px'):
            count +=1
            # We get the link to the news page.
            news = news.find(class_='h1 modul-petit')
            process_news(news.find("a").get('href'))

if __name__ == '__main__':
    get_links()
