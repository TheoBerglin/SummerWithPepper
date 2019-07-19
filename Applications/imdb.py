import random
import pandas as pd
import dask.dataframe as dd
from omdb import OMDBClient
from bs4 import BeautifulSoup
import re
import urllib
import sys


class Imbd:

    def __init__(self):
        self.api_key = '303b365e'
        self.nbr_vote_pop = 25000
        self.df = pd.read_csv('data/data_fixed.csv')
        self.movie_data = None
        reload(sys)
        sys.setdefaultencoding('utf-8')

    def random_pop(self):
        """ Find a random popular movie and create a page """
        df_pop_sorted = self.filter_popular(self.df)
        movie_id = self.get_random_movie(df_pop_sorted)
        self.get_api_data(movie_id)
        self.create_movie_page()

    def random_new_pop(self):
        """ Find a random new popular movie and create a page """
        df_new = self.filter_new(self.df)
        df_pop_new = self.filter_popular(df_new)
        movie_id = self.get_random_movie(df_pop_new)
        self.get_api_data(movie_id)
        self.create_movie_page()

    def get_random_movie(self, df_sorted):
        """
        Get a random movie id from the top 500

        :param df_sorted: sorted dataframe with top rated movie in first row
        :return: imdb id of the movie
        """
        idx = random.randrange(500)  # Choose from the top 500
        imdb_id = df_sorted.iloc[idx]['tconst']
        return imdb_id

    def filter_new(self, df):
        """
         Remove movies older than made 1990
        :return: sorted dataframe
        """
        df_new = df[df['startYear'] > 1990]
        return df_new

    def filter_popular(self, df):
        """
         Sort the df descending according to rating
        :return: sorted dataframe
        """
        df_pop = df[df['numVotes'] > self.nbr_vote_pop]
        df_pop_sorted = df_pop.sort_values('averageRating', ascending=False)
        return df_pop_sorted

    def get_api_data(self, movie_id):
        """
        Get API data for movie
        :param movie_id: imdb id
        """
        client = OMDBClient(apikey=self.api_key)
        movie_info = client.get(imdbid=movie_id)

        # Download and store poster
        movie_poster_url = movie_info['poster']
        urllib.urlretrieve(movie_poster_url, "pepper_html/imdb/images/movie_poster.jpg")
        self.movie_data = movie_info

    def create_movie_page(self):
        """
        Create an html movie page
        """
        # Get template file
        filehandle = open("pepper_html/imdb/movie_template.html")
        soup = BeautifulSoup(filehandle, 'html.parser')

        # Some ugly html coding
        images = soup.find_all('input')
        text_title = soup.find_all(id=re.compile('title'))
        text_runtime = soup.find_all(id=re.compile('runtime'))
        text_genre = soup.find_all(id=re.compile('genre'))
        text_director = soup.find_all(id=re.compile('director'))
        text_plot = soup.find_all(id=re.compile('desc'))
        text_rating = soup.find_all(id=re.compile('rating'))

        images[0]['src'] = 'movie_poster.jpg'

        text_title[0].string = self.movie_data['title'] + ' (' + self.movie_data['year'] + ')'

        runtime_tag = soup.new_tag("b")
        runtime_tag.string = 'Runtime: '
        text_runtime[0].string = self.movie_data['runtime']
        text_runtime[0].string.insert_before(runtime_tag)

        genre_tag = soup.new_tag("b")
        genre_tag.string = 'Genre: '
        text_genre[0].string = self.movie_data['genre']
        text_genre[0].string.insert_before(genre_tag)

        director_tag = soup.new_tag("b")
        director_tag.string = 'Director: '
        text_director[0].string = self.movie_data['director']
        text_director[0].string.insert_before(director_tag)

        plot_tag = soup.new_tag("b")
        plot_tag.string = 'Plot: '
        text_plot[0].string = self.movie_data['plot']
        text_plot[0].string.insert_before(plot_tag)

        text_rating[0].string = 'Rating: ' + self.movie_data['imdb_rating'] + ' / 10'

        # Save file
        with open("pepper_html/imdb/movie.html", "w") as file:
            file.write(str(soup.prettify()))


def parse_n_save_data():
    df_rating = pd.read_csv('data/ratings.tsv', sep="\t")
    df_rating.set_index('tconst', inplace=True)

    df = dd.read_csv('data/data.tsv', sep="\t",
                     usecols=['tconst', 'titleType', 'primaryTitle', 'originalTitle', 'genres', 'startYear'], dtype={'startYear': 'object'})
    df = df[df['titleType'] == 'movie']
    df = df[df['startYear'] != '']
    df = df[df['startYear'] != '\N']
    df = df.compute()
    df.set_index('tconst', inplace=True)

    df_merged = pd.concat([df, df_rating], axis=1, join='inner')  # Merge inner to avoid nans

    df_merged.drop('titleType', axis=1, inplace=True)  # Drop unnecessary column

    df_merged.to_csv('data/data_fixed.csv')

