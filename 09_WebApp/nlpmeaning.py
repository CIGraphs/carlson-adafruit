#from winreg import QueryReflectionKey
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

import ProdCategorySet
import CountrySet
import RegionSet

#import ComsumerList
#import CompetitorList


#https://discuss.dizzycoding.com/sanitising-user-input-using-python/
import re
#from urlparse import urljoin
#from BeautifulSoup import BeautifulSoup, Comment


PossNodeTypes = [
    'our',
    'adafruit',

    'company',
    'companies',

    'buyer',
    'purchaser',
    'distributor',
    'distributors',
    'hackerspace',
    'hackerspaces',
    'buyers',
    'purchasers'

    'product',
    'products',
    'offers',
    'things'

]

PossNodeTypesMAP = [
    'N:L:Company:entity:Adafruit',
    'N:L:Company:entity:Adafruit',

    'N:L:Company',
    'N:L:Company',
    
    'N:L:Company',
    'N:L:company',
    'N:L:Company:entitytype:Distributor',
    'N:L:Company:entitytype:Distributor',
    'N:L:Company:entitytype:Hackerspace',
    'N:L:Company:entitytype:Hackerspace',
    'N:L:Company',
    'N:L:Company',

    'N:L:Product',
    'N:L:Product',
    'N:L:Product',
    'N:L:Product'
    
]

PossRelNames = [
    'buy',
    'buys',
    'purchases',
    'purchase',
    'distributes',

    'sells',
    'sell',
    'offers',
    'produces',
    'makes',

    'complement',
    'like',
    'similar',
    
    'rival',
    'rivals',
    'competitor',
    'competes'
]

PossRelNamesMAP = [
    'R:L:Buys',
    'R:L:Buys',
    'R:L:Buys',
    'R:L:Buys',
    'R:L:Buys',

    'R:L:Sells',
    'R:L:Sells',
    'R:L:Sells',
    'R:L:Sells',
    'R:L:Sells',

    'R:L:Is_Complement_To',
    'R:L:Is_Complement_To',
    'R:L:Is_Complement_To',

    'R:L:is_a_rival_of',
    'R:L:is_a_rival_of',
    'R:L:is_a_rival_of',
    'R:L:is_a_rival_of'    
]

CompanyTypes = [
    'distributor',
    'hackerspace',
    'competitor',
    ]

CompanyTypesMAP = [
    'N:L:Company:entitytype:Distributor',
    'N:L:Company:entitytype:Hackerspace',
    'N:L:Company:entitytype:Competitor'
]


PossQualifiers = [
    'over',
    'above',
    'more',
    'greater'
    
    'less',
    'below',
    'smaller',
    'under',

    '$',
    'dollars',
    'money'
    ]

PossQualifiersMAP = [
    '>',
    '>',
    '>',
    '>'
    
    '<',
    '<',
    '<',
    '<',

    'R:L:Sells:USDprice',
    'R:L:Sells:USDprice',
    'R:L:Sells:USDprice'
    ]

stop_words = set(stopwords.words('english'))

for word in PossNodeTypes:
    if word in stop_words:
        stop_words.remove(word)

for word in PossRelNames:
    if word in stop_words:
        stop_words.remove(word)

for word in CompanyTypes:
    if word in stop_words:
        stop_words.remove(word)

for word in PossQualifiers:
    if word in stop_words:
        stop_words.remove(word)

AddToStopWords = ['?', '.', ',', 'about']

for word in AddToStopWords:
    stop_words.add(word)

print()

#entitytype, region, country, MajorProdcategory, infourl

"""
def sanitizeHtml(value, base_url=None):
    rjs = r'[s]*(&#x.{1,7})?'.join(list('javascript:'))
    rvb = r'[s]*(&#x.{1,7})?'.join(list('vbscript:'))
    re_scripts = re.compile('(%s)|(%s)' % (rjs, rvb), re.IGNORECASE)
    validTags = 'p i strong b u a h1 h2 h3 pre br img'.split()
    validAttrs = 'href src width height'.split()
    urlAttrs = 'href src'.split() # Attributes which should have a URL
    soup = BeautifulSoup(value)
    for comment in soup.findAll(text=lambda text: isinstance(text, Comment)):
        # Get rid of comments
        comment.extract()
    for tag in soup.findAll(True):
        if tag.name not in validTags:
            tag.hidden = True
        attrs = tag.attrs
        tag.attrs = []
        for attr, val in attrs:
            if attr in validAttrs:
                val = re_scripts.sub('', val) # Remove scripts (vbs & js)
                if attr in urlAttrs:
                    val = urljoin(base_url, val) # Calculate the absolute url
                tag.attrs.append((attr, val))

    return soup.renderContents().decode('utf8')
"""

def MeaningParser (UserInputText):
    #WorkingText = sanitizeHtml(UserInputText)
    # LOWERCASE CAUSES ISSUES WWITH CYPHER CASE SENSITIVE....
    # WorkingText = UserInputText.lower()
    WorkingText = UserInputText
    word_tokens = word_tokenize(WorkingText)
  
    filtered_sentence = [w for w in word_tokens if not w.lower() in stop_words]
  
    filtered_sentence = []
  
    for w in word_tokens:
        if w not in stop_words:
            filtered_sentence.append(w)


    filtered_NamedEntitiesTypes = []
    match_NamedEntities = []
    QuerySetupEntities = []

    for w in filtered_sentence:
        if w.lower() in PossNodeTypes: filtered_NamedEntitiesTypes.append(1)
        elif w.lower() in PossRelNames: filtered_NamedEntitiesTypes.append(2)
        elif w.lower() in PossQualifiers: filtered_NamedEntitiesTypes.append(3)
        elif w.lower() in CompanyTypes: filtered_NamedEntitiesTypes.append(4)
        #elif w in ProdCategorySet.ProdCategorySet: filtered_NamedEntitiesTypes.append(5)
        elif w.lower() in CountrySet.CountrySet: filtered_NamedEntitiesTypes.append(6)
        elif w.lower() in RegionSet.RegionSet: filtered_NamedEntitiesTypes.append(7)
        elif re.match(r"\d+", w) is not None:
            filtered_NamedEntitiesTypes.append(90)
        else: filtered_NamedEntitiesTypes.append(99)

        if filtered_NamedEntitiesTypes[-1] < 90:
            if filtered_NamedEntitiesTypes[-1] == 1:
                for count, value in enumerate(PossNodeTypes):
                    if value == w.lower():
                        match_NamedEntities.append(value)
                        QuerySetupEntities.append(PossNodeTypesMAP[count])
            if filtered_NamedEntitiesTypes[-1] == 2:
                for count, value in enumerate(PossRelNames):
                    if value == w.lower():
                        match_NamedEntities.append(value)
                        QuerySetupEntities.append(PossRelNamesMAP[count])
            if filtered_NamedEntitiesTypes[-1] == 3:
                for count, value in enumerate(PossQualifiers):
                    if value == w.lower():
                        match_NamedEntities.append(value)
                        QuerySetupEntities.append(PossQualifiersMAP[count])
            if filtered_NamedEntitiesTypes[-1] == 4:
                for count, value in enumerate(CompanyTypes):
                    if value == w.lower():
                        match_NamedEntities.append(value)
                        QuerySetupEntities.append(CompanyTypesMAP[count])
            if filtered_NamedEntitiesTypes[-1] == 5:
                match_NamedEntities.append(w)
                QuerySetupEntities.append(w)
            if filtered_NamedEntitiesTypes[-1] == 6:
                match_NamedEntities.append(w)
                QuerySetupEntities.append('F:country:' + w)
            if filtered_NamedEntitiesTypes[-1] == 7:
                match_NamedEntities.append(w)
                QuerySetupEntities.append('F:region:' + w)
        else:
            match_NamedEntities.append(w)
            QuerySetupEntities.append(w)

    print(filtered_sentence)
    print("-----------------")
    print(filtered_NamedEntitiesTypes)
    print(match_NamedEntities)
    print(QuerySetupEntities)
    print("")
    CypherQuery = ParseCypher(QuerySetupEntities)
    print("#######################")
    return CypherQuery
    




def ParseCypher(QueryPartList):
    AlphaBetSoup = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q']
    QueryTypeOrder = []
    TotalNodes = -1
    TotalRel = -1
    for count, item in enumerate(QueryPartList):
        if item == "N:L:Company:entity:Adafruit":
            QueryTypeOrder.append('NodeROOT')
            TotalNodes = TotalNodes + 1
            LastNodeLoc = count
        elif item[:2] == "N:":
            QueryTypeOrder.append('Node')
            TotalNodes = TotalNodes + 1
            LastNodeLoc = count
        elif item[:2] == "R:":
            QueryTypeOrder.append('Rela')
            TotalRel = TotalRel + 1

        #elif item[:2] == "F:" or item[0] == ">" or item[0] == "<": 
        #    QueryTypeOrder.append('Filter')
        #else:
        #    QueryTypeOrder.append('Information')

    
    


    
    #if len(QueryTypeOrder) == 2:
    #    print("Length of QTO:" + str(len(QueryTypeOrder)))
    #    print(QueryTypeOrder)
    #    print("NodeROOT" in QueryTypeOrder)
    #    print("Node" in QueryTypeOrder)
    

    if len(QueryTypeOrder) == 2 and "NodeROOT" in QueryTypeOrder and "Node" in QueryTypeOrder:
        #print("Made it here")
        QueryPartList.remove("N:L:Company:entity:Adafruit")
        QueryTypeOrder.remove("NodeROOT")
        TotalNodes = -1
        LastNodeLoc=0
        for count, item in enumerate(QueryPartList):
            if item == "N:L:Company:entity:Adafruit":
                #QueryTypeOrder.append('NodeROOT')
                TotalNodes = TotalNodes + 1
                LastNodeLoc = count
            elif item[:2] == "N:":
                #QueryTypeOrder.append('Node')
                TotalNodes = TotalNodes + 1
                LastNodeLoc = count
            elif item[:2] == "R:":
                #QueryTypeOrder.append('Rela')
                TotalRel = TotalRel + 1
    
    #print(QueryPartList)
    #print(LastNodeLoc)
    #print(QueryTypeOrder)
    #print(QueryTypeOrder)
    if not QueryTypeOrder:
        print("BAD CYPHER")
        return("Can't Parse Meaning")

    previousEntry = ""
    if QueryTypeOrder[0] == 'Rel':
        NextItem = "Rel"
    else:
        NextItem = "Node"
        
    
    
    for item in QueryTypeOrder:
        #print(item[:4])
        #print(NextItem)
        if item[:4] == NextItem:
            if item == 'Rela':
                NextItem = "Node"
            else: 
                NextItem = "Rela"
            continue
        else:
            print("BAD CYPHER")
            return("Can't Parse Meaning")
            

    #Start to Build Cypher:
    #Always return the last Node's Stuff
    CypherReturn = ""
    CypherSQLReturn = ""
    NodeLabel = QueryPartList[LastNodeLoc].split(':')
    if NodeLabel[2] == 'Product':
        CypherReturn = f"""
            RETURN
            DISTINCT
            {AlphaBetSoup[TotalNodes]}.entity,
            {AlphaBetSoup[TotalNodes]}.MajorProdcategory,
            {AlphaBetSoup[TotalNodes]}.infourl
        """
        CypherSQLReturn = f"""
            $$) AS (
            entity agtype,
            MajorProdcategory agtype,
            infourl agtype
        """
    if NodeLabel[2] == 'Company':
        CypherReturn = f"""
            RETURN
            DISTINCT
            {AlphaBetSoup[TotalNodes]}.entity,
            {AlphaBetSoup[TotalNodes]}.infourl
        """
        CypherSQLReturn = f"""
            $$) AS (
            entity agtype,
            infourl agtype
        """
    #If we end up with Rel Sells then we will add the price to Return

    
    #Assume nothing matters until the first N or R
    CypherStart = "MATCH "
    CypherFilter = " WHERE "
    NodeCount = 0
    relCount = 0
    AddingTerms = False
    for count, item in enumerate(QueryPartList):

        if AddingTerms:
            if item[:2] != "R:" and item[:2] != "N:" and item[:2] != "F:" and count + 1 != len(QueryPartList): 
                ActiveTerm = ActiveTerm + ' ' + item
                continue
            else: 
                if CypherFilter != " WHERE ":
                    CypherFilter = CypherFilter + " AND " 
                CypherFilter = CypherFilter + f" {AlphaBetSoup[NodeCount-1]}.entity contains '{ActiveTerm}'"
        
        if item[:2] == "R:" and NodeCount == 0:      
            CypherStart = CypherStart + f"(z:Company)"
            CypherFilter = CypherFilter + " z.entity='Adafruit'"
        
        if item[:2] == "R:":
            ItemParts = item.split(":")
            CypherStart = CypherStart + f"-[r{AlphaBetSoup[relCount]}:{ItemParts[2]}]"

            if len(ItemParts) > 4:
                if CypherFilter != " WHERE ":
                    CypherFilter = CypherFilter + " AND " 
                CypherFilter = CypherFilter + f"r{AlphaBetSoup[relCount]}.{ItemParts[3]}='{ItemParts[4]}'"
            
            relCount = relCount + 1
        
        elif item[:2] == "N:":
            
            ItemParts = item.split(":")
            if relCount != 0 or NodeCount !=0:
                CypherStart = CypherStart + "-"

            CypherStart = CypherStart + f"({AlphaBetSoup[NodeCount]}:{ItemParts[2]})"

            if len(ItemParts) > 4:
                if CypherFilter != " WHERE ":
                    CypherFilter = CypherFilter + " AND " 
                CypherFilter = CypherFilter + f"{AlphaBetSoup[NodeCount]}.{ItemParts[3]}='{ItemParts[4]}'"
            
            NodeCount = NodeCount + 1        

        elif relCount > 0 or NodeCount > 0:
            if item[:2] == "F:":
                Checker = QueryPartList[count -1].split(":")
                ItemParts= item.split(":")
                if Checker[4] == "Distributor" or Checker[4] == "Hackerspace":
                    if CypherFilter != " WHERE ":
                        CypherFilter = CypherFilter + " AND " 
                    CypherFilter = CypherFilter + f" {AlphaBetSoup[NodeCount-1]}.{ItemParts[1]}='{ItemParts[2]}'"
            else:
                AddingTerms = True
                ActiveTerm = item
                if count + 1 == len(QueryPartList): 
                
                    if CypherFilter != " WHERE ":
                        CypherFilter = CypherFilter + " AND " 
                    CypherFilter = CypherFilter + f" {AlphaBetSoup[NodeCount-1]}.entity contains '{ActiveTerm}'"


    if CypherFilter == " WHERE ":
        CypherFilter = " "
    Cypher = "SELECT * FROM cypher('adafruit', $$ " + CypherStart + CypherFilter + CypherReturn + CypherSQLReturn + ");"
    print(Cypher)
    return Cypher
        





#MeaningParser("Who are our rival companies?")



#MeaningParser("Who are our distributors?")

#MeaningParser("who are our Distributors in Canada")

#MeaningParser("Distributors in Canada that buy Feather Products")

#MeaningParser("Distributors in Europe")

#MeaningParser("Products about Feather")

#MeaningParser("Products about Machine Learning")

#MeaningParser("Raspberry pi")

#MeaningParser("Arduino")