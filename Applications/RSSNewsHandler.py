import feedparser
import numpy as np
import yaml
import os


NEWS_DICT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'news_dict.yml')


class RSSNewsHandler:
    """Handles the BBC news rss feed"""

    def __init__(self, ):
        """Really only needs a url"""
        #self.news_url = "http://feeds.bbci.co.uk/news/rss.xml?edition=int"
        with open(NEWS_DICT_FILE, 'r') as stream:
            try:
                self.news_dict = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)


    @staticmethod
    def get_news_feed(site_url):
        """Get full news feed from the BBC rss"""
        return feedparser.parse(site_url)

    def get_news_entries(self, site_url):
        """Get only news entries of the BBC rss"""
        news_feed = self.get_news_feed(site_url)
        return news_feed.entries

    def get_random_news(self, news_site):
        """Get one random news article from the BBC rss"""
        site_url = self.news_dict.get(news_site, 'bbc')
        entries = self.get_news_entries(site_url)
        news_ind = np.random.randint(0, len(entries))
        return entries[news_ind]


if __name__ == '__main__':
    rnh = RSSNewsHandler()
    news = rnh.get_random_news('fotbollskanalen')
    test = feedparser.parse("https://www.fotbollskanalen.se/rss/")
    print "pen"
