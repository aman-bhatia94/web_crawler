from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
from collections import deque
import requests
import sys
import logging
import time


queue = deque()
visited_urls = set()
error_log = "error_logs.log"
logging.basicConfig(filename = error_log, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def get_html(url):
    html_doc = 'error'
    try:
        html_doc = requests.get(url).text
    except requests.exceptions.RequestException as e:
        logger.error(e)
        html_doc = 'error'
    finally:
        return html_doc

def find_duplicate_url(url):
    if url in visited_urls:
        return True
    return False

def task(url, queue):
    print('task getting executed')
    links = []
    source = get_html(url)
    
    if source == 'error':
        #do not process this
        pass
    else:
        soup = BeautifulSoup(source,'lxml')
        for link in soup.find_all('a'):
            href_string = link.get('href')
            if href_string is not None and (href_string.startswith('http') or href_string.startswith('https')):
                #visited_urls.add(href_string)
                links.append(href_string)
                #queue.append(href_string)
        visited_urls.add(url)
        print(url)
        for link in links:
            print("\t"+link)
            if find_duplicate_url(link):
                pass
            else:
                queue.append(link)
            




def find_links(queue,visited_urls):
    executor = ThreadPoolExecutor(max_workers = 20)
    #count = 0

    while(True):
        while (len(queue) != 0):
            url = queue.popleft()
            #print(++count)
            executor.submit(task(url,queue))
        executor.shutdown(wait = True)
        #time.sleep(10)
        if(len(queue)==0):
            break



def main():
    url = sys.argv[1];
    visited_urls.add(url)
    queue.append(url)
    #for the first time we have to populate links so that each thread can work on them
    links = []
    url = queue.popleft()
    source = get_html(url)
    if source == 'error':
        #do not process initial step itself
        #error is already logged
        pass
    else:
        soup = BeautifulSoup(source, 'lxml')
        for link in soup.find_all('a'):
            href_string = link.get('href')
            if href_string is not None and (href_string.startswith('http') or href_string.startswith('https')):
                    #visited_urls.add(href_string)
                    links.append(href_string)
                    #queue.append(href_string)
        print(url)
        visited_urls.add(url)
        for link in links:
            print("\t"+link)
            if find_duplicate_url(link):
                continue
            else
                queue.append(link)
        find_links(queue,visited_urls)



if __name__ == '__main__':
    main()
