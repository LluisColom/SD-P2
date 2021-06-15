# Web scraping libraries.
import requests
from bs4 import BeautifulSoup

# System libraries.
import sys
import json

# Lithops.
from lithops.multiprocessing import Pool
from lithops import Storage

# Http header.
header = { 'user-agent':'Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0' }

# Thread code.
def process_news(link):

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

    storage = Storage()
    storage.put_object(bucket='news-bucket', key='diarideTGN/'+news_format['title'].replace(" ","")+'.json', body = json.dumps(news_format))

# -------------------------------------------------------------------------------------------------------------------------------------

def get_links():

    # Auxiliar variables.
    link_to_news = []

    # We create HTML parser.
    r = requests.get('https://www.diaridetarragona.com/ajax/get_search_news.html?viewmore=%2Fajax%2Fget_search_news.html&page=1&size='+sys.argv[2]+'&search='+sys.argv[1], headers=header)
    soup = BeautifulSoup(r.text, 'html.parser')

    count = 0
    for news in soup.find_all("div", class_='news-data'):

        count +=1

        # We get the link to the news page.
        link_to_news.append("https://www.diaridetarragona.com"+news.find("a").get('href'))

    return link_to_news,count

if __name__ == '__main__':
        
    link_to_news,count = get_links()

    # Start cloud thread
    with Pool() as pool:
        result = pool.map(process_news, link_to_news)
        print(result)

    if count == 0:
        print("No hi ha resultats de la cerca.")
    else:
        print("Numero de resultados indexados:"+str(count))
