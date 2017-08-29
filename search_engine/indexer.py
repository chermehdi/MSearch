from elasticsearch import *


class Indexer:
    def __init__(self):
        self.connection = None  # elastic connection
        self.dict = {}

    def index(self, body, link):
        html = body
        h1 = html.find_all('h1')
        h2 = html.find_all('h2')
        h3 = html.find_all('h3')
        h4 = html.find_all('h4')
        self.extract_info(h1, link)
        self.extract_info(h2, link)
        self.extract_info(h3, link)
        self.extract_info(h4, link)

    def extract_info(self, h1, link):
        h1 = map(lambda x: x.text, h1)
        if len(h1) == 0: return
        tokenized_link = self.tokenize(h1)
        print('{} length {}'.format(tokenized_link, len(tokenized_link)))
        if len(tokenized_link) == 0: return
        for header in tokenized_link:
            if header not in self.dict:
                self.dict[header] = set()
            self.dict[header].add(link)

    def tokenize(self, txt):
        txt = str(txt)
        return map(lambda x: x.strip(), filter(lambda x: len(x.strip()) > 0, txt.split()))
