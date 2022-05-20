import json
import os


from AGE_ETL import sanitizetext



dist=[]

gatheredDist = set()

with open('../01_WebFocusedCrawl_AF/afconsumer.jl') as f:
    for line in f:
        dist.append(json.loads(line))

for entity in dist:
    gatheredDist.add(sanitizetext(entity['entity']))



#ineffecient but load everything into memory first
data = []
with open('../01_WebFocusedCrawl_AF/affiles.jl') as f:
    for line in f:
        data.append(json.loads(line))



CleanProductDictionary = dict()

uniqueProductsIDs = set()
uniqueComplement = set()
uniqueRelated = set()
UniqueDistrib = set()

uniqueMissingPordID = set()

dupcount = 0
for entry in data:
    if entry['attributeinfo']['ProdAFID'] in uniqueProductsIDs:
        #There should only be one entry for each product ID if there is more than 1 that means the product falls into mutiple main categories
        dupcount = dupcount + 1
        ProdID = entry['attributeinfo']['ProdAFID']
        CleanProductDictionary[ProdID]['categoryName'] = CleanProductDictionary[ProdID]['attributeinfo']['categoryName'] + ", " + entry['attributeinfo']['categoryName']
    else:
        ProdID = entry['attributeinfo']['ProdAFID']
        uniqueProductsIDs.add(entry['attributeinfo']['ProdAFID'])
        
        cleanTechDetProd = []
        cleanRelProd = []
        cleanCompProd = []
        cleanProdDist = []
        
        if entry['attributeinfo']['ComplementProducts']:
            for prodid in entry['attributeinfo']['ComplementProducts']:
                cleanCompProd.append(prodid.split("/")[-1])
                uniqueComplement.add(prodid.split("/")[-1])

        if entry['attributeinfo']['RelatedProducts']:
            for prodid in entry['attributeinfo']['RelatedProducts']:
                cleanRelProd.append(prodid.split("/")[-1])
                uniqueRelated.add(prodid.split("/")[-1])
        if entry['attributeinfo']['ProdDistributors']:
            for prodid in entry['attributeinfo']['ProdDistributors']:
                if sanitizetext(prodid) in gatheredDist:
                    cleanProdDist.append(sanitizetext(prodid))
                    UniqueDistrib.add(sanitizetext(prodid))
                #else:
                    #print("Dist Name not Scraped:" + sanitizetext(prodid))
        
        if entry['attributeinfo']['ProdTechnicalDetails']:
            for prodid in entry['attributeinfo']['ProdTechnicalDetails']:
                cleanTechDetProd.append(sanitizetext(prodid))

        
        CleanProductDictionary[ProdID] = {
            'entity':  sanitizetext(entry['entity']),
            'infourl': entry['infourl'],

            'ProdAFID': ProdID,
            'ProdAFPrice': sanitizetext(entry['attributeinfo']['ProdAFPrice']),
            'categoryName': sanitizetext(entry['attributeinfo']['categoryName']),


            'ProdTechnicalDetails': cleanTechDetProd,
            'ComplementProducts': cleanCompProd,
            'RelatedProducts': cleanRelProd,
            'ProdDistributors': cleanProdDist,

            'ProdDesc': sanitizetext(entry['text']),
            'entitytype': entry['entitytype']
            
            }
MissingProdIDs = 0

if os.path.exists("cleanAFproducts.jl"):
  os.remove("cleanAFproducts.jl")

for key, entry in CleanProductDictionary.items():
    cleanRel = []
    cleanComp = []
    for prodid in entry['ComplementProducts']:
        if prodid in uniqueProductsIDs:
            cleanComp.append(prodid)
            MissingProdIDs = MissingProdIDs + 1
        #else:
            #print("NotScraped Prod ID: " + prodid)
    for prodid in entry['RelatedProducts']:
        if prodid in uniqueProductsIDs:
            cleanRel.append(prodid)
            MissingProdIDs = MissingProdIDs + 1
        #else:
            #print("NotScraped Prod ID: " + prodid)
    entry['RelatedProducts'] = cleanRel
    entry['ComplementProducts'] = cleanComp

    with open("cleanAFproducts.jl", "a") as outfile:
        json.dump(entry, outfile) 
        outfile.write('\n')

    
for pID in uniqueComplement:
    if pID not in uniqueProductsIDs:
        uniqueMissingPordID.add(pID)
for pID in uniqueRelated:
    if pID not in uniqueProductsIDs:
        uniqueMissingPordID.add(pID)


with open("cleanAFproducts.json", "w") as outfile:
    json.dump(CleanProductDictionary, outfile) 

#with open("test.txt", "w") as outfile:
#    for line in uniqueMissingPordID:
#        outfile.write(line + '\n')

print("Duplicate entries: " + str(dupcount))
print("MissingProdIDs: " + str(MissingProdIDs))
print("unique Missing ProdIDs: " + str(len(uniqueMissingPordID)))
print("Total Unique ID Records: " + str(len(uniqueProductsIDs)))