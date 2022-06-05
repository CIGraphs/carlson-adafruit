import json

RegionSet = set()
CountrySet = set()
ConsumerTypeSet = set()
ComsumerList = set()

CompetitorTypeSet = set()
CompetitorList = set()

ProdCategorySet = set()




with open('../01_WebFocusedCrawl_AF/afconsumer.jl') as f:
    for line in f:
        
        
        tmpjson = json.loads(line)
        
        ComsumerList.add(tmpjson['entity'].lower())
        RegionSet.add(tmpjson['attributeinfo']['major_region'].lower())
        CountrySet.add(tmpjson['attributeinfo']['country'].lower())
        ConsumerTypeSet.add(tmpjson['entitytype'].lower())
        
with open('../01_WebFocusedCrawl_AF/main-companiesitems.jl') as f:
    for line in f:
        tmpjson = json.loads(line)
        
        CompetitorTypeSet.add(tmpjson['entitytype'].lower())
        CompetitorList.add(tmpjson['entity'].lower())

        
    

 
with open('../02_Create_PostGreSQL_AGE/cleanAFproducts.jl') as f:
    for line in f:
        tmpjson = json.loads(line)
        
        ProdCategorySet.add(tmpjson['categoryName'])

SetLists = ['RegionSet', 'CountrySet', 'ConsumerTypeSet', 'ComsumerList', 'CompetitorTypeSet', 'CompetitorList', 'ProdCategorySet']
SetDict = {'RegionSet': RegionSet, 
            'CountrySet': CountrySet, 
            'ConsumerTypeSet': ConsumerTypeSet, 
            'ComsumerList': ComsumerList,
            'CompetitorTypeSet': CompetitorTypeSet, 
            'CompetitorList': CompetitorList, 
            'ProdCategorySet': ProdCategorySet
        }


for file in SetLists:
    with open(file + '.py', 'w') as f:
        f.write(f'{file} = [')
        for entry in SetDict[file]:
            f.write(f', "{entry}"')
        f.write(']')