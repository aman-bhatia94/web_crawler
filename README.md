# Web_crawler
A multi threaded web crawler written in Python that crawls urls on a web page and prints the root url, along with those present on the web page.

# Working
- main is the starting point of the application.
- The crawler maintains a visited_url set to keep track of the urls visited
- All the unvisited urls are pushed in the unvisited queue
- Thread pool manages the worker threads that can be used by the application(currently set to 30)
- While there are more links to process the application polls a url from the unvisited queue and submits a task to process this url using the worker thread

# Build
- go to the directory where the web_crawler.py script is present
- open the terminal and type the following command to run the application
- python3 webcrawler.py "<url_to_parse>"
- you should be able to see the results printed in the terminal

# Requirements
- The application uses the following libraries and 
  - Beautiful Soup [source](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) 
  - Requests [source](https://requests.readthedocs.io/en/master/)
  - lxml [source](https://pypi.org/project/lxml/)

# Testing
- Tested the crawler on a few urls
- The following shows screenshots of the application running with python3 webcrawler.py "https://www.rescale.com"
- ![alt text](https://github.com/aman-bhatia94/web_crawler_screenshots/blob/master/scrrenshots/screenshot1.png)
- ![alt text](https://github.com/aman-bhatia94/web_crawler_screenshots/blob/master/scrrenshots/screenshot2.png)
- ![alt text](https://github.com/aman-bhatia94/web_crawler_screenshots/blob/master/scrrenshots/screenshot3.png)
- ![alt text](https://github.com/aman-bhatia94/web_crawler_screenshots/blob/master/scrrenshots/screenshot4.png)
- ![alt text](https://github.com/aman-bhatia94/web_crawler_screenshots/blob/master/scrrenshots/screenshot5.png)

