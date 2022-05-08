
#Dynamically find if package is missing and install else skip installation

import json
import pytz
import logging
from api import AzureQueue

from CommonMethods import CommonFunctions

class WebExtractor:
    def __init__(self):
          # it will get the time zone of the specified location
        self.IST = pytz.timezone('Asia/Kolkata')
        self.queue_crawledarchive = AzureQueue.AZQueue("queue-crawledarchiveurls")#for fetching links
        self.queue_extracteddetails = AzureQueue.AZQueue("queue-extractedpagedetails")#for queuein link with extracated text json 

        self.CommonFunctions= CommonFunctions()
        self.allLinks = []
        self.queueMessages = [] #queue messages
        self.queueUrlCount = 0

    
    async def LoopThroughUrls(self):
        try:
            queueUrlCount = self.queue_crawledarchive.GetMessageCount()
            logging.info("Message count: " + str(queueUrlCount))
        except Exception as e: 
            print("Problem fetching count from queue. Message : "+ str(e)) 
            return None   

        try:   
            queueMessages = self.queue_crawledarchive.GetQueueMessages()
            while queueMessages != None and len(queueMessages) > 0:
                for urlMsg in queueMessages:
                    if urlMsg != None:
                        url = urlMsg.content 
                        if self.CommonFunctions.ExisitsInArray(self.allLinks,url) == False: #Check if the Url is not already added to the list
                            self.allLinks.append(url)
                            #Queue new data
                            txt = self.GetSoupContent(url)
                            if txt != None:
                                txt= txt.strip()
                                jsonData = {"Url":url, "TextInfo":txt}
                                json_dump = json.dumps(jsonData)#Serialize data
                                print(json_dump)
                                self.queue_extracteddetails.QueueMessage(json_dump)
            queueMessages =  self.queue_crawledarchive.GetQueueMessages()    
        except Exception as e: 
            print("Problem processing urls. Message : "+ str(e))
            return None

