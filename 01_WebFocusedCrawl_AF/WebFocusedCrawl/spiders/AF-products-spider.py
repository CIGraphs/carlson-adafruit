# Scrape Wikipedia, saving page html code to wikipages directory 
# Most Wikipedia pages have lots of text 
# We scrape the text data creating a JSON lines file items.jl
# with each line of JSON representing a Wikipedia page/document
# Subsequent text parsing of these JSON data will be needed
# This example is for the topic robotics
# Replace the urls list with appropriate Wikipedia URLs
# for your topic(s) of interest

# ensure that NLTK has been installed along with the stopwords corpora
# pip install nltk
# python -m nltk.downloader stopwords

import scrapy
import os.path
from WebFocusedCrawl.items import WebfocusedcrawlItem  # item class 
import nltk  # used to remove stopwords from tags
import re  # regular expressions used to parse tags

def remove_stopwords(tokens):
    stopword_list = nltk.corpus.stopwords.words('english')
    good_tokens = [token for token in tokens if token not in stopword_list]
    return good_tokens     

class ArticlesSpider(scrapy.Spider):
    name = "AF-products-spider"

    def start_requests(self):
        #Spider for Adafruit Products
        urls = [
            "https://www.adafruit.com/categories",
            ]


        for urlpage in urls:
            #Assume we have already downselected and will be pulling info for all products in each category
            yield scrapy.Request(url=urlpage, callback=self.initialpass)


    #We care about all the H2 a href tags as these are links to all the main categories
    def initialpass(self, response):
        
        #URLChecker = response.url.split("/")[2]
        
       if response.xpath('//h2/a/@href'):
            for url in response.xpath('//h2/a/@href').extract():
                # Manually looking at adafruit's category links all of the categorie href start with /category/NUMBER
                # We only want categories. 
                
                if url.split("/")[1] == "category":
                    
                    #print(url)
                    url = 'https://www.adafruit.com' + url
                    yield scrapy.Request(url=url, callback=self.productpass, cb_kwargs=dict(categoryID=url.split("/")[2]))

       return "good to go"

    #Each category has a list of product hyperlinks that relate to that category, Bring the Category ID from the categories and Look for all product hrefs
    def productpass(self, response, categoryID):
        
        category = response.xpath('//h1[@id="productListHeading"]//text()').extract()[0]
        #print(category)
        #print(response)
        
        for url in response.xpath('//h2/a/@href').extract():
            #print(url)
            url = 'https://www.adafruit.com' + url
            yield scrapy.Request(url=url, callback=self.productparse, cb_kwargs=dict(categoryID=categoryID, categoryName=category))
        return "good to go"

    #For each product we want to actually parse the information and return it as well as save the page:
    def productparse(self, response, categoryID, categoryName):
        # first part: save each page html to wikipages directory
        print(categoryID, categoryName)
        #Product Name
        #print("Prod Name", response.xpath('//h1[@class="products_name"]//text()').extract()[0])
        #Product ID
        #print("Prod ID", response.xpath('//div[@class="product_id"]/span//text()').extract()[0])
        #Product Price
        #print("Prod Price", response.xpath('//div[@id="prod-price"]/span/@content').extract()[0])
        #Description -- LIST
        #print("Prod Desc", response.xpath('//div[@id="tab-description-content"]/p//text()').extract())
        #Technical Details -- LIST
        #print("Technical Details", response.xpath('//div[@id="tab-technical-details-content"]/p//text()').extract())
        #Complement Products -- LIST
        #print("Complement Products", response.xpath('//label/a/@href').extract())       
        #Related Products -- LIST
        #print("Related Products", response.xpath('//div[@id="tab-related-products-content"]/div/div/div/a/@href').extract())
        #Distributors
        #print("Distributors", response.xpath('//ul[@id="prod-distributors"]/li/a/h3//text()').extract())
        #BULK PRICES I"M NOT PULLING
        
        ProdName = response.xpath('//h1[@class="products_name"]//text()').extract()[0]
        #Product ID
        ProdAFID = response.xpath('//div[@class="product_id"]/span//text()').extract()[0]
        #Product Price
        ProdAFPrice = response.xpath('//div[@id="prod-price"]/span/@content').extract()[0]
        #Description -- LIST
        ProdDesc = response.xpath('//div[@id="tab-description-content"]/p//text()').extract()
        #Technical Details -- LIST
        ProdTechnicalDetails = response.xpath('//div[@id="tab-technical-details-content"]/p//text()').extract()
        #Complement Products -- LIST
        ComplementProducts = response.xpath('//label/a/@href').extract()
        #Related Products -- LIST
        RelatedProducts = response.xpath('//div[@id="tab-related-products-content"]/div/div/div/a/@href').extract()
        #Distributors
        ProdDistributors = response.xpath('//ul[@id="prod-distributors"]/li/a/h3//text()').extract()
        
	
        page = response.url.replace("/", ".")
        page_dirname = 'adafruit-product'
        filename = '%s.html' % page
        with open(os.path.join(page_dirname,filename), 'wb') as f:
            f.write(response.body)
        self.log('Saved file %s' % filename) 
        
        item = WebfocusedcrawlItem()
        item['infourl'] = response.url
        
        #Manually edit for each Type of page/product.
        item['entity'] = ProdName
        item['entitytype'] = "Product"
        item['text'] = ProdDesc
        item['attributeinfo'] = {'categoryName': categoryName, 'categoryID': categoryID, 'ProdAFID': ProdAFID, 
                                 'ProdAFPrice': ProdAFPrice, 'ProdDesc': ProdDesc, 
                                 'ProdTechnicalDetails': ProdTechnicalDetails, 'ComplementProducts': ComplementProducts,
                                 'RelatedProducts': RelatedProducts, 'ProdDistributors': ProdDistributors}
                                 
                                 
        return item 
