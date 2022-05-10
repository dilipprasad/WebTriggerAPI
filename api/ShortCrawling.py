#Create regex
import re
from api import CommonMethods
from urllib.parse import urlparse
from urllib.parse import urljoin

class ShortCrawl():

    def __init__(self): #Urls is an array with starting point of url
        self.visited_urls = []
        self.CommonMethods = CommonMethods.CommonFunctions()
        self.regex = re.compile(
            r"(\w+://)?"                # protocol                      (optional)
            r"(\w+\.)?"                 # host                          (optional)
            r"((\w+)\.(\w+))"           # domain
            r"(\.\w+)*"                 # top-level domain              (optional, can have > 1)
            r"([\w\-\._\~/]*)*(?<!\.)"  # path, params, anchors, etc.   (optional)
        )




     #Short Crawls
    #Find all possible href in any given link
    def GetAllHrefFromUrl(self,url):
        soupLinks = []
        soup = self.CommonMethods.getSoupObj(url)
        if soup != None:
            for link in soup.findAll('a'):
                if link != None and link.get("href") != None:
                    soupLinks.append(link.get("href"))
                    print("------------"+str(link.get('href'))+"-------------------------")
            
        return soupLinks

        
    def IsValidUrl_Regex(self,url):
        try: 
            return self.regex.match(url).span()[1] - self.regex.match(url).span()[0] == len(url)
        except:
            return False
    


    def IsAbsoluteUrl(self,url):
        return bool(urlparse(url).netloc)

        
    def JoinUrl(self,subUrl, baseUrl = "https://www.bundesarchiv.de//cocoon/barch/0000/k/index.html"):
        # print("BaseURL",baseUrl)
        # print("SubUrl",subUrl)
        return urljoin(baseUrl,subUrl)


    def GetValidURL(self,urlval,ParentUrlVal):
        # print("GetValidURL",urlval)
        linkToAdd= None
        if urlval != None and self.IsAbsoluteUrl(urlval) == False and urlval[0:1] != "#":    
            # print("GetValidURL-sub url parent",urlval)
            #linkToAdd = urlval
            linkToAdd= None
            if self.IsAbsoluteUrl(urlval) == False: #If sublink
                # print("GetValidURL-sub url IsAbsoluteUrl() -false",urlval)
                linkToAdd = self.JoinUrl(urlval,ParentUrlVal) #Join with base url and get full path 
            else:
                # print("GetValidURL-sub url IsAbsoluteUrl() -true",urlval)
                linkToAdd = urlval       
        elif self.IsValidUrl_Regex(urlval) and urlval != None: #Only if the link is valid
                # print("GetValidURL-sub url IsAbsoluteUrl() -valid link",urlval)
                linkToAdd = urlval
        else: 
            # print("GetValidURL-sub url IsAbsoluteUrl() -Not valid link",urlval)
            linkToAdd= None
            #print(ctr, "Not valid based on regex",nextLink) - Dont do anything, Ignore invalid Urls

        return linkToAdd     
        
    #Get the List of Processed Relative Urls
    def GetFullUrl(self,partialUrllist,currentUrl):
        #completeUrl = []
        completeUrl = {"www.google.com"}
        if(partialUrllist != None):
            for partialUrl in partialUrllist:
                if(partialUrl != None):
                    fullUrl = self.GetValidURL(partialUrl,currentUrl)
                    if fullUrl != None:
                        #completeUrl.append(fullUrl)
                        completeUrl.add(fullUrl)
        return completeUrl

   
