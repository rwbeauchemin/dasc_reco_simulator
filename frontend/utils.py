import pandas as pd
import requests


def title_link(title_id):
    """Creates a link to view more details on a title given an id

    Args:
        title_id (Any): The id to look up with

    Returns:
        str: The link to get more details on the title
    """
    return f"https://www.themoviedb.org/movie/{title_id}"


def fetch_poster(title_id):
    """Creates a link to see an image of the title given an id

    Args:
        title_id (Any): The id to look up with

    Returns:
        str: The link to an image of the title
    """
    url = (f"https://api.themoviedb.org/3/movie/{title_id}"
           "?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US")
    data = requests.get(url)
    data = data.json()
    poster_path = data['poster_path']
    full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
    return full_path


def get_recommendations(metadata, titles, cosine_sim, title_number):
    """In this function we find similarity score between titles

    Args:
        metadata (pd.DataFrame): The details for all titles
        titles (list): The list of titles a siumlated user has viewed
        cosine_sim (np.ndarray): A matrix of cosine similarities between titles
        title_number (int): The number of titles to pull back details for

    Returns:
        pd.DataFrame: The dataframe with recommended titles, names, and scores
    """
    indices = pd.Series(metadata.index, index=metadata['title']).drop_duplicates()
    idx = {indices[t] for t in titles}
    sim_scores = dict()
    for title_idx in idx:
        sim = cosine_sim[title_idx]
        for i, s in enumerate(sim):
            sim_scores[i] = s if s > sim_scores.get(i, 0) else sim_scores.get(i, 0)

    for i in idx:
        del sim_scores[i]

    sim_scores = list(sorted(sim_scores.items(),
                             key=lambda item: item[1],
                             reverse=True))[:title_number]

    title_indices = [i[0] for i in sim_scores]
    title_similarity = [i[1] for i in sim_scores]
    return pd.DataFrame(zip(metadata['id'].iloc[title_indices],
                            metadata['title'].iloc[title_indices],
                            title_similarity),
                        columns=["movieId", "title", "score"])
