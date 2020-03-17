from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
from collections import deque
from threading import Lock
import requests
import sys
import logging
import time


visited_url_lock = Lock()
queue_add_lock = Lock()
queue_poll_lock = Lock()
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

def add_to_visited_urls(url,visited_urls):
    add_url = url
    if url.startswith('https://'):
        add_url = url[8:]
    elif url.startswith('http://'):
        add_url = url[7:]

    if add_url.endswith('/'):
        add_url = add_url[ :-1]

    visited_url_lock.acquire()
    visited_urls.add(add_url)
    visited_url_lock.release()


def find_duplicate_url(url,visited_urls):

    search_string = url
    
    if url.startswith('https://'):
        search_string = url[8:]
    elif url.startswith('http://'):
        search_string = url[7:]

    if search_string.endswith('/'):
        search_string = search_string[ :-1]

    #visited_url_lock.acquire()
    if search_string in visited_urls:
        return True
    return False
    #visited_url_lock.release()

def task(url, queue, visited_urls):

    visited_url_lock.acquire()
    if find_duplicate_url(url,visited_urls):
        visited_url_lock.release()
        pass
    else:
        visited_url_lock.release()
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
                    links.append(href_string)
            print(url)
            add_to_visited_urls(url,visited_urls)
            #visited_urls.add(url)
            for link in links:
                print("\t"+link)
                visited_url_lock.acquire()
                if find_duplicate_url(link,visited_urls):
                    #print("alread visited"+link)
                    visited_url_lock.release()
                    continue
                else:
                    visited_url_lock.release()
                    #queue.append(link)
                    add_to_queue(link,queue)
            

def add_to_queue(url,queue):
    queue_add_lock.acquire()
    queue.append(url)
    queue_add_lock.release()



def find_links(queue,visited_urls):
    executor = ThreadPoolExecutor(max_workers = 20)

    while(True):
        while (len(queue) != 0):
            queue_poll_lock.acquire()
            url = queue.popleft()
            queue_poll_lock.release()
            executor.submit(task(url,queue, visited_urls))
        executor.shutdown(wait = True)
        if(len(queue)==0):
            break


def main():
    queue = deque()
    visited_urls = set()
    url = sys.argv[1];
    add_to_visited_urls(url,visited_urls)
    #visited_urls.add(url)
    #print(visited_urls)
    #queue.append(url)
    add_to_queue(url,queue)
    #for the first time we have to populate links so that each thread can work on them
    links = []
    #queue_poll_lock.acquire()
    url = queue.popleft()
    #queue_poll_lock.release()
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
                links.append(href_string)
                    
        print(url)
        #visited_urls.add(url)
        add_to_visited_urls(url,visited_urls)
        for link in links:
            print("\t"+link)
            visited_url_lock.acquire()
            if find_duplicate_url(link,visited_urls):
                visited_url_lock.release()
                continue
            else:
                #queue.append(link)
                visited_url_lock.release()
                add_to_queue(link,queue)
        find_links(queue,visited_urls)



if __name__ == '__main__':
    main()
