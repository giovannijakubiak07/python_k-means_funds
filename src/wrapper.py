
import json
from lxml import html
import re
import requests
from peewee import *
import sklearn
import pandas as pd
import sqlite3
from sklearn.cluster import KMeans
import matplotlib.pyplot
import matplotlib.pyplot as plt

db = SqliteDatabase('database_fundos.db')

class Fundo(Model):
    name = CharField()
    twelveMonths = DecimalField	()
    variable = DecimalField()

    class Meta:
        database = db

db.connect()
db.create_tables([Fundo])

class oAtivo:
    def __init__(self, name, twelveMonths, variable):
        self.name = name
        self.twelveMonths = twelveMonths
        self.variable = variable

############################################
#EXTRAINDO INDORMAÇÕES DO SITE DA CORRETORA#
############################################
page = requests.api.get('https://www.genialinvestimentos.com.br/investimentos/fundos/lista-completa/',  headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.103 Safari/537.36"})
tree = html.fromstring(page.content)
script = tree.xpath('//script[contains(., "arrayFundosLista")]/text()')[0]

data = re.split("=", script)[1]
data = json.loads(data)

print('###############')
print('consulta ativos')
print('###############')

for ativo in data:
    ########################################################
    #CRIANDO AS ENTIDADES E SALVANDO NO BANCO SQLIT VIA ORM#
    ########################################################
    Fundo.create(name=ativo["FinancialInstrumentName"],
                 twelveMonths=ativo["TwelveMonths"],
                 variable=ativo["Day"]) #aqui pode-se escolher qual variável auxiliar será utilizada para a clusterização, melhor encontrada foi "Day"

###################################
#EXIBINDO OS FUNDOS SEM FORMATAÇÃO#
###################################
for fundo in Fundo.select():
    print(fundo.name)
    print(fundo.twelveMonths)
    print(fundo.variable)

###############
#CLUSTERING...#
###############
conn = sqlite3.connect('Database_fundos.db')
query = "SELECT twelveMonths, variable FROM Fundo;"

df = pd.read_sql_query(query,conn)

dfn= df.to_numpy()

modelo = KMeans(n_clusters=20)
modelo.fit_predict(dfn)
rotulos = modelo.fit_predict(dfn)

plt.scatter(dfn[:, 0], dfn[:, 1],c=rotulos)
plt.show()

