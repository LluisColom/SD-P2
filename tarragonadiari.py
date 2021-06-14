# Web scraping libraries.
import requests
from bs4 import BeautifulSoup

# System libraries.
import sys
import threading

# Thread code.
import tarragonadiari_thread

mutex = threading.Lock()

# Auxiliar variables.
threads = []
header = { 'user-agent':'Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0' }
news_format = {}

# We create HTML parser.
r = requests.get('https://www.diaridetarragona.com/ajax/get_search_news.html?viewmore=%2Fajax%2Fget_search_news.html&page=1&size='+sys.argv[2]+'&search='+sys.argv[1], headers=header)
soup = BeautifulSoup(r.text, 'html.parser')

count = 0
for news in soup.find_all("div", class_='news-data'):

    count +=1

    # We get the link to the news page.
    link_to_news = "https://www.diaridetarragona.com"+news.find("a").get('href')

    print(link_to_news)

    # Start thread
    new_th = threading.Thread(target=tarragonadiari_thread.process_news, args=(link_to_news,mutex,))
    threads.append(new_th)
    new_th.start()

c = 1
for t in threads:
    print("Esperant al thread ",c)
    t.join()
    c += 1

if count == 0:
    print("No hi ha resultats de la cerca.")
else:
    print("Numero de resultados indexados:"+str(count))
