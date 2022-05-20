import psycopg2
import json
import re

import pswdconf

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

#GraphDB name
GraphDBname = 'adafruit'

def sanitizetext(inputtext):
    inworktext = inputtext
    # Single Quotes kill the json formated text
    inworktext = re.sub(r"[']", "", inworktext)
    inworktext = re.sub(r"[\n]", " ", inworktext)
    return inworktext


def GenCypNodeComp():
    cyphQryLst = []

    data = []
    with open('../01_WebFocusedCrawl_AF/main-companiesitems.jl') as f:
        for line in f:
            data.append(json.loads(line))
    preventity = ""
    for entry in data:
        entity = sanitizetext(entry['entity'])
        if entity == preventity:
            continue
        else:
            preventity=entity
        infourl = entry['infourl']
        lbl = 'Company'


        entitytype = sanitizetext(entry['entitytype'])

        cQtmp = f"$$ CREATE (:{lbl} {{entity: '{entity}', infourl: '{infourl}'"
        cQtmp = cQtmp + f", entitytype: '{entitytype}'"
        cQtmp = cQtmp + f"}}) $$) as (n agtype);"

        cyphQryLst.append(cQtmp)

    return cyphQryLst

def GenCypEdgeComp():
    cyphQryLst = []

    data = []
    with open('../01_WebFocusedCrawl_AF/main-companiesitems.jl') as f:
        for line in f:
            data.append(json.loads(line))
    
    preventity = ""
    for entry in data:
        entity = sanitizetext(entry['entity'])
        if entity == preventity:
            continue
        else:
            preventity=entity
        #infourl = entry['infourl']
        lbl = 'Company'


        #entitytype = entry['entitytype']

        cQtmp = f"$$ MATCH (a:{lbl}), (c:{lbl}) WHERE a.entity='Adafruit' AND c.entity='{entity}'"
        cQtmp = cQtmp + f" CREATE (a)-[rel:is_a_rival_of]->(c) RETURN rel $$) as (rel agtype);"

        cyphQryLst.append(cQtmp)

    return cyphQryLst


def GenCypNodeBuyers():
    cyphQryLst = []

    data = []
    with open('../01_WebFocusedCrawl_AF/afconsumer.jl') as f:
        for line in f:
            data.append(json.loads(line))
    
    for entry in data:
        entity = sanitizetext(entry['entity'])
        infourl = entry['infourl']
        lbl = 'Company'

        entitytype = sanitizetext(entry['entitytype'])
        region = sanitizetext(entry['attributeinfo']['major_region'])
        country = sanitizetext(entry['attributeinfo']['country'])
        companyurl = entry['attributeinfo']['url']
        

        cQtmp = f"$$ CREATE (:{lbl} {{entity: '{entity}', infourl: '{infourl}'"
        cQtmp = cQtmp + f", entitytype: '{entitytype}', region: '{region}', country: '{country}', companyurl: '{companyurl}'"
        cQtmp = cQtmp + f"}}) $$) as (n agtype);"

        cyphQryLst.append(cQtmp)

    return cyphQryLst

def GenCypEdgeBuyers():
    cyphQryLst = []

    data = []
    with open('../01_WebFocusedCrawl_AF/afconsumer.jl') as f:
        for line in f:
            data.append(json.loads(line))
    
    preventity = ""
    for entry in data:
        entity = sanitizetext(entry['entity'])
        lbl = 'Company'


        #entitytype = entry['entitytype']

        cQtmp = f"$$ MATCH (a:{lbl}), (c:{lbl}) WHERE a.entity='Adafruit' AND c.entity='{entity}'"
        cQtmp = cQtmp + f" CREATE (a)-[rel:sells_to]->(c) RETURN rel $$) as (rel agtype);"

        cyphQryLst.append(cQtmp)

    return cyphQryLst

def GenCypNodeAFproducts():
    cyphQryLst = []

    data = []
    with open('cleanAFproducts.jl') as f:
        for line in f:
            data.append(json.loads(line))
    #print(data)
    for entry in data:
        entity = sanitizetext(entry['entity'])
        infourl = entry['infourl']
        lbl = 'Product'

        #entitytype = sanitizetext(entry['entitytype'])
        #print(entity)
        #print(type(entity))
        
        
        ProdAFID = entry['ProdAFID']
        categoryName = entry['categoryName']
        

        cQtmp = f"$$ CREATE (:{lbl} {{entity: '{entity}', infourl: '{infourl}'"
        cQtmp = cQtmp + f", ProdAFID: '{ProdAFID}', MajorProdcategory: '{categoryName}'"
        cQtmp = cQtmp + f"}}) $$) as (n agtype);"

        cyphQryLst.append(cQtmp)
        
    return cyphQryLst   

def GenCypEdgeProductBase():
    cyphQryLst = []

    data = []
    with open('cleanAFproducts.jl') as f:
        for line in f:
            data.append(json.loads(line))
    
    for entry in data:
        entityAFID = entry['ProdAFID']
        lbl1 = 'Company'
        lbl2 = 'Product'
        price = entry['ProdAFPrice']

        #entitytype = entry['entitytype']

        cQtmp = f"$$ MATCH (a:{lbl1}), (p:{lbl2}) WHERE a.entity='Adafruit' AND p.ProdAFID='{entityAFID}'"
        cQtmp = cQtmp + f" CREATE (a)-[rel:Sells {{USDprice: '{price}'}}]->(p) RETURN rel $$) as (rel agtype);"

        cyphQryLst.append(cQtmp)

        
        if entry['ComplementProducts']:
            for prodID in entry['ComplementProducts']:
                cQtmp = f"$$ MATCH (a:{lbl2}), (p:{lbl2}) WHERE a.ProdAFID='{entityAFID}' AND p.ProdAFID='{prodID}'"
                cQtmp = cQtmp + f" CREATE (a)-[rel:Is_Complement_To]->(p) RETURN rel $$) as (rel agtype);"

                cyphQryLst.append(cQtmp)
        """
        # Adds almost 50,000 Relationships Removing for now
        if entry['RelatedProducts']:
            for prodID in entry['RelatedProducts']:
                cQtmp = f"$$ MATCH (a:{lbl2}), (p:{lbl2}) WHERE a.ProdAFID='{entityAFID}' AND p.ProdAFID='{prodID}'"
                cQtmp = cQtmp + f" CREATE (a)-[rel:Is_Related_To]->(p) RETURN rel $$) as (rel agtype);"

                cyphQryLst.append(cQtmp)
        """
        if entry['ProdDistributors']:
            for company in entry['ProdDistributors']:
                cQtmp = f"$$ MATCH (c:{lbl1}), (p:{lbl2}) WHERE c.entity='{company}' AND p.ProdAFID='{entityAFID}'"
                cQtmp = cQtmp + f" CREATE (c)-[rel:Buys]->(p) RETURN rel $$) as (rel agtype);"

                cyphQryLst.append(cQtmp)
    return cyphQryLst

#Define the connection and create a cursor to exicute commands
conn = psycopg2.connect(host=ip, database=db, user=user, password=pwd)
cur = conn.cursor()

#Test the connection and cursor by selecting the current_date from the postgreSQL server
cur.execute('SELECT CURRENT_DATE;')

print("If your connection worked the current date is:")
print(cur.fetchall()[0])

cur.execute("LOAD '$libdir/plugins/age';")
cur.execute("SET search_path = ag_catalog, '$user', public;")

#-----------------------------------------------------------------
#------------------RESET GRAPH------------------------------------
cur.execute(f"SELECT drop_graph('{GraphDBname}', true);")
conn.commit()
cur.execute(f"SELECT create_graph('{GraphDBname}');")
conn.commit()
#----------------------------------------------------------------

print("Main Company Manual Entry")
cur.execute(f"SELECT * FROM cypher('{GraphDBname}', $$ CREATE (:Company {{entity: 'Adafruit', title: 'Main Company We are Investigating', infourl: 'https://www.adafruit.com/'}}) $$) as (n agtype);")
conn.commit()

#competitors
print("Starting Competitors")
CyphQ = GenCypNodeComp()
for query in CyphQ:
    cur.execute(f"SELECT * FROM cypher('{GraphDBname}', " + query)
conn.commit()

print("Relationships Competitors")
CyphQ = GenCypEdgeComp()
for query in CyphQ:
    cur.execute(f"SELECT * FROM cypher('{GraphDBname}', " + query)
conn.commit()

#buyers/distributors
print("Starting buyers/distributors")
CyphQ = GenCypNodeBuyers()
for query in CyphQ:
    cur.execute(f"SELECT * FROM cypher('{GraphDBname}', " + query)
conn.commit()

print("Relationships buyers/distributors")
CyphQ = GenCypEdgeBuyers()
for query in CyphQ:
    cur.execute(f"SELECT * FROM cypher('{GraphDBname}', " + query)
conn.commit()

#-------------------PRODUCTS-------------------------
print("Starting AF Products")
CyphQ = GenCypNodeAFproducts()
counter = 0
for query in CyphQ:
    if counter >= 15:
        counter = 0
        conn.commit()
    cur.execute(f"SELECT * FROM cypher('{GraphDBname}', " + query)
    counter = counter + 1
conn.commit()

print("Relationships AF Products")
CyphQ = GenCypEdgeProductBase()
counter = 0
counterStats = 1
for query in CyphQ:
    if counter >= 15:
        counter = 0
        conn.commit()
        if counterStats >= 100:
            print("Just Loaded: " + str(15 * counterStats))
            counterStats = 0
        counterStats = counterStats + 1
    cur.execute(f"SELECT * FROM cypher('{GraphDBname}', " + query)
    counter = counter + 1
conn.commit()

# Clean up when done
cur.close()
if conn is not None:
    conn.close()

print("done and closed")
#print(CyphQ)
