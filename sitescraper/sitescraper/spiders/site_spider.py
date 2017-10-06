import requests
from urllib.parse import urlparse
import scrapy
from scrapy.spiders import CrawlSpider
from scrapy.selector import Selector
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule, CrawlSpider

from sitescraper.items import SiteScraperItem

HANDLED_ERRORS = [404, 500] 
ACCOUNT_OWNER = "Robert Dayton"
SITE_NAME= "programmersball"
class SiteScraperSpider(CrawlSpider):
    name = "sitescraper"
    handle_httpstatus_list = HANDLED_ERRORS
    allowed_domains = ['programmersball.com']
    start_urls = [
        "http://programmersball.com",
    ]
    # This spider has one rule: extract all (unique and canonicalized) links, follow them and parse them using the parse_items method
    rules = [
        Rule(
            LinkExtractor(
                canonicalize=True,
                unique=True
            ),
            follow=True,
            callback="parse_links"
        )
    ]

    processed_external_links = []
    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.parse, dont_filter=True)

    def parse_links(self, response):
        links = LinkExtractor(canonicalize=True, unique=True).extract_links(response)
        items = []
        
        for link in links:
            item = SiteScraperItem()
            item['account_owner'] = ACCOUNT_OWNER
            item['domain'] = SITE_NAME
            item['page'] = response.url
            item['link_destination'] = link.url
            item['status'] = response.status
            item['external_link_status'] = None
            
            if ('http' in link.url 
                and urlparse(link.url).hostname not in self.allowed_domains
                and link.url not in self.processed_external_links
                ):
                try:
                    r = requests.head(link.url)
                    print(r.status_code)
                    # prints the int of the status code. Find more at httpstatusrappers.com :)
                except requests.ConnectionError:
                    print("failed to connect")
                self.processed_external_links.append(link.url)
                item['external_link_status'] = r.status_code
            items.append(item)

        return items