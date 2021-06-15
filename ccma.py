# Web scraping libraries.
import requests
from bs4 import BeautifulSoup

<<<<<<< HEAD
#Sentiment Analisys libraries.
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import mtranslate

# System libraries.
import sys
import json

# Lithops.
from lithops.multiprocessing import Pool
from lithops import Storage

# Http header.
header = { 'user-agent':'Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0' }

def process_news(link,topic):

    analyzer = SentimentIntensityAnalyzer() 
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

    #Get news sentiment analysis.
    news_format['sentiment'] = analyzer.polarity_scores(mtranslate.translate(news_format['starter']+'\n'+news_format['body'],'en','auto'))['compound']

    storage = Storage()
    storage.put_object(bucket='news-bucket', key=sys.argv[1]+'/ccma/'+news_format['title'].replace(" ","")+'.json', body = json.dumps(news_format))

# -------------------------------------------------------------------------------------------------------------------------------------

def get_links():

    # Auxiliar variables.
    link_to_news = []

    # We create HTML parser.
    r = requests.get('https://www.ccma.cat/cercador/?text='+sys.argv[1]+'&profile=noticies&pagina=1', headers=header)
    soup = BeautifulSoup(r.text, 'html.parser')

    # Get the number of pages in the website.
    pages = soup.find(class_='numeracio')
    if pages is None:
        pages = 0
    else:
        pages = pages.text.split(" ")[3]

    count = 0
    for i in range(int(pages)+1):
        r = requests.get('https://www.ccma.cat/cercador/?text='+sys.argv[1]+'&profile=noticies&pagina='+str(i), headers=header)
        soup = BeautifulSoup(r.text, 'html.parser')

        for news in soup.find_all("li", class_='F-llistat-item'):
            count +=1
            # We get the link to the news page.
            link_to_news.append("https://www.ccma.cat"+news.find("a").get('href'))
    
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
=======
# System libraries.
import sys
import threading

import ccma_thread

# Auxiliar variables.
mutex = threading.Lock()
threads = []
header = { 'user-agent':'Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0' }
news_format = {}

# We create HTML parser.
r = requests.get('https://www.ccma.cat/cercador/?text='+sys.argv[1]+'&profile=noticies&pagina=1', headers=header)
soup = BeautifulSoup(r.text, 'html.parser')

# Get the number of pages in the website.
pages = soup.find(class_='numeracio')
if pages is None:
    pages = 0
else:
    pages = pages.text.split(" ")[3]

count = 0
for i in range(int(pages)+1):
    r = requests.get('https://www.ccma.cat/cercador/?text='+sys.argv[1]+'&profile=noticies&pagina='+str(i), headers=header)
    soup = BeautifulSoup(r.text, 'html.parser')

    for news in soup.find_all("li", class_='F-llistat-item'):
        count +=1
        # We get the link to the news page.
        link_to_news = "https://www.ccma.cat"+news.find("a").get('href')

        print(link_to_news)

        # Start thread
        new_th = threading.Thread(target=ccma_thread.process_news, args=(link_to_news,mutex,))
        threads.append(new_th)
        new_th.start()

# c = 1
# for t in threads:
#     print("Esperant al thread ",c)
#     t.join()
#     c += 1

if count == 0:
    print("No hi ha resultats de la cerca.")
else:
    print("Numero de resultados indexados:"+str(count))
>>>>>>> 9a2b8f6817c0b655dcb9f31dfb1dcbcb5967b3c4
