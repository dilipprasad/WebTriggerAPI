#Create regex
import re
from urllib.parse import urljoin, urlparse
import logging
import requests
from bs4 import BeautifulSoup


class CommonFunctions:
   
    def __init__(self):
        print("CommonFunctions - Init" )
        self.regex = re.compile(
            r"(\w+://)?"                # protocol                      (optional)
            r"(\w+\.)?"                 # host                          (optional)
            r"((\w+)\.(\w+))"           # domain
            r"(\.\w+)*"                 # top-level domain              (optional, can have > 1)
            r"([\w\-\._\~/]*)*(?<!\.)"  # path, params, anchors, etc.   (optional)
            )
        self.ignoredLinks = ['https://www.bundesarchiv.de/DE/Navigation/'] #Limiting the sub url crawl with 1 more more root url
        self.blackListedUrls=  ['https://www.bundesarchiv.de/','http://www.bundesarchiv.de/']#Urls or sub urls of domain we dont want to crawl
        self.allowedDomains = ['www.bundesarchiv.de'] #Keeps us away from social media links

    def JoinUrl(self,subUrl, currUrl):
    # print("BaseURL",baseUrl)
    # print("SubUrl",subUrl)
        return urljoin(currUrl,subUrl)    
    
    def IsValidUrl_Regex(self,url):
        try: 
            return self.regex.match(url).span()[1] - self.regex.match(url).span()[0] == len(url)
        except:
            return False

     
    def download_url(self, url):
        return requests.get(url).text

    def get_linked_urls(self, url, html):
        soup = BeautifulSoup(html, 'html.parser')
        for link in soup.find_all('a'):
            path = link.get('href')
            if path and path != None and  path.startswith('#') == False: #path.startswith('/') and
                logging.info(f'get_linked_urls() - valid path: {path}')
                path = urljoin(url, path)
                yield path
            else:
                logging.info(f'get_linked_urls() - invalid path: {path}')       


     #validates if the the url to crawl is what we want,we do not wanted to wander
    def WithinCurrentDomain(self,urlDomain):
        urlDomain= urlparse(urlDomain).netloc
        for domain in self.allowedDomains:
            if urlDomain == domain:
                return True
        print("Domain is not part of allowed list: "+ str(urlDomain)    )
        return False                


    def isListPartOfIgnoreLinks(self,urlToCheck):
        resp = False
        if urlToCheck != None:
            for item in self.ignoredLinks:
                if item in urlToCheck :
                    resp =True
        print('isListPartOfIgnoreLinks()-' + str(urlToCheck)+ ". Is Ignored?: "+ str(resp))#print only if ignored
        return resp

    def IsBlackListedUrl(self,urlTovalidate):
        for urls in self.blackListedUrls:
            if urlTovalidate.removesuffix("/") == urls.removesuffix("/"):
                print("Url is blacklisted: "+ urlTovalidate)    
                return True
        return False
    
    
    def check_url_exists(chkurl: str):
        try:
            response = requests.get(chkurl)
            if response.status_code == 200:
                print('Web site exists')
                return True
            else:
                print('Web site does not exist') 
        except:
            print('Problem processing url')    
        return False

        
    def ExisitsInArray(allLinks, urlToChk):
        try:
            return allLinks.index(urlToChk) >= 0
        except: 
            return False
        return False
    