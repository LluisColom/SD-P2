# Web scraping libraries.
import requests
from bs4 import BeautifulSoup
from requests.sessions import Request

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

SEARCH_KEY = ''

def process_news(link):

    analyzer = SentimentIntensityAnalyzer() 
    news_format = {}
    try:
        r = requests.get(link, headers=header)
    except requests.exceptions.TooManyRedirects:
        return 0

    soup = BeautifulSoup(r.text, 'html.parser')
    frame = soup.find("div", class_='span8')
    
    # Put news link.
    news_format['link'] = link

    # Get news header.
    news_format['title'] = frame.find("h1", class_='titol').text

    # Get news starter.
    starter = frame.find("h2", class_='entradeta')
    if starter is not None:
        starter = starter.text
    else: starter = ''
    news_format['starter'] = starter.replace("\n","").replace("\t","")

    # Get news date.
    news_format['date'] = frame.find("time", class_='data').text.split(" ")[0]

    # Get news paragraphs.
    frame = frame.find("div", class_='R-itemNotiCos')
    body = ''
    for parraph in frame.find_all("p"):
        body = body+" "+parraph.text
    news_format['body'] = body.replace("\n","").replace("\t","")

    #Get news sentiment analysis.
    news_format['sentiment'] = analyzer.polarity_scores(mtranslate.translate(news_format['starter']+'\n'+news_format['body'],'en','auto'))['compound']

    # Get news total words number.
    word_counter = 0
    for field in news_format.values():
        word_counter += len(str(field).split(" "))
    news_format['words_number'] = word_counter

    # Store the news content to the cloud COS.
    storage = Storage()
    storage.put_object(bucket='news-bucket', key=SEARCH_KEY+'/ccma/'+news_format['title'].replace(" ","_")+'.json', body = json.dumps(news_format))

    return 1
# -------------------------------------------------------------------------------------------------------------------------------------

def get_links():

    # Auxiliar variables.
    link_to_news = []

    # We create HTML parser.
    r = requests.get('https://www.ccma.cat/cercador/?text='+SEARCH_KEY+'&profile=noticies&pagina=1', headers=header)
    soup = BeautifulSoup(r.text, 'html.parser')

    # Get the number of pages in the website.
    pages = soup.find(class_='numeracio')
    if pages is None:
        pages = 0
    else:
        pages = pages.text.split(" ")[3]

    # Get the links to the news.
    for i in range(int(pages)+1):
        r = requests.get('https://www.ccma.cat/cercador/?text='+SEARCH_KEY+'&profile=noticies&pagina='+str(i), headers=header)
        soup = BeautifulSoup(r.text, 'html.parser')

        for news in soup.find_all("li", class_='F-llistat-item'):
            # We get the link to the news page.
            link_to_news.append("https://www.ccma.cat"+news.find("a").get('href'))
    
    return link_to_news


def query(topic):
    global SEARCH_KEY
    SEARCH_KEY = topic
    link_to_news = get_links()

    # Start cloud multiprocessing.
    with Pool() as pool:
        result = pool.map(process_news, link_to_news)
    
    count = result.sum()

    if count == 0:
        return "CCMA: no results found."
    else:
        return str(count)+" results found."

if __name__ == '__main__':

    SEARCH_KEY = sys.argv[1]

    link_to_news = get_links()

    # Start cloud multiprocessing.
    with Pool() as pool:
        result = pool.map(process_news, link_to_news)

    count = sum(result)
    if count == 0:
        print ("CCMA: no results found.")
    else:
        print (str(count)+" results found.")