#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov  8 16:33:49 2017

@author: vitor
"""

arquivo = open('./pre-processamento.txt', 'r') # Abra o arquivo (leitura)
conteudo = arquivo.readlines()
conteudo.append('Teste7\n')   # insira seu conteúdo
conteudo.append('Teste8\n')
conteudo.append('Teste9\n')
conteudo.append('Teste10\n')
arquivo = open('./pre-processamento.txt', 'w') # Abre novamente o arquivo (escrita)
arquivo.writelines(conteudo)    # escreva o conteúdo criado anteriormente nele.
arquivo.close() 