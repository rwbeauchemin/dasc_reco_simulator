import random
import math
import pandas as pd
import pickle
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
import scipy.sparse


def refetch_data():
    """Refetch and store data from BigQuery
    """
    # TODO: Connect this query to bigquery from here
    query = r"""
SELECT id,
    COALESCE(title, "") as title,
    COALESCE(genre_family, "") as genre_family,
    COALESCE(segments, "") as segments,
    COALESCE(genre, "") as genre,
    COALESCE(lang, "") as lang,
    COALESCE(runtime_minutes, 1) as runtime_minutes,
    COALESCE(min_production_year, 0) as min_production_year,
    COALESCE(max_production_year, 0) as max_production_year,
    COALESCE(tags, "") as tags,
    COALESCE(show_recap, "") as show_recap,
    COALESCE(synopsis, "") as synopsis,
    COALESCE(popularity, 0) as popularity
FROM (
    SELECT  COALESCE(SeriesUuid, ProgrammeUuid) AS id,
            MAX(COALESCE(DQ_Title, LQ_Title)) as title,
            MAX(CASE
                WHEN ContentType = "MOVIE" THEN "MOVIES"
                WHEN ContentType = "SERIES" THEN "TV"
                WHEN ContentType = "PROGRAMME"
                AND UPPER(COALESCE(DQ_SeriesGenre, DQ_ProgrammeGenre)) = "TV"
                THEN "TV"
                WHEN ContentType = "PROGRAMME"
                AND UPPER(COALESCE(DQ_SeriesGenre, DQ_ProgrammeGenre)) = "MOVIES"
                THEN "MOVIES"
                WHEN ContentType = "PROGRAMME"
                AND UPPER(COALESCE(DQ_SeriesGenre, DQ_ProgrammeGenre)) LIKE "%NEWS%"
                THEN "NEWS"
                END) as genre_family,
            MAX(VQ_ContentSegments) as segments,
            MAX(COALESCE(DQ_SeriesSubGenre, DQ_ProgrammeSubGenre)) as genre,
            MAX(COALESCE(DQ_Language, VQ_Language)) as lang,
            SUM(COALESCE(VQ_ContentDurationMilliseconds,0)/60000.0) as runtime_minutes,
            MIN(VQ_ProductionYear) as min_production_year,
            MAX(VQ_ProductionYear) as max_production_year,
            MAX(CONCAT(DQ_ProgrammeTags, "|", DQ_SeasonTags, "|", DQ_SeriesTags)) as tags,
            STRING_AGG(COALESCE(
                DQ_TitleLongSynopsis, VQ_TitleLongSynopsis, DQ_SeriesMediumSynopsis,
                VQ_SeriesMediumSynopsis, DQ_SeriesShortSynopsis, VQ_SeriesShortSynopsis),
                " " ORDER BY VQ_SeasonNumber asc, VQ_EpisodeNumber asc) as show_recap,
            MAX(COALESCE(
                DQ_SeriesLongSynopsis, VQ_SeriesLongSynopsis, DQ_TitleLongSynopsis,
                VQ_TitleLongSynopsis, DQ_SeriesMediumSynopsis, VQ_SeriesMediumSynopsis,
                DQ_SeriesShortSynopsis, VQ_SeriesShortSynopsis)) as synopsis
    FROM `nbcu-sdp-prod-003.sdp_persistent_views.VqDqLqContentMetadataView`
    WHERE (
            UPPER(ContentType) IN ("MOVIE", "SERIES")
            OR (UPPER(ContentType) = "PROGRAMME"
                AND UPPER(COALESCE(DQ_SeriesGenre, DQ_ProgrammeGenre)) IN ("TV", "MOVIES")
            )
        )
    AND VQ_Title NOT LIKE "%(Trailer)%"
    AND COALESCE(DQ_Title, LQ_Title) IS NOT NULL
    GROUP BY COALESCE(SeriesUuid, ProgrammeUuid)
) a
LEFT JOIN (
    SELECT content_id, max(popularity) AS popularity
    FROM `nbcu-ds-sandbox-b-001.ncr_lightyear.popularity_sampling_statistics`
    GROUP BY content_id
) b
ON a.id = b.content_id
WHERE runtime_minutes > 10.0
AND genre NOT IN ("Talk", "News")
AND genre NOT LIKE "%Entertainment%"
;
    """
    print(query)
    df = pd.read_csv('title_metadata.csv')
    df['genre'].fillna('', inplace=True)
    df['synopsis'].fillna('', inplace=True)
    df['score'] = df['popularity'] / df['runtime_minutes']
    # Add some uniqueness for duplicate names
    dupes = df[df['title'].isin(df['title'][df['title'].duplicated()])].index
    df.loc[dupes, 'title'] = df.loc[dupes, 'title'] + ' (' + \
        df.loc[dupes, 'max_production_year'].astype(int).astype(str) + ', ' + \
        df.loc[dupes, 'genre_family'] + ')'
    # The rest are true duplicates, so add index to differentiate
    dupes = df[df['title'].isin(df['title'][df['title'].duplicated()])].index
    df.loc[dupes, 'title'] = df.loc[dupes, 'title'] + ' Dupe ' + \
        df.loc[dupes, 'title'].index.astype(str)
    # Calculate score
    df.sort_values('score', axis=0, ascending=False, inplace=True)
    df.reset_index(inplace=True, drop=True)
    # Store table for use in the app
    with open('title_metadata.pkl', 'wb') as fi:
        pickle.dump(df, fi)
    # Run TFIDF on synopsis data
    df['text_aggregated'] = df['title'] + ' ' + \
        df['genre'].apply(lambda x: ' '.join(' '.join(x.split('|')).split(' & '))) + ' ' + \
        df['synopsis']
    vectorizer = TfidfVectorizer(
        stop_words=stopwords.words('english'),
        ngram_range=(1, 2))
    data_vector = vectorizer.fit_transform(df['text_aggregated'])
    scipy.sparse.save_npz('tfidf_matrix_peacock.npz', data_vector)
    return

def title_link(title_id):
    """(Deprecated) Creates a link to view more details on a title given an id

    Args:
        title_id (Any): The id to look up with

    Returns:
        str: The link to get more details on the title
    """
    # TODO: Find a good landing page to learn more about Peacock titles
    return f"https://www.themoviedb.org/movie/{title_id}"


def fetch_poster(title_id):
    """Creates a link to see an image of the title given an id

    Args:
        title_id (Any): The id to look up with

    Returns:
        str: The link to an image of the title
    """
    return (
        'https://imageservice.disco.peacocktv.com/uuid/'
        f'{title_id}/TITLE_ART_16_9/400'
        '?territory=US&proposition=NBCUOTT&language=eng')

def apply_shuffling(titles, title_number, shuffle_mode=None):
    """Shuffles using shuffling functions found in this utililty file.

    Args:
        titles (pd.Dataframe): A dataframe to apply shuffling to
        title_number (int): The number of titles to return
        shuffle_mode (str, optional): The type of . Defaults to None.

    Returns:
        pd.DataFrame: The dataframe with shuffling and truncation applied
    """
    if shuffle_mode is None or shuffle_mode == 'None':
        titles = titles.head(title_number)
    elif shuffle_mode == 'linear':
        indices = linear_rising_temperature(list(titles.index), break_at=title_number)
        titles = titles.loc[indices]
    elif shuffle_mode == 'log':
        indices = log_rising_temperature(list(titles.index), break_at=title_number)
        titles = titles.loc[indices]
    elif shuffle_mode == 'exp':
        indices = exponential_rising_temperature(list(titles.index), break_at=title_number)
        titles = titles.loc[indices]
    return titles


def exponential_rising_temperature(sorted_list: list,
                                   init_group: int = 4,
                                   break_at: int = 12):
    final_list = []
    group = init_group * 1
    for i in range(len(sorted_list)):
        selection = random.choice(sorted_list[:group])
        sorted_list.remove(selection)
        final_list.append(selection)
        group *= 2
        if i + 1 == break_at:
            break
    return final_list


def linear_rising_temperature(sorted_list: list,
                              init_temperature: int = 2,
                              break_at: int = 12):
    final_list = []
    temperature = init_temperature * 1
    for i in range(len(sorted_list)):
        selection = random.choice(sorted_list[:temperature])
        sorted_list.remove(selection)
        final_list.append(selection)
        temperature = (init_temperature + i) * 2
        if i + 1 == break_at:
            break
    return final_list


def log_rising_temperature(sorted_list: list,
                           init_temperature: int = 2,
                           break_at: int = 12):
    final_list = []
    temperature = init_temperature * 1
    for i in range(len(sorted_list)):
        selection = random.choice(sorted_list[:temperature])
        sorted_list.remove(selection)
        final_list.append(selection)
        temperature = 2 * math.ceil(math.log(init_temperature + i)) + 1
        if i + 1 == break_at:
            break
    return final_list
