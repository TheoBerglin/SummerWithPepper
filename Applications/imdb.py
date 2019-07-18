import random
import pandas as pd
import dask.dataframe as dd
from omdb import OMDBClient


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
        movie_desc = movie_data['plot']
        movie_poster_url = movie_data['poster']
        movie_rating = movie_data['imdb_rating']
        movie_genre = movie_data['genre']
        print movie_desc

    def get_api_data(self, movie_id):
        client = OMDBClient(apikey=self.api_key)
        movie_info = client.get(imdbid=movie_id)
        return movie_info


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

