import json
import re


import pswdconf
import psycopg2

#connectingTo = 'local'
connectingTo = 'remote'

if connectingTo == 'local':
    ip = pswdconf.localIP
    user = pswdconf.localuser
    pwd = pswdconf.localpwd
    db = pswdconf.localdb
else:
    ip = pswdconf.remoteIP
    user = pswdconf.remoteuser
    pwd = pswdconf.remotepwd
    db = pswdconf.remotedb


def prepforSQL(textToPrep):
    temptext = textToPrep
    temptext = temptext.replace("'", "''")
    temptext = temptext.replace(";", "")
    return temptext

def cleanText(textToClean):
    temptext = textToClean
    #Replace spaces charrage returns tabs etc with a single normal space
    temptext = temptext.replace("\u00a0", " ")
    temptext = temptext.replace("\n", " ")
    temptext = temptext.replace("\r", " ")
    temptext = temptext.replace("\t", " ")

    #replace web special characters with a single space
    #Note* on some websites this seems to replace single quotes and double quotes it depends on how the site is coded and pulled
    temptext = re.sub(r'\\u[a-f0-9]{4}', ' ', temptext)

    temptext = re.sub(' [ ]+', ' ', temptext)

    return temptext

dist=[]

gatheredDist = set()

LongestItem = 0


filenames = ['affiles.jl']

#ineffecient but load everything into memory first
data = []

with open('../01_WebFocusedCrawl_AF/afconsumer.jl') as f:
    for line in f:
        tmpjson = json.loads(line)
        data.append({
            'DocTitle': tmpjson['entity'], 
            'DocType': tmpjson['entitytype'], 
            'DocLink':tmpjson['attributeinfo']['url'], 
            'Text': cleanText(tmpjson['text']) + ' ' + tmpjson['attributeinfo']['major_region'] + ' ' + tmpjson['attributeinfo']['country']
            })
with open('../01_WebFocusedCrawl_AF/main-companiesitems.jl') as f:
    prevjson = {'entity': "NONE"}
    for line in f:
        tmpjson = json.loads(line)
        
        if prevjson['entity'] != tmpjson['entity']:
            if prevjson['entity'] != "NONE":
                data.append({
                    'DocTitle': prevjson['entity'], 
                    'DocType': prevjson['entitytype'], 
                    'DocLink':prevjson['infourl'], 
                    'Text': prevjson['text']
                    })
            prevjson = tmpjson
        else:
            prevjson={'entity': tmpjson['entity'], 'entitytype': tmpjson['entity'], 'infourl': prevjson['infourl'], 'text': cleanText(prevjson['text']) + ' ' + cleanText(tmpjson['text'])}
    data.append({
                'DocTitle': prevjson['entity'], 
                'DocType': prevjson['entitytype'], 
                'DocLink':prevjson['infourl'], 
                'Text': cleanText(prevjson['text'])
                })
    

 
with open('../02_Create_PostGreSQL_AGE/cleanAFproducts.jl') as f:
    for line in f:
        tmpjson = json.loads(line)
        data.append({
            'DocTitle': tmpjson['entity'], 
            'DocType': tmpjson['entitytype'], 
            'DocLink':tmpjson['infourl'], 
            'Text': cleanText(tmpjson['ProdDesc'])
            })



for x in range(len(data)):   
    if LongestItem <= len(data[x]['Text']):
        LongestItem = len(data[x]['Text'])

print(LongestItem)





#Define the connection and create a cursor to exicute commands
conn = psycopg2.connect(host=ip, database=db, user=user, password=pwd)
cur = conn.cursor()

#Test the connection and cursor by selecting the current_date from the postgreSQL server
cur.execute("SELECT EXISTS (SELECT FROM pg_tables WHERE  schemaname = 'adafruit_rel' AND tablename  = 'adafruit_docs')")

print("Check if the table exits we will do a flush and reload")
if cur.fetchall()[0][0]:
    print("Drop Table and Remaking Table")
    cur.execute("DROP TABLE adafruit_rel.adafruit_docs")
    conn.commit()

print("Creating Table adafruit_docs")
SQLcreate_adafruit_docs = """
    CREATE TABLE adafruit_rel.adafruit_docs (
        DocTitle VARCHAR(200),
        DocType VARCHAR(50),
        DocLink VARCHAR(255),
        Text VARCHAR,
        id SERIAL PRIMARY KEY
    );
"""

cur.execute(SQLcreate_adafruit_docs)
conn.commit()



i = 0        
for record in data:
    SQLstatment = f"INSERT INTO adafruit_rel.adafruit_docs VALUES ('{prepforSQL(record['DocTitle'])}', '{prepforSQL(record['DocType'])}', '{prepforSQL(record['DocLink'])}', '{prepforSQL(record['Text'])}');"
    cur.execute(SQLstatment)
    i = i + 1
    if i > 20:
        i = 0
        conn.commit()






print("Creating GIN index for full text search")

#https://www.postgresql.org/docs/current/textsearch-tables.html
ginSQL = """
ALTER TABLE adafruit_rel.adafruit_docs
    ADD COLUMN textsearchable_index_col tsvector;
"""
cur.execute(ginSQL)
conn.commit()
ginSQL = """
UPDATE adafruit_rel.adafruit_docs
SET textsearchable_index_col = to_tsvector('english', coalesce(Text,''))

"""
cur.execute(ginSQL)
conn.commit()


createindexSQL = """
CREATE INDEX textsearch_idx ON adafruit_rel.adafruit_docs USING GIN (textsearchable_index_col);
"""
cur.execute(createindexSQL)
conn.commit()

cur.close()
if conn is not None:
    conn.close()

print("Created Done")
