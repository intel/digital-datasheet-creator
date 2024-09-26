from urllib.parse import urljoin
from urllib.request import urlopen
from bs4 import BeautifulSoup
from edatasheets_creator.logger.exceptionlogger import ExceptionLogger
from contextlib import closing


class Plugin:
    def __init__(self):
        pass

    def __del__(self):
        pass

    def process(self):
        try:
            pagelist = ["https://en.wikipedia.org/wiki/Python_%28programming_language%29"]
            urls = self.crawl(pagelist, depth=1)
            print(urls)
        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)

    def crawl(self, pages, depth=None):
        try:
            indexed_url = []  # a list for the main and sub-HTML websites in the main website
            for i in range(depth):
                for page in pages:
                    if page not in indexed_url:
                        indexed_url.append(page)
                        try:
                            with closing(urlopen(page)) as c:  # nosec
                                """ Bandit ignore warning reason
                                The page variable value is not an input of the system. Instead, the
                                possible value is specified in function process() as a hard coded URL.
                                For this reason the validation of file/ type of inputs it is not necessary
                                and the vulnerability described is not applicable to the system:
                                https://cwe.mitre.org/data/definitions/20.html
                                """
                                soup = BeautifulSoup.BeautifulStoneSoup(c.read())
                            # c = urlopen(page)
                        except Exception:
                            print("Could not open %s" % page)
                            continue
                        # soup = BeautifulSoup(c.read())
                        links = soup('a')  # finding all the sub_links
                        for link in links:
                            if 'href' in dict(link.attrs):
                                url = urljoin(page, link['href'])
                                if url.find("'") != -1:
                                    continue
                                url = url.split('#')[0]
                                if url[0:4] == 'http':
                                    indexed_url.append(url)
                pages = indexed_url
            return indexed_url

        except Exception as e:
            ExceptionLogger.logError(__name__, "", e)
