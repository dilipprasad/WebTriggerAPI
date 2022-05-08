import logging
# from tkinter.tix import Tree
from api import CommonMethods
from api import AzureQueue

# logging.basicConfig(
#     format='%(asctime)s %(levelname)s:%(message)s',
#     level=logging.INFO)

class WebCrawler:

    def __init__(self, urls): #Urls is an array with starting point of url
        self.visited_urls = []
        self.urls_to_visit = urls
        self.url_Invalid = []
        self.CommonMethods = CommonMethods.CommonFunctions()
        self.CrawlUrlQueue = AzureQueue.AZQueue("queue-crawledarchiveurls")
  
    def IsValidToAdd(self, url):
        if (url != None and url not in self.visited_urls and url not in self.urls_to_visit and
        url not in self.url_Invalid and self.CommonMethods.WithinCurrentDomain(url) and
        self.CommonMethods.isListPartOfIgnoreLinks(url) == False and
        self.CommonMethods.IsBlackListedUrl(url) == False):
            return True

    def IsInvalid(self,url):
       if ((url != None and self.CommonMethods.WithinCurrentDomain(url) == False or  
       self.CommonMethods.isListPartOfIgnoreLinks(url) == False or  
       self.CommonMethods.IsBlackListedUrl(url) == False) and 
       url not in self.url_Invalid):
        return True

    def add_url_to_visit(self, url):
        if self.IsValidToAdd(url):
            self.urls_to_visit.append(url)
            self.CrawlUrlQueue.QueueUrlFound(url)
        elif  url not in self.visited_urls:
            logging.info(f'Site visited : {url}')    
        elif self.IsInvalid(url): #not already in invalid url
            self.url_Invalid.append(url)

    def crawl(self, currUrl):
        html = self.CommonMethods.download_url(currUrl)
        for subUrl in self.CommonMethods.get_linked_urls(currUrl, html):
            logging.info(f'crawl() - Sub Url: {subUrl}')
            self.add_url_to_visit(subUrl)

    async def run(self):
        while self.urls_to_visit:
            url = self.urls_to_visit.pop(0)
            logging.info(f'Run() - Url to Crawl: {url}')
            try:
                self.crawl(url)
            except Exception as e:
                logging.exception(f'Failed to crawl: {url}, Error: {str(e)}')
            finally:
                self.visited_urls.append(url)

# if __name__ == '__main__':
#     logging.info('Initiating Main function')
#     WebCrawler(urls=['https://www.bundesarchiv.de/cocoon/barch/0000/index.html']).run()
