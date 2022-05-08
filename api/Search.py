import gensim
from gensim import corpora
from gensim.similarities import MatrixSimilarity
from operator import itemgetter
import nltk
from translate import Translator
import pandas as pd
from gensim.similarities import MatrixSimilarity


class Search:
    def __init__(self):
        print('Init')
        self.tfidf_corpus = None
        self.lsi_corpus = None
        self.outputFolder = "/Dissertation/"
        self.search_index = None
        self.LoadModel()
        self.LoadDataFrame()
        self.CreateCorpora()
        self.BuildSerchIndex()
        
    def LoadModel(self):
        self.tfidf_model = gensim.corpora.MmCorpus(self.outputFolder+'tfidf_model_mm')
        self.lsi_corpus = gensim.corpora.MmCorpus(self.outputFolder+'lsi_model_mm')
        self.lsi_model = MatrixSimilarity(self.lsi_corpus, num_features = self.lsi_corpus.num_terms)

    def LoadDataFrame(self):
        self.urlDetails = self.outputFolder+'pandasDataFrame.csv'



    def translateTextToEnglish(text2Trans):
        translator= Translator(from_lang="de", to_lang="en")
        translation = translator.translate(text2Trans).replace("&#39;","'")
        return translation

        
    def translateTextToGerman(text2Trans):
        translator= Translator(from_lang="en", to_lang="de")
        translation = translator.translate(text2Trans).replace("&#39;","'")
        return translation
            

    
    def CreateCorpora(self):
        #creating term dictionary
        dictionary = corpora.Dictionary(self.urlDetails.tokenizedWords)
        #filterout if not present in more than 4 pages
        # dictionary.filter_extremes(no_below=4, no_above=0.2)
        #Remove unwanted words from dictionary
        stoplist = set('de')
        stop_ids = [dictionary.token2id[stopword] for stopword in stoplist if stopword in dictionary.token2id]
        dictionary.filter_tokens(stop_ids)
        self.dictionary = dictionary

    def BuildSerchIndex(self):
        self.search_index = MatrixSimilarity(self.lsi_corpus, num_features = self.lsi_corpus.num_terms)

    def search_similar_text(self,search_term):
        query_bow = self.dictionary.doc2bow(nltk.word_tokenize(search_term))
        query_tfidf = self.tfidf_model[query_bow]
        query_lsi = self.lsi_model[query_tfidf]

        self.search_index.num_best = 5

        search_list = self.search_index[query_lsi]

        search_list.sort(key=itemgetter(1), reverse=True)
        search_names = []

        for j, searchResult in enumerate(search_list):
            relavenceFactor =round((searchResult[1] * 100),2)
            if relavenceFactor > 2:
                search_names.append (
                    {
                        'Relevance': round((searchResult[1] * 100),2),
                        'Url': self.urlDetails['Url'][searchResult[0]],
                        'Text': self.urlDetails['TextInfo'][searchResult[0]]
                    }

                )
                if j == (self.search_index.num_best-1):
                    break

        return pd.DataFrame(search_names, columns=['Relevance','Url','Text'])
