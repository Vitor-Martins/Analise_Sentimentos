# -*- coding: utf-8 -*-
"""
Spyder Editor

Este é um arquivo de script temporário.

@author: Vitor Martins
"""
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

arquivo = open('./teste.txt','r')

#teste = arquivo.encode('utf8','strict')
texto = arquivo.readlines()


#print(texto[0])


#frases = nltk.sent_tokenize(texto)
#palavras = nltk.word_tokenize(texto)

#frases[50:]
#palavras[50:]

basetoken = []
stop_words = set(stopwords.words('portuguese'))

#stop_words.update(('','http','and','I','A','And','So','arnt','This','When','It','many','Many','so','cant','Yes','yes','No','no','These','these'))

#print(stop_words)

for tweet in texto:
    palavras = nltk.word_tokenize(tweet)
    palavras = [palavra for palavra in palavras if palavra.lower().isalpha()]
    palavras = [palavra for palavra in palavras if len(palavra) > 1]
    palavras = [palavra for palavra in palavras if palavra.lower() not in stop_words]
    #palavras = [str(stemmer.stem(p)) for p in str(palavras).split()]
    basetoken.append(palavras)

arquivo = open('./pre-processamento.txt', 'r') # Abra o arquivo (leitura)
conteudo = arquivo.readlines()

for linha in basetoken:
    myString = " ".join(linha)      
    #print (basetoken)
    conteudo.append(myString + '\n')   # insira seu conteúdo
    arquivo = open('./pre-processamento.txt', 'w') # Abre novamente o arquivo (escrita)
    arquivo.writelines(conteudo)    # escreva o conteúdo criado anteriormente nele.
arquivo.close() # Escrever um arquivo substituindo tudo
#arq_pre = open('./pre-processamento.txt', 'w')
#arq_pre.write(basetoken)
#arq_pre.close()    


# Inserir conteúdo dentro do arquivo
#arquivo = open('nome.txt', 'r') # Abra o arquivo (leitura)
#conteudo = arquivo.readlines()
#conteudo.append('Nova linha')   # insira seu conteúdo
#arquivo = open('nome.txt', 'w') # Abre novamente o arquivo (escrita)
#arquivo.writelines(conteudo)    # escreva o conteúdo criado anteriormente nele.
#arquivo.close()    




