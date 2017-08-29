from flask import Flask

from search_engine import crawler

app = Flask(__name__)

c = crawler.Crawler()


@app.route('/')
def hello_world():
    ret = c.start_crawling('https://google.com')
    return ret


if __name__ == '__main__':
    app.run()
