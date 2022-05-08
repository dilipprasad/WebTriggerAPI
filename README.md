# WebTriggerAPI
Creating Web Trigger API using a FAST API service and hosting it on azure

# Confiuration 

1. create virtualenv `virtualvenv venv`
2. run `source venv/bin/activate`
3. run `pip install -r requirements.txt`

# running FAST API

run the following command to start `uvicorn api.main:app --reload`

- http://127.0.0.1:8000/docs => Documentation of the API
- http://127.0.0.1:8000 => API end point 


In Azure this website is hosted at 

https://webtriggerapi.azurewebsites.net/

sample url to test
https://webtriggerapi.azurewebsites.net/Ping
