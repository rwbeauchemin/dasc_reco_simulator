import scipy
import pickle
from sklearn.metrics.pairwise import linear_kernel, cosine_similarity
from utils import get_recommendations


def score_based_recommendations(title_number):
    """Select the top `title_number` titles given pre-calculated scores

    Args:
        title_number (int): The number of titles to select and display

    Returns:
        pd.DataFrame: A DataFrame with the title ID, the name, and scores.
    """
    with open('frontend/mock_data/title_scores.pickle', 'rb') as f:
        titles = pickle.load(f)
    titles = titles.head(title_number)
    titles = titles[["id", "title", "score"]]
    titles.columns = ["movieId", "title", "score"]
    return titles


def content_based_kernel_recommendations(metadata, titles, title_number):
    """Create recommendations from a linear kernel function on top of a
    pre-run TF-IDF for all titles

    Args:
        metadata (pd.DataFrame): A dataframe containing title metadata
        titles (list): A list of titles from a simualted user history
        title_number (int): The number of recommendations to bring back

    Returns:
        pd.DataFrame: A DataFrame with the title ID, the name, and scores.
    """
    tfidf_matrix = scipy.sparse.load_npz('frontend/mock_data/tfidf_matrix.npz')
    cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)
    return get_recommendations(metadata, titles, cosine_sim, title_number)


def content_based_cosine_recommendations(metadata, titles, title_number):
    """Create recommendations from a cosine similarity function on top of a
    pre-run count matrix for all titles

    Args:
        metadata (pd.DataFrame): A dataframe containing title metadata
        titles (list): A list of titles from a simualted user history
        title_number (int): The number of recommendations to bring back

    Returns:
        pd.DataFrame: A DataFrame with the title ID, the name, and scores.
    """
    count_matrix = scipy.sparse.load_npz("frontend/mock_data/count_matrix.npz")
    cosine_sim = cosine_similarity(count_matrix, count_matrix)
    return get_recommendations(metadata, titles, cosine_sim, title_number)
