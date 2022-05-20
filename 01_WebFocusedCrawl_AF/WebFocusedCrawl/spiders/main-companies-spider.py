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
    name = "main-companies-spider"

    def start_requests(self):

        urls = [
            "https://www.sparkfun.com/about_sparkfun",
            "https://www.sparkfun.com/coverage",
            "https://www.arduino.cc/en/Guide/Introduction",
            "https://www.velleman.eu/about/",
            "https://www.seeedstudio.com/blog/about-us-2/",
            "https://make.co/",
            "https://www.canakit.com/Pages/FAQs.aspx",
            "https://www.canakit.com/Contact",
            "https://www.farnell.com/newark/",
            "https://www.farnell.com/emea/",
            "https://www.farnell.com/newark/",
            "https://www.farnell.com/element14/",
            "https://www.farnell.com/our-heritage/",
            "https://www.farnell.com/products-and-expertise/",
            "https://www.farnell.com/where-we-operate/",
            "https://www.farnell.com/policies/"
            ]

        Companies = [
            "sparkfun",
            "sparkfun",
            "arduino",
            "velleman",
            "seeedstudio",
            "make.co",
            "canakit",
            "canakit",
            "farnell",
            "farnell",
            "farnell",
            "farnell",
            "farnell",
            "farnell",
            "farnell",
            "farnell"
            ]
            



        for company, urlpage in zip(Companies, urls):
            #add page numbers to the blog/news site
            yield scrapy.Request(url=urlpage, callback=self.parse, cb_kwargs=dict(company=company))


    #Kelly Added to skim through all the web addresses that are actual articles only
    def initialpass(self, response):
        #Not used this go around

        return "good to go"


    def parse(self, response, company):
        # first part: save each page html to wikipages directory
        #print(len(response.url.split("/")[-1]))
        #print(response.url.split("/")[-2])
        if len(response.url.split("/")[-1]):
            subpage = response.url.split("/")[-1]
        else:
            subpage = response.url.split("/")[-2]

        #Go to the last entry pulled this will we the "Name"
        page = response.url.replace("/", ".")

        #Save the page for later use
        page_dirname = 'main-companies'
        filename = '%s.html' % page
        with open(os.path.join(page_dirname,filename), 'wb') as f:
            f.write(response.body)
        self.log('Saved file %s' % filename) 

        # second part: extract text for the item for document corpus
        item = WebfocusedcrawlItem()
        item['infourl'] = response.url
        item['entity'] = company
        item['entitytype'] = "Competitor"
        
        #Grab All the paragraph tags on the page
        item['text'] = response.xpath('//p//text()').extract()
        item['attributeinfo'] = {'subpageName': subpage}
        
        return item 
