# Web scraping libraries.
from bs4.builder import TreeBuilder
import requests
from bs4 import BeautifulSoup

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

SEARCH_KEY = sys.argv[1]

def process_news(link):

    analyzer = SentimentIntensityAnalyzer()
    news_format = {}

    try:
        r = requests.get(link, headers=header)
        soup = BeautifulSoup(r.text, 'html.parser')
    except requests.exceptions.TooManyRedirects:
        return 0
    soup = BeautifulSoup(r.text, 'html.parser')
    
    # Put news link.
    news_format['link'] = link

    # Get news header.
    title = soup.find("div", class_='title-opening-section')
    if title is None:
        return 0         #  Case we are threatting an opinion...
    news_format['title'] = title.text.replace("\n","").replace("\t","").replace("\"","")

    # Get news starter.
    description = soup.find("div", class_='description')
    if description is None:
        return 0         # Case we are threatting an interview...
    news_format['starter'] = description.text.replace("\n","").replace("\t","").replace("\xa0"," ").replace("\"","")

    # Get news date.
    frame = soup.find("div", class_='info-date')
    date = frame.find("span", class_='date').text
    news_format['date'] = date.replace(" ","").replace("d’","/").replace("de","/").replace("gener","01/").replace("febrer","02/").replace("març","03/").replace("abril","04/").replace("maig","05/").replace("juny","06/").replace("juliol","07/").replace("agost","08/").replace("setembre","09/").replace("octubre","10/").replace("novembre","11/").replace("desembre","12/")
    # Get news paragraphs.
    frame = soup.findAll("div", class_='component-html pb-3')[3]
    body = ''
    for parraph in frame.find_all("p"):
        body = body+" "+parraph.text
    news_format['body'] = body.replace("\n","").replace("\t","").replace("\xa0"," ").replace("\"","")
    
    #Get news sentiment analysis.
    news_format['sentiment'] = analyzer.polarity_scores(mtranslate.translate(news_format['starter']+'\n'+news_format['body'],'en','auto'))['compound']

    # Get news total words number.
    word_counter = 0
    for field in news_format.values():
        word_counter += len(str(field).split(" "))
    news_format['words_number'] = word_counter

    # Store the news content to the cloud COS.
    storage = Storage()
    storage.put_object(bucket='news-bucket', key=SEARCH_KEY+'/diaridebarcelona/'+news_format['title'].replace(" ","_")+'.json', body = json.dumps(news_format))

    return 1

def get_links():

    # Auxiliar variables.
    link_to_news = []

    # We create HTML parser.
    r = requests.get('https://www.diaridebarcelona.cat/search?q='+SEARCH_KEY, headers=header)
    soup = BeautifulSoup(r.text, 'html.parser')

    # Get the number of pages in the website.
    frame = soup.find(lambda tag: tag.name == 'li' and tag.get('class') == ['first'])
    if frame is not None:
        pages = frame.find("a").get('href')
        pages = pages.split("=")[-1]
    else:
        pages = 0  

    # Get the links to the news.
    for i in range(int(pages)+1):
        r = requests.get('https://www.diaridebarcelona.cat/search?q='+SEARCH_KEY+'&start='+str(i), headers=header)
        soup = BeautifulSoup(r.text, 'html.parser')

        for news in soup.find_all(class_='col-sm-6 col-lg-3 mb-20px mb-lg-30px'):
            # We get the link to the news page.
            news = news.find(class_='h1 modul-petit')
            link_to_news.append(news.find("a").get('href'))
    
    return link_to_news

if __name__ == '__main__':

    link_to_news = get_links()

    # Start cloud multiprocessing.
    with Pool() as pool:
        result = pool.map(process_news, link_to_news)
    count = sum(result)

    if count == 0:
        print("No hi ha resultats de la cerca.")
    else:
        print("Numero de resultados indexados:"+str(count))