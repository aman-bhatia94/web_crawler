""" 
A multithreaded web crawler which fetches URLs and outputs crawl results to standard output and logs the errors into error_logs.log 
Author: Aman Bhatia
Date: 03/16/2020
""" 

from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
from collections import deque
from threading import Lock
import requests
import sys
import logging
import time

#variables that will be used throughout the application
visited_url_lock = Lock()
error_log = "error_logs.log"
logging.basicConfig(filename = error_log, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


#fetch the html document as text from the url and return
#if an error is encountered, log it
def get_html(url):
    html_doc = 'error'
    try:
        html_doc = requests.get(url).text
    except requests.exceptions.RequestException as e:
        logger.error(e)
        html_doc = 'error'
    finally:
        return html_doc

 
#Add the url to the visited_urls set
#synchronization ensures thread safety and consistency
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

#return true if the url is already visited
#return false otherwise
def find_duplicate_url(url,visited_urls):

    search_string = url
    
    if url.startswith('https://'):
        search_string = url[8:]
    elif url.startswith('http://'):
        search_string = url[7:]

    if search_string.endswith('/'):
        search_string = search_string[ :-1]

    if search_string in visited_urls:
        return True
    return False

#Each task is a unit of execution 
#parse the document to find urls
#print the url and the urls contained within it
#add the url to visited_urls set
#add the contained urls to an unvisited queue(for later polling), if they are not visited
#if the url is already visited, do not process it
def task(url, unvisited_url_queue, visited_urls):

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
            for link in links:
                print("\t"+link)
                visited_url_lock.acquire()
                if find_duplicate_url(link,visited_urls):
                    visited_url_lock.release()
                    continue
                else:
                    visited_url_lock.release()
                    unvisited_url_queue.append(link)
            
#poll a url to visit from the queue
#submit a task to the executor to process the polled url
def find_links(unvisited_url_queue,visited_urls):
    executor = ThreadPoolExecutor(max_workers = 30)

    while(True):
        while (len(unvisited_url_queue) != 0):
            url = unvisited_url_queue.popleft()
            executor.submit(task(url,unvisited_url_queue, visited_urls))
        executor.shutdown(wait = True)
        if(len(unvisited_url_queue)==0):
            break


#starting point of the web crawler application
#parses the root url and puts the url's contained
#in the root, inside queue for later polling
def main():

    #I haven't used any synchronization for my unvisited_url_queue since the documentation says that appends and pops are thread safe in dequeues
    #source https://docs.python.org/2/library/collections.html#collections.deque
    unvisited_url_queue = deque()
    visited_urls = set()
    url = sys.argv[1];
    add_to_visited_urls(url,visited_urls)
    unvisited_url_queue.append(url)

    #for the first time we have to populate links so that each thread can work on them
    links = []
    url = unvisited_url_queue.popleft()
    source = get_html(url)
    if source == 'error':
        pass
    else:
        soup = BeautifulSoup(source, 'lxml')
        for link in soup.find_all('a'):
            href_string = link.get('href')
            if href_string is not None and (href_string.startswith('http') or href_string.startswith('https')):
                links.append(href_string)
                    
        print(url)
        add_to_visited_urls(url,visited_urls)
        for link in links:
            print("\t"+link)
            visited_url_lock.acquire()
            if find_duplicate_url(link,visited_urls):
                visited_url_lock.release()
                continue
            else:
                visited_url_lock.release()
                unvisited_url_queue.append(link)
        find_links(unvisited_url_queue,visited_urls)


#start main as the first function that runs
if __name__ == '__main__':
    main()
