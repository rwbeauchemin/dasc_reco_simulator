import streamlit as st
from utils import title_link, fetch_poster


def initialize_title_widget(cfg, title_number):
    """Start an empty set of columns and give the title

    Args:
        cfg (dict): The config dictionary object with title and description
        title_number (int): The number of titles to show in the UI

    Returns:
        st.columns: A streamlit columns object with empty contents
    """
    with st.expander(cfg["title"]):
        st.markdown(cfg["description"])

    title_cols = st.columns(title_number)
    for c in title_cols:
        with c:
            st.empty()

    return title_cols


def show_recommended_title_info(recommended_titles, title_cols, show_score):
    """Fills out the contents of the empty streamlit columns in the app

    Args:
        recommended_titles (pd.DataFrame): A set of recommendations to show
        title_cols (st.columns): A streamlit columns object with empty contents
        show_score (bool): Whether or not to show the score on the UI.
    """
    title_ids = recommended_titles["movieId"]
    title_titles = recommended_titles["title"]
    title_scores = recommended_titles["score"]
    posters = [fetch_poster(i) for i in title_ids]
    links = [title_link(i) for i in title_ids]
    for c, t, s, p, l in zip(title_cols, title_titles, title_scores, posters, links):
        with c:
            st.markdown(f"<a style='display: block; text-align: center;' href='{l}'>{t}</a>",
                        unsafe_allow_html=True)
            st.image(p)
            if show_score:
                st.write(round(s, 3))
