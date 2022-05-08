from typing import Optional
from unittest import result
from fastapi import FastAPI
# from pydantic import BaseModel
# import ml_model as model
import pytz
from datetime import datetime
from api.NLPProcessor import NLPProcesor
from api.Search import Search
from api.WebCrawler import WebCrawler
from api.WebdataExtractor import WebExtractor
from api.AzureQueue import AZQueue
import uvicorn

# Declaring User signup data structure
# class UserSignup(BaseModel):
#     name: str
#     email: str
#     phoneNum: str
#     ipAddress: str
#     spamScore: Optional[int] = None
#     spamStatus: Optional[bool] = None


# Initializing FastAPI
app = FastAPI()

if __name__ == '__main__':
   print('Initiating Main function')
   uvicorn.run(app, host="0.0.0.0", port=90)


# it will get the time zone of the specified location
IST = pytz.timezone('Asia/Kolkata')

# Post method to fetch spam status and return in post call
# @app.post("/spamScore")
# async def fetch_spam_score(user_signup: UserSignup):
#    spamStatus= model.get_spam_status(user_signup)
#    return spamStatus


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/Ping")
async def ping_api_status():
   return "Hello from api "+ datetime.now(IST).strftime("%d/%m/%Y %H:%M:%S")


@app.get("/InvokeCrawling")
async def invoke_web_crawling():
#    return crawl_limited_links()
    results = await WebCrawler(['https://www.bundesarchiv.de/cocoon/barch/0000/index.html']).run()
    return result


@app.get("/InvokeWebExtraction")
async def invoke_web_crawling():
#    return crawl_limited_links()
    results = await WebExtractor().LoopThroughUrls()
    return result


@app.get("/GetQueueCount")
async def invoke_web_crawling():
#    return crawl_limited_links()
    queue_crawledarchive =  AZQueue("queue-crawledarchiveurls")#for fetching links
    queue_extracteddetails = AZQueue("queue-extractedpagedetails")#for queuein link with extracated text json 

    msg = f"Queue name- queue-crawledarchiveurls, Message Count: { await queue_crawledarchive.GetMessageCount()} <br/>"
    msg += f"Queue name- queue-extractedpagedetails, Message Count: {await queue_extracteddetails.GetMessageCount()} <br/>"
     
    return msg




@app.get("/GetAllQueueMessage")
async def invoke_getall_queuemsg(queueName: str):
#    return crawl_limited_links()
    #queueName = queue-crawledarchiveurls or queue-extractedpagedetails
    queue =  AZQueue(queueName)#for fetching links
    result = await queue.GetAllQueueMessages(True)
    return " <br/>".join(result)



@app.get("/ProcessNLP")
async def invoke_web_crawling():
    results = await NLPProcesor.Invoke()
    return results



@app.get("/Search")
async def invoke_Search(searchQuery: str):
    results = await Search.search_similar_text(searchQuery)
    return results
