import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import plotly.express as px
import os
import base64
from PIL import Image
from keboola_streamlit import KeboolaStreamlit
from wordcloud import WordCloud

# Constants
PROJECT = 'keboola-ai'
LOCATION = 'us-central1'
IMAGE_PATH = os.path.dirname(os.path.abspath(__file__))
KEBOOLA_LOGO_PATH = os.path.join(IMAGE_PATH, "static/keboola_logo.png")
LONDON_EYE_WC_PATH = os.path.join(IMAGE_PATH, "static/london_eye_wc.png")

# Streamlit Configurations
st.set_page_config(layout='wide')
# Try to get credentials from environment variables
STORAGE_API_TOKEN = os.environ.get('KBC_TOKEN', None)
KEBOOLA_HOSTNAME = os.environ.get('KBC_URL', None)

if not STORAGE_API_TOKEN or not KEBOOLA_HOSTNAME:
    # Fall back to Streamlit secrets if environment variables are not available
    STORAGE_API_TOKEN = st.secrets['KBC_TOKEN']
    KEBOOLA_HOSTNAME = st.secrets['KBC_URL']

keboola = KeboolaStreamlit(KEBOOLA_HOSTNAME, STORAGE_API_TOKEN)

# Load Data with Caching
@st.cache_data
def read_data(table_name):
    return keboola.read_table(table_name)

# Helper Functions
def color_for_value(value):
    if value < -0.2:
        return '#EA4335'  # Negative
    elif -0.2 <= value <= 0.2:
        return '#FBBC05'  # Neutral
    return '#34A853'  # Positive

def sentiment_color(sentiment):
    return {
        "Positive": "color: #34A853",
        "Neutral": "color: #FBBC05",
        "Negative": "color: #EA4335"
    }.get(sentiment, "color: black")

def generate_wordcloud(word_freq, mask_image_path):
    colormap = mcolors.ListedColormap(['#4285F4', '#34A853', '#FBBC05', '#EA4335'])
    mask_image = np.array(Image.open(mask_image_path)).astype(np.uint8)
    wordcloud = WordCloud(width=300, height=300, background_color=None, colormap=colormap, mask=mask_image, mode='RGBA')
    return wordcloud.generate_from_frequencies(word_freq)

# Display Logo
logo_html = f'<div style="display: flex; justify-content: flex-end;"><img src="data:image/png;base64,{base64.b64encode(open(KEBOOLA_LOGO_PATH, "rb").read()).decode()}" style="width: 200px; margin-bottom: 10px;"></div>'
st.markdown(f"{logo_html}", unsafe_allow_html=True)

# Title
st.title('London Eye Reviews Sentiment Analysis')

# Load Data
data = read_data('out.c-reviews-data-cleaning.reviews_parsed')
data['parsed_date'] = pd.to_datetime(data['parsed_date'], format='mixed').dt.tz_localize(None)
data['date'] = data['parsed_date'].dt.date

keywords = read_data('out.c-reviews-data-cleaning.keyword_counts')
keywords['parsed_date'] = pd.to_datetime(keywords['parsed_date'], format='mixed').dt.tz_localize(None)
keywords['date'] = keywords['parsed_date'].dt.date
keywords_filtered = keywords[~keywords['keywords'].isin(['London', 'London Eye'])]

# Filters Section
st.markdown("<br>__Filters__", unsafe_allow_html=True)
col1, col2 = st.columns(2, gap='medium')
st.markdown("<br>", unsafe_allow_html=True)

with col1:
    min_score, max_score = st.slider(
        'Select a range for the sentiment score:',
        min_value=-1.0, max_value=1.0, value=(-1.0, 1.0),
        key="sentiment_slider"
    )

with col2:
    min_date, max_date = data['parsed_date'].min(), data['parsed_date'].max()
    date_range = st.date_input("Select a date range:", (min_date, max_date), min_value=min_date, max_value=max_date)

# Apply Filters
if len(date_range) == 2:
    start_date, end_date = date_range
    data = data[(data['parsed_date'] >= pd.to_datetime(start_date)) & (data['parsed_date'] <= pd.to_datetime(end_date))]
    keywords_filtered = keywords_filtered[(keywords_filtered['parsed_date'] >= pd.to_datetime(start_date)) & (keywords_filtered['parsed_date'] <= pd.to_datetime(end_date))]
    filtered_data = data[(data['sentiment'] >= min_score) & (data['sentiment'] <= max_score)]
    keywords_filtered = keywords_filtered[(keywords_filtered['sentiment'] >= min_score) & (keywords_filtered['sentiment'] <= max_score)]
else:
    st.info("Please select both start and end dates.")
    st.stop()
    
# Visualization Section
col1, col2 = st.columns(2, gap='medium')

with col1:
    filtered_data['color'] = filtered_data['sentiment'].apply(color_for_value)
    fig = px.histogram(filtered_data, x='sentiment', nbins=21, title='Sentiment Score Distribution', color='color', color_discrete_map='identity')
    fig.update_layout(bargap=0.1, xaxis_title='Sentiment Score', yaxis_title='Count')
    st.plotly_chart(fig, use_container_width=True)

with col2:
    keyword_counts = keywords_filtered.groupby('keywords')['counts'].sum().reset_index().sort_values(by='counts', ascending=True).tail(10)
    fig = px.bar(keyword_counts, x='counts', y='keywords', orientation='h', title='Top 10 Keywords by Count', color_discrete_sequence=['#4285F4'])
    fig.update_layout(xaxis_title='Count', yaxis_title='Keywords')
    st.plotly_chart(fig, use_container_width=True)

# Data Table and Word Cloud Section
st.markdown("<br>", unsafe_allow_html=True)
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("__Data__")
    sorted_data = filtered_data.sort_values(by='parsed_date', ascending=False)
    st.data_editor(
        sorted_data[['sentiment_category', 'text_in_english', 'stars', 'reviewSource', 'date', 'url']].style.map(sentiment_color, subset=["sentiment_category"]),
        column_config={
            'sentiment_category': 'Sentiment Category',
            'text_in_english': 'Text',
            'stars': 'Rating',
            'reviewSource': 'Review Source',
            'date': 'Date',
            'url': st.column_config.LinkColumn('URL')
        },
        height=1000, disabled=['sentiment_category', 'text_in_english', 'stars', 'reviewSource', 'date', 'url'],
        use_container_width=True, hide_index=True
    )

with col2:
    st.markdown("__Word Eye__")
    word_freq = dict(zip(keywords_filtered['keywords'], keywords_filtered['counts']))
    if word_freq:
        wordcloud = generate_wordcloud(word_freq, LONDON_EYE_WC_PATH)
        fig, ax = plt.subplots(figsize=(5, 5), frameon=False)  # Smaller size for alignment
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        st.pyplot(fig, use_container_width=True)
    else:
        st.info("No keywords found to generate the word cloud.")