# https://docs.microsoft.com/en-us/azure/storage/queues/storage-python-how-to-use-queue-storage?tabs=python2%2Cenvironment-variable-windows
# https://pypi.org/project/azure-data-tables/

from azure.storage.queue import (
        QueueService,
        QueueMessageFormat
)


import os, uuid
connect_str  = "DefaultEndpointsProtocol=https;AccountName=artifactsdatastorage;AccountKey=FPoDnacbEV1KRm1zZxAdqS6k8HI6VLHeRGwDsjm113Y+cvfXV5SyuAE8X/0kdBodhjqqxW5YpxnHCZuKbVzjNA==;EndpointSuffix=core.windows.net"

class AZQueue:
        
    def __init__(self, queue_name): #Urls is an array with starting point of url
        # queue_name = "queue-crawledarchiveurls"
        self.queue_name = queue_name
        queue_service = QueueService(connection_string=connect_str)
        # Setup Base64 encoding and decoding functions
        queue_service.encode_function = QueueMessageFormat.text_base64encode
        queue_service.decode_function = QueueMessageFormat.text_base64decode
        self.queue_service = queue_service

    
    def QueueUrlFound(self,urlVal):
        print("Queueing url: "+urlVal)
        self.queue_service.put_message(self.queue_name,urlVal)    

    def QueueMessage(self,msg):
        print("Queueing message:"+ msg)
        self.queue_service.put_message(self.queue_name,msg)       

    def GetMessageCount(self):
        metadata = self.queue_service.get_queue_metadata(self.queue_name)
        count = metadata.approximate_message_count
        print("Message count: " + str(count))   
        return count
     

    def GetQueueMessages(self, deleteMsg = False,msglimit= 30):
        messagesArr = ['']
        messages = self.queue_service.get_messages(self.queue_name, num_messages=msglimit)  
        for message in messages:
            print("Dequeueing message: " + message.content)
            messagesArr.append(message)
            if deleteMsg:
                self.queue_service.delete_message(self.queue_name,message.id, message.pop_receipt)  
        return messagesArr

    def DeleteQueueMessages(self, msgId, popReceipt):
        try:
            self.queue_service.delete_message(queue_name=self.queue_name,message_id=msgId,pop_receipt=popReceipt)
        except Exception as e:
            print("Error in DeleteQueueMessages(), Msg: {e}")
          
    
    def GetAllQueueMessages(self, deleteMsg = False):
        messagesArr = []
        queueMessages = self.GetQueueMessages()
        while queueMessages != None and len(queueMessages) > 0:
            for urlMsg in queueMessages:
                if deleteMsg:
                    self.queue_service.delete_message(queue_name=self.queue_name,message_id=urlMsg.id,pop_receipt=urlMsg.pop_receipt)
                    # self.DeleteQueueMessages(urlMsg.id, urlMsg.pop_receipt)
                if urlMsg != None:
                    messagesArr.append(urlMsg.content)
                    
        queueMessages = self.GetQueueMessages()   
        return messagesArr    