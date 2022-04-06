import pickle
import streamlit as st
# import streamlit.components.v1 as components
from recommender import (
    score_based_recommendations,
    content_based_cosine_recommendations,
    content_based_kernel_recommendations)
from config import score_based_cfg, content_based_cosine_cfg, content_based_kernel_cfg
from widgets import initialize_title_widget, show_recommended_title_info
import sys
import os
sys.path.insert(0, os.path.abspath(__file__ + '/../..'))
from frontend import TITLE_NUMBER


st.set_page_config(
    page_title="Peachick QA Tool",
    page_icon="🐥",
    layout="wide")

st.title('Peachick: A Recommendations QA Tool')

# Style Changes
with open('frontend/style.css') as f:
    st.markdown(
        f'<style>{f.read()}</style>',
        unsafe_allow_html=True)

# Load Titles
with open('frontend/mock_data/title_df.pickle', 'rb') as f:
    metadata = pickle.load(f)

# Add Viewed Title Selector
main_layout, search_layout = st.columns([10, 1])
options = main_layout.multiselect(
    'Select Viewed Titles:',
    metadata["title"].unique())
show_recommended_titles_btn = search_layout.button("Build")

# Add Sidebar Widgets
recommended_title_num = st.sidebar.slider(
    "Titles Per Rail:",
    min_value=5,
    max_value=10,
    value=TITLE_NUMBER)
show_score = st.sidebar.checkbox("Show Score")

# Initialize Title Widgets
col_for_score_based = initialize_title_widget(
    score_based_cfg,
    recommended_title_num)
col_for_content_based = initialize_title_widget(
    content_based_cosine_cfg,
    recommended_title_num)
col_for_content_based_extra = initialize_title_widget(
    content_based_kernel_cfg,
    recommended_title_num)

# Show Static Recommendations (Score-Based)
score_based_recommended_titles = score_based_recommendations(recommended_title_num)
show_recommended_title_info(
    score_based_recommended_titles,
    col_for_score_based,
    show_score)

# Show Dynamic Recommendations (Content-Based)
if show_recommended_titles_btn:
    content_based_recommended_titles = content_based_cosine_recommendations(
        metadata,
        options,
        recommended_title_num)
    show_recommended_title_info(
        content_based_recommended_titles,
        col_for_content_based,
        show_score)

    content_extra_based_recommended_titles = content_based_kernel_recommendations(
        metadata,
        options,
        recommended_title_num)
    show_recommended_title_info(
        content_extra_based_recommended_titles,
        col_for_content_based_extra,
        show_score)
