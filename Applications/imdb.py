import random
import pandas as pd
import dask.dataframe as dd
from omdb import OMDBClient
from bs4 import BeautifulSoup
import re
import urllib


class Imbd:

    def __init__(self):
        self.api_key = '303b365e'
        self.nbr_vote_pop = 25000
        self.df = pd.read_csv('data/data_fixed.csv')

    def random_pop(self):
        df_pop = self.df[self.df['numVotes'] > self.nbr_vote_pop]
        df_pop_sorted = df_pop.sort_values('averageRating', ascending=False)
        idx = random.randrange(500)  # Choose from the top 500
        id = df_pop_sorted.iloc[idx]['tconst']
        movie_data = self.get_api_data(id)
        self.create_movie_page(movie_data)

    def get_api_data(self, movie_id):
        client = OMDBClient(apikey=self.api_key)
        movie_info = client.get(imdbid=movie_id)
        return movie_info

    def create_movie_page(self, movie_info):
        movie_desc = movie_info['plot']
        movie_poster_url = movie_info['poster']
        urllib.urlretrieve(movie_poster_url, "pepper_html/imdb/images/movie_poster.jpg")
        movie_rating = movie_info['imdb_rating']
        movie_genre = movie_info['genre']
        movie_title = movie_info['title']
        movie_year = movie_info['year']

        # Get template file
        filehandle = open("pepper_html/imdb/movie_template.html")
        soup = BeautifulSoup(filehandle, 'html.parser')

        # Some ugly html coding
        images = soup.find_all('input')
        text_title = soup.find_all(id=re.compile('title'))
        text_genre = soup.find_all(id=re.compile('genre'))
        text_desc = soup.find_all(id=re.compile('desc'))
        text_rating = soup.find_all(id=re.compile('rating'))

        images[0]['src'] = 'movie_poster.jpg'
        text_title[0].string = movie_title + ', (' + movie_year + ')'
        text_genre[0].string = movie_genre
        text_desc[0].string = movie_desc
        text_rating[0].string = 'Rating: ' + movie_rating + ' / 10'

        # Save file
        with open("pepper_html/imdb/movie.html", "w") as file:
            file.write(str(soup.prettify()))


def parse_n_save_data():
    df_rating = pd.read_csv('../data/ratings.tsv', sep="\t")
    df_rating.set_index('tconst', inplace=True)

    df = dd.read_csv('../data/data.tsv', sep="\t",
                     usecols=['tconst', 'titleType', 'primaryTitle', 'originalTitle', 'genres'])
    df = df[df['titleType'] == 'movie']
    df = df.compute()
    df.set_index('tconst', inplace=True)

    df_merged = pd.concat([df, df_rating], axis=1, join='inner')  # Merge inner to avoid nans

    df_merged.drop('titleType', axis=1, inplace=True)  # Drop unnecessary column

    df_merged.to_csv('../data/data_fixed.csv')

