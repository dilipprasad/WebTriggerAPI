import json
import logging
# from tkinter.tix import Tree
from  api import CommonMethods
from  api import AzureQueue

from datetime import datetime
import pytz
import pandas as pd
import nltk
from nltk.stem import WordNetLemmatizer
import re
import gensim
from gensim import corpora
from nltk.stem.snowball import SnowballStemmer



class NLPProcesor:
    def __init__(self):
        print('Init')
        self.CommonMethods = CommonMethods.CommonFunctions()
        self.queue_service = AzureQueue.AZQueue("queue-extractedpagedetails")
        self.allLinks = []
        self.queueMessages = [] #queue messages
        self.textData = []
        self.IST = pytz.timezone('Asia/Kolkata')
        self.words = [] #for frequency distribution
        self.lemmatizer = WordNetLemmatizer()
        self.outputFolder = "/Dissertation/"
        self.QueueDownloadLimit = 30 #Max is 32
        self.IsPerformLemmatization= True
        self.stemmer = SnowballStemmer("german")
        try:
            nltk.download('all')
            nltk.download('stopwords')#although we have downloaded everything - doing this to be safe
            # Get English stopwords and print some of them
            self.germanStopWords = nltk.corpus.stopwords.words('german')
        except Exception as e:
            print("Error downloading NLTK packages. Msg: "+ str(e))

        
    def DownloadMessages(self):
        try:
            queueUrlCount = self.queue_service.GetMessageCount()
            print("Message count: " + str(queueUrlCount))
        except Exception as e: 
            print("Problem fetching count from queue. Message : "+ str(e)) 
            return None   

        try:   
            queueMessages = self.queue_service.GetQueueMessages()
            while queueMessages != None and len(queueMessages) > 0:
                print('queue is not none')
                for queMsg in queueMessages:
                    if queMsg != None:
                        msgCont = queMsg.content 
                        print("msgCont: "+ msgCont)
                        # queue_service.delete_message(extractedDetails_queue_name,queMsg.id, queMsg.pop_receipt)
                        #convert string to  object
                        json_object = json.loads(msgCont)
                        url = json_object["Url"]
                        TextInfo = json_object["TextInfo"]
                        if self.CommonMethods.ExisitsInArray(self.allLinks,url) == False and TextInfo != None: #Check if the Url is not already added to the list
                            self.allLinks.append(url)
                            self.textData.append([url, TextInfo])
            queueMessages = self.queue_service.GetQueueMessages()
        except Exception as e: 
            print("Problem Fetching text from queue. Message : "+ str(e))
            return None



    def CreateDataframe(self):
        print("initiaing crawling: "+ datetime.now(self.IST).strftime("%d/%m/%Y %H:%M:%S"))
        self.DownloadMessages()
        arrHeader = ['Url','TextInfo']
        urlDetails = pd.DataFrame(self.textData,  columns= arrHeader)
        self.urlDetails= urlDetails
        print("End of crawling: "+ datetime.now(self.IST).strftime("%d/%m/%Y %H:%M:%S"))     

    def SentenceTokenize(self):
        #create a New column for the scentence tokenization first part of stemming
        self.urlDetails['sent_tokenize'] = self.urlDetails['TextInfo'].apply(nltk.sent_tokenize) 


    def GetWordTokens(self,tokscentences):
        # words = [] #for frequency distribution
        tokWords= []
        for i in range(len(tokscentences)):
            self.tokWords.extend( nltk.word_tokenize(tokscentences[i]) )
            self.words.extend( nltk.word_tokenize(tokscentences[i]))
        return tokWords

    def WordTokenize(self):
        #Create a new column for word tokenization - second part of stemming
        #self.urlDetails['word_tokenize'] = self.urlDetails['sent_tokenize'].apply(self.GetWordTokens) 
        self.urlDetails['word_tokenize'] = self.urlDetails['sent_tokenize'].apply(self.CleanupText) 

    
    def GetStemmedWords(self,tokWords):
        stemmedWords = []
        for i in range(len(tokWords)):
            stemmedWords.append(self.stemmer.stem(tokWords[i]) )
        return stemmedWords


    def GetLemmatizedWords(self,tokWords):
        lemmWords = []
        for i in range(len(tokWords)):
            lemmWords.append( self.lemmatizer.lemmatize(tokWords[i]) )
        return lemmWords

    def WordLemmatization(self):
        #Now create a new column with stemmed words of arry
        #self.urlDetails['lemmaWords'] = self.urlDetails['word_tokenize'].apply(self.GetLemmatizedWords) 
        self.urlDetails['lemmaWords'] = self.urlDetails['withoutStopWords'].apply(self.GetLemmatizedWords) 
   
    def GetMorpholigicalWords(self,tokWords):
        if self.IsPerformLemmatization == True:
            return self.GetLemmatizedWords(tokWords)
        else:
            return self.GetStemmedWords(tokWords)

    def GetScentenceWithoutStopWords(self, tokWords):
        actualWords = [] #without stopwords
        for i in range(len(tokWords)):
            if tokWords[i] not in self.germanStopWords:
                actualWords.append( tokWords[i] )
        return self.CommonMethods.JoinArray(actualWords) #return only the scentence

    def RemoveStopwords(self):
        #Now create a new column with stop words removed
        self.urlDetails['withoutStopWords'] = self.urlDetails['word_tokenize'].apply(self.GetScentenceWithoutStopWords) 

    #Parts of Speech - POS
    def GetPOS(self,tokWords):
        pos_words = []
        tagged_words = nltk.pos_tag(tokWords)
        for tw in tagged_words:
            pos_words.append(tw[0]+"_"+ tw[1])
        return pos_words

    def ApplyPOS(self):
        #Now create a new column with Parts of speech (POS)
        #self.urlDetailss['POS'] = self.urlDetails['word_tokenize'].apply(self.GetPOS) 
        self.urlDetailss['POS'] = self.urlDetails['lemmaWords'].apply(self.GetPOS) 

    
    def GetNamedEnitiy(self,tokWords):##############
        tagged_words = nltk.pos_tag(tokWords)
        return nltk.ne_chunk(tagged_words)

    

    # def LowCaseAndRemoveNonWords(sentTokens):
    #     updatedData = []
    #     for i in range(len(sentTokens)):
    #         val =sentTokens[i].lower()
    #         val =re.sub(r'\W',' ', val) #remove non words such as special characters
    #         val =re.sub(r'\s+',' ', val)  #Remove multip spaces
    #         updatedData.append(val)
    #     return updatedData

    # def ApplyCleanup_LowerCase(self):
    #     #Now create a new column with Lower case and special characters removed for the scentences
    #     self.urlDetails['sent_LowerCase'] = self.urlDetails['sent_tokenize'].apply(self.LowCaseAndRemoveNonWords) 

    def CreateCorpora(self):
        #creating term dictionary
        # dictionary = corpora.Dictionary(self.urlDetails.tokenizedWords)
        dictionary = corpora.Dictionary(self.urlDetails.withoutStopWords)
        #filterout if not present in more than 4 pages
        # dictionary.filter_extremes(no_below=4, no_above=0.2)
        #Remove unwanted words from dictionary
        stoplist = set('de')
        stop_ids = [dictionary.token2id[stopword] for stopword in stoplist if stopword in dictionary.token2id]
        dictionary.filter_tokens(stop_ids)
        self.dictionary = dictionary

    def CreateCorpus(self):
        corpus = [self.dictionary.doc2bow(desc) for desc in self.urlDetails.tokenizedWords]
        # word_frequencies = [[(self.dictionary[id], frequency) for id, frequency in line] for line in corpus[0:3]]
        self.corpus = corpus

    def SaveDF(self):
        csvWritePath = self.outputFolder+'pandasDataFrame.csv'
        print("CSV Write path: "+ csvWritePath)
        # #Write Dataframe to CSV file
        self.urlDetails.to_csv(csvWritePath, index=False)

    def CleanupText(self,scentenceToProcess):
        RE_WSPACE = re.compile(r"\s+", re.IGNORECASE)
        RE_TAGS = re.compile(r"<[^>]+>")
        RE_ASCII = re.compile(r"[^A-Za-zÀ-ž0-9]", re.IGNORECASE)
        RE_SINGLECHAR = re.compile(r"\b[A-Za-zÀ-ž]\b", re.IGNORECASE)

        scentenceToProcess = re.sub(RE_TAGS, " ", scentenceToProcess)
        scentenceToProcess = re.sub(RE_ASCII, " ", scentenceToProcess)
        scentenceToProcess = re.sub(RE_SINGLECHAR, " ", scentenceToProcess)
        scentenceToProcess = re.sub(RE_WSPACE, " ", scentenceToProcess)

        scentenceToProcess = scentenceToProcess.lower()
        words_tokens_lower = nltk.word_tokenize(scentenceToProcess)
        processedWords = []
        #Remove Stop words and get stemmed words
        for word in self.GetMorpholigicalWords(words_tokens_lower): #Loop for the Get stemmed words/ lemmatized words based on config
            if word not in self.germanStopWords:
                processedWords.append(word)

        return processedWords

    def GenerateAndSaveTFIDFModels(self):
        tfidf_model = gensim.models.TfidfModel(self.corpus, id2word=self.dictionary)
        lsi_model = gensim.models.LsiModel(tfidf_model[self.corpus], id2word=self.dictionary, num_topics=300)
        gensim.corpora.MmCorpus.serialize(self.outputFolder+'tfidf_model_mm', tfidf_model[self.corpus])
        gensim.corpora.MmCorpus.serialize(self.outputFolder+'lsi_model_mm',lsi_model[tfidf_model[self.corpus]])

    def Invoke(self):    
        self.CreateDataframe()
        self.SentenceTokenize() #sent_tokenize
        # self.CleanupText()#Check order
        # self.ApplyCleanup_LowerCase()#Check order
        self.WordTokenize() #word_tokenize
        self.RemoveStopwords()#withoutStopWords
        self.WordLemmatization()#lemmaWords
        self.ApplyPOS()#POS
        self.CreateCorpora()#To changed to lemma words
        self.CreateCorpus()
        self.GenerateAndSaveTFIDFModels()


