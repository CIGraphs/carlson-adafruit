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
import json
from WebFocusedCrawl.items import WebfocusedcrawlItem  # item class 
import nltk  # used to remove stopwords from tags
import re  # regular expressions used to parse tags

def remove_stopwords(tokens):
    stopword_list = nltk.corpus.stopwords.words('english')
    good_tokens = [token for token in tokens if token not in stopword_list]
    return good_tokens     

class ArticlesSpider(scrapy.Spider):
    name = "AF-consumers-spider"

    def start_requests(self):
        #Spider for Adafruit Products
        urls = [
            "https://www.adafruit.com/distributors",
            ]


        for urlpage in urls:
            #Assume we have already downselected and will be pulling info for all products in each category
            yield scrapy.Request(url=urlpage, callback=self.initialpass)


    #We care about all the H2 a href tags as these are links to all the main categories
    def initialpass(self, response):
        
        #URLChecker = response.url.split("/")[2]
       countrycodeids = []
       if response.xpath('//ul/li/h4//text()'):
            print("IN THE RIGHT FILE")
            
            page = response.url.replace("/", ".")
            page_dirname = 'adafruit-consumers'
            filename = '%s.html' % page
            with open(os.path.join(page_dirname,filename), 'wb') as f:
                f.write(response.body)
            self.log('Saved file %s' % filename) 
            
            for contcountry in response.xpath('//ul/li/h4//@id').extract():
            #for consumer in response.xpath('//ul/li/h4[@id="' + contcountry + '"]/ul/li[@class="hackerdistEntry"]/a/@href | //ul/li[@class="hackerdistEntry"]//text()').extract():
                #print("")
                #print("-------------------------------------------------------------")
                #print(contcountry)
                contcd = contcountry.split("-")
                
                major_region = contcd[0]
                country = contcd[1]
                i = 0
                for consumer in response.xpath('//ul/li[h4[@id="' + contcountry + '"]]/ul/li[@class="hackerdistEntry"]/a/@href | //ul/li[h4[@id="' + contcountry + '"]]/ul/li[@class="hackerdistEntry"]//text()').extract():
                #for consumer in response.xpath('//ul/li/h4[@id="' + contcountry + '"]//following::ul/li[@class="hackerdistEntry"]/a/@href | //ul/li/h4[@id="' + contcountry + '"]//following::ul/li[@class="hackerdistEntry"]//text()').extract():
                    #print(i, consumer)
                    if i == 0:
                        url = consumer
                    elif i == 1:
                        ConsumerName = consumer
                    elif i == 2:
                        consumertype = consumer[3:]
                        #print(major_region, country, ConsumerName, consumertype, url)
                        
                        self.consumerparse(major_region=major_region, country=country, ConsumerName=ConsumerName, consumertype=consumertype, url=url, infourl=response.url)
                        
                        i = -1
                    
                    i = i + 1
                    



            

       #return "good to go"



    #For each product we want to actually parse the information and return it as well as save the page:
    def consumerparse(self, major_region, country, ConsumerName, consumertype, url, infourl):
        
        
        #item = WebfocusedcrawlItem()
        item = dict()
        item['infourl'] = infourl
        
        #Manually edit for each Type of page/product.
        item['entity'] = ConsumerName
        item['entitytype'] = consumertype
        item['text'] = ConsumerName
        item['attributeinfo'] = {'major_region': major_region, 'country': country, 'url': url}
        
        line = json.dumps(item) + "\n"
        #print(line)
        with open('afconsumer.jl', 'a') as f:
            f.write(line)
        
        #self.file.write(line)                         
                                 
        return item 
