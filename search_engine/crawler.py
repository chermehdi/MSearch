from urllib import urlopen
import bs4 as bs
from search_engine.indexer import Indexer


## the visited set should be changed to a more persistant datastruct that's easy
## to access : i will use redis for prod


class Crawler:
    def __init__(self, depth=1):
        self.depth = depth
        self.visited = set()
        self.stack = []
        self.indexer = Indexer()

    def start_crawling(self, start_link, parent=None, current_depth=0):
        if start_link in self.visited: return
        print('visiting {} parent {}'.format(start_link, parent))
        self.visited.add(start_link)
        if current_depth > self.depth:
            return
        start_link = self.transform_local(start_link, self.get_root(parent))
        try:
            s = urlopen(start_link).read()
            soup = bs.BeautifulSoup(s, 'html5lib')
            self.indexer.index(soup, start_link)
        except IOError:
            return
        links = soup.find_all('a')
        for link in links:
            link_value = link.get('href')
            link_value = self.transform_local(link_value, self.get_root(start_link))
            self.start_crawling(link_value, start_link, current_depth + 1)

        return self.visited

    def get_root(self, link):
        if not link: return ''
        if link.startswith('https'):
            first_slash = link[8:].find('/')
            if first_slash >= 0:
                return link[:8 + first_slash]
            else:
                return link

        if link.startswith('http'):
            first_slash = link[7:].find('/')
            if first_slash >= 0:
                return link[:7 + first_slash]
            else:
                return link

        first_slash = link.find('/')
        if first_slash >= 0:
            return link[:first_slash]
        else:
            return link

    def transform_local(self, link_value, parent_link):
        """
            this function sanitizes the url passed, ignores urls starting with ., and do resolve relative urls
        """
        if (not link_value) or (link_value == '/') or (link_value[0] == '.') or link_value.find('#') >= 0:
            return parent_link
        link_value = str(link_value)
        if link_value[0] != '/':
            return link_value
        if not parent_link:
            return link_value
        parent_link = str(parent_link)
        if parent_link[len(parent_link) - 1] == '/':
            parent_link = parent_link[:len(parent_link) - 1]
        final_value = parent_link + link_value
        hash = final_value.find('#')
        if hash != - 1:
            final_value = final_value[:final_value.find('#')]
        return final_value


if __name__ == '__main__':
    c = Crawler(depth=4)
    c.start_crawling('https://en.wikipedia.org/wiki/Square_root')
    keys = list(c.indexer.dict.keys())
    for key in keys:
        print('{}   {}'.format(key.strip(), c.indexer.dict[key]))
