# Web scraping libraries.
import requests
from bs4 import BeautifulSoup

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