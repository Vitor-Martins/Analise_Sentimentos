# -*- coding: utf-8 -*-
"""
Created on Sun Nov 05 14:25:35 2017

@author: SOL
"""


import urllib2
import json
import datetime
from abc import ABCMeta
from urllib import urlencode
from abc import abstractmethod
from urlparse import urlunparse
from bs4 import BeautifulSoup
from time import sleep
import logging as log
import md5
import re
import psycopg2
#from connect import do_connect
#from connect import close_connection
import sys  
import nltk
import re
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer



def listatweets():
    conn = psycopg2.connect("dbname='extracoes-twitter' user='postgres' host='localhost' password='senha123'")
    cursor = conn.cursor()

    cursor.execute("SELECT tweet_text  FROM raw_tweets")
    linhas = cursor.fetchall()
    
    frases = []
    for linha in linhas:
        frases.append(str(linha))

    cursor.close()
    conn.close()
    
    return frases

basealfa = listatweets()

basetoken = []

stop_words = set(stopwords.words('english'))

stop_words.update(('','http','and','I','A','And','So','arnt','This','When','It','many','Many','so','cant','Yes','yes','No','no','These','these'))

print(stop_words)


#stemmer = nltk.stem.SnowballStemmer("english", ignore_stopwords=True)
for tweet in basealfa:
    palavras = nltk.word_tokenize(tweet)
    palavras = [palavra for palavra in palavras if palavra.lower().isalpha()]
    palavras = [palavra for palavra in palavras if len(palavra) > 1]
    palavras = [palavra for palavra in palavras if palavra.lower() not in stop_words]
    #palavras = [str(stemmer.stem(p)) for p in str(palavras).split()]
    basetoken.append(palavras)
  
    
con = psycopg2.connect("dbname='extracoes-twitter' user='postgres' host='localhost' password='senha123'")
cur  = con.cursor()  
    
myString = ""

for linha in basetoken:
    myString = " ".join(linha)
    cur.execute("INSERT INTO preprocessado (texto, marca) VALUES ('%s','IBM')" % (myString))

cur.close()
con.commit()
con.close()
    
    


