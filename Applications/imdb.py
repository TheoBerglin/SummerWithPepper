import random
import pandas as pd
import dask.dataframe as dd
from omdb import OMDBClient


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


def random_pop(df):
    nbr_vote_pop = 25000
    df_pop = df[df['numVotes'] > nbr_vote_pop]
    df_pop_sorted = df_pop.sort_values('averageRating', ascending=False)
    idx = random.randrange(500)  # Choose from the top 500
    id = df_pop_sorted.iloc[idx]['tconst']
    get_api_data(id)


def get_api_data(movie_id):
    api_key = '303b365e'
    client = OMDBClient(apikey=api_key)
    hej = client.get(imdbid=movie_id)
    print hej


if __name__ == '__main__':
    df = pd.read_csv('../data/data_fixed.csv')

    random_pop(df)

    nbr_vote_pop = 25000

    nbr_vote_unknown = 1000
    df_unknown = df[df['numVotes'] < nbr_vote_pop]
    df_unknown = df_unknown[df_unknown['numVotes'] > nbr_vote_unknown]

