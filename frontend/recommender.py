import pandas as pd
import scipy
from sklearn.metrics.pairwise import linear_kernel, cosine_similarity
from utils import apply_shuffling


def get_recommendations(metadata, titles, cosine_sim, title_number, shuffle_mode=None):
    """In this function we find similarity score between titles

    Args:
        metadata (pd.DataFrame): The details for all titles
        titles (list): The list of titles a siumlated user has viewed
        cosine_sim (np.ndarray): A matrix of cosine similarities between titles
        title_number (int): The number of titles to pull back details for
        shuffle_mode (optional, str): (None, 'log', 'linear', 'exp') Adds shuffling
            to top `title_number` recommendations. Defaults to None (No shuffling)

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
                             reverse=True))

    title_indices = [i[0] for i in sim_scores]
    title_similarity = [i[1] for i in sim_scores]
    df = pd.DataFrame(
        zip(metadata['id'].iloc[title_indices],
            metadata['title'].iloc[title_indices],
            title_similarity),
        columns=["id", "title", "score"])

    df = apply_shuffling(df, title_number, shuffle_mode)
    return df

def score_based_recommendations(titles, title_number, shuffle_mode=None):
    """Select the top `title_number` titles given pre-calculated scores

    Args:
        titles (pd.DataFrame): The DataFrame containing ids, titles, and scores
        title_number (int): The number of titles to select and display
        shuffle_mode (optional, str): (None, 'log', 'linear', 'exp') Adds shuffling
            to top `title_number` recommendations. Defaults to None (No shuffling)

    Returns:
        pd.DataFrame: A DataFrame with the title ID, the name, and scores.
    """
    titles = apply_shuffling(titles, title_number, shuffle_mode)
    titles = titles[["id", "title", "score"]]
    return titles


def content_based_kernel_recommendations(metadata, titles, title_number, shuffle_mode=None):
    """Create recommendations from a linear kernel function on top of a
    pre-run TF-IDF for all titles

    Args:
        metadata (pd.DataFrame): A dataframe containing title metadata
        titles (list): A list of titles from a simualted user history
        title_number (int): The number of recommendations to bring back
        shuffle_mode (optional, str): (None, 'log', 'linear', 'exp') Adds shuffling
            to top `title_number` recommendations. Defaults to None (No shuffling)

    Returns:
        pd.DataFrame: A DataFrame with the title ID, the name, and scores.
    """
    tfidf_matrix = scipy.sparse.load_npz('frontend/mock_data/tfidf_matrix_peacock.npz')
    # Can also try with cosine_similarity if L2 Normalized (Rows currently do not sum to 1)
    cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)
    return get_recommendations(metadata, titles, cosine_sim, title_number, shuffle_mode)


def content_based_cosine_recommendations(metadata, titles, title_number, shuffle_mode=None):
    """Create recommendations from a cosine similarity function on top of a
    pre-run count matrix for all titles

    Args:
        metadata (pd.DataFrame): A dataframe containing title metadata
        titles (list): A list of titles from a simualted user history
        title_number (int): The number of recommendations to bring back
        shuffle_mode (optional, str): (None, 'log', 'linear', 'exp') Adds shuffling
            to top `title_number` recommendations. Defaults to None (No shuffling)

    Returns:
        pd.DataFrame: A DataFrame with the title ID, the name, and scores.
    """
    count_matrix = scipy.sparse.load_npz("frontend/mock_data/count_matrix.npz")
    cosine_sim = cosine_similarity(count_matrix, count_matrix)
    return get_recommendations(metadata, titles, cosine_sim, title_number, shuffle_mode)
