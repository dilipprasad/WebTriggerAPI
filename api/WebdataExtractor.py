
#Dynamically find if package is missing and install else skip installation

import json
import pytz
import logging
from api import AzureQueue
from api import CommonMethods

class WebExtractor:
    def __init__(self):
          # it will get the time zone of the specified location
        self.IST = pytz.timezone('Asia/Kolkata')
        self.queue_crawledarchive = AzureQueue.AZQueue("queue-crawledarchiveurls")#for fetching links
        self.queue_extracteddetails = AzureQueue.AZQueue("queue-extractedpagedetails")#for queuein link with extracated text json 

        self.CommonFunctions= CommonMethods.CommonFunctions()
        self.allLinks = []
        self.queueMessages = [] #queue messages
        self.queueUrlCount = 0

    
    async def LoopThroughUrls(self):
        try:
            queueUrlCount =  self.queue_crawledarchive.GetMessageCount()
            logging.info("Message count: " + str(queueUrlCount))
        except Exception as e: 
            print("Problem fetching count from queue. Message : "+ str(e)) 
            return None   

        try:   
            queueMessages = self.queue_crawledarchive.GetQueueMessages()
            currIterationAllowed = queueMessages is not None and len(queueMessages) > 1
            if currIterationAllowed == True:
                while currIterationAllowed:
                    for urlMsg in queueMessages:
                        if urlMsg != None and urlMsg != '':
                            url = urlMsg.content 
                            self.queue_crawledarchive.DeleteQueueMessages(urlMsg.id,urlMsg.pop_receipt)
                            if self.CommonFunctions.ExisitsInArray(self.allLinks,url) == False: #Check if the Url is not already added to the list
                                self.allLinks.append(url)
                                try:
                                    #Queue new data
                                    txt = self.CommonFunctions.GetSoupContent(url)
                                    if txt != None:
                                        txt= txt.strip()
                                        jsonData = {"Url":url, "TextInfo":txt}
                                        json_dump = json.dumps(jsonData)#Serialize data
                                        print(json_dump)
                                        self.queue_extracteddetails.QueueMessage(json_dump)
                                except:
                                    print("Problem sending to queue. Message : "+ str(e))                    
                    queueMessages =  self.queue_crawledarchive.GetQueueMessages()    
                    currIterationAllowed = queueMessages is not None and len(queueMessages) > 1

        # except: 
        #     print("Problem processing urls. Message : ")
        except Exception as e: 
            print("Problem processing urls. Message : "+ str(e))
            return None
        finally:
            print('Web data extraction complete')
        # except Exception as e: 
        #     print("Problem processing urls. Message : "+ str(e))
        #     return None

