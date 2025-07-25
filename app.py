import os
import sys
import pickle
import streamlit as st
import numpy as np
import pandas as pd
from books_recommender.logger.log import logging
from books_recommender.config.configuration import AppConfiguration
from books_recommender.pipeline.training_pipeline import TrainingPipeline
from books_recommender.exception.exception_handler import AppException
import base64


# def add_bg_from_local(image_file):
#     with open(image_file, "rb") as image:
#         encoded_string = base64.b64encode(image.read()).decode()
#     css = f"""
#     <style>
#     .stApp {{
#         background-image: url("data:image/jpg;base64,{encoded_string}");
#         background-size: cover;
#         background-position: center;
#         background-repeat: no-repeat;
#         background-attachment: fixed;
#     }}
#     </style>
#     """
# st.markdown(css, unsafe_allow_html=True)


# add_bg_from_local(
#     r"./background.jpg")


class Recommendation:
    def __init__(self, app_config=AppConfiguration()):
        try:
            self.recommendation_config = app_config.get_recommendation_config()
        except Exception as e:
            raise AppException(e, sys) from e

    def fetch_poster(self, suggestion):
        try:
            book_name = []
            ids_index = []
            poster_url = []
            book_pivot = pickle.load(
                open(self.recommendation_config.book_pivot_serialized_objects, 'rb'))
            final_rating = pickle.load(
                open(self.recommendation_config.final_rating_serialized_objects, 'rb'))

            for book_id in suggestion:
                book_name.append(book_pivot.index[book_id])

            for name in book_name[0]:
                ids = np.where(final_rating['title'] == name)[0][0]
                ids_index.append(ids)

            for idx in ids_index:
                url = final_rating.iloc[idx]['image_url']
                poster_url.append(url)

            return poster_url

        except Exception as e:
            raise AppException(e, sys) from e

    def recommend_book(self, book_name):
        try:
            books_list = []
            model = pickle.load(
                open(self.recommendation_config.trained_model_path, 'rb'))
            book_pivot = pickle.load(
                open(self.recommendation_config.book_pivot_serialized_objects, 'rb'))
            book_id = np.where(book_pivot.index == book_name)[0][0]
            distance, suggestion = model.kneighbors(
                book_pivot.iloc[book_id, :].values.reshape(1, -1), n_neighbors=6)

            poster_url = self.fetch_poster(suggestion)

            for i in range(len(suggestion)):
                books = book_pivot.index[suggestion[i]]
                for j in books:
                    books_list.append(j)
            return books_list, poster_url

        except Exception as e:
            raise AppException(e, sys) from e

    def train_engine(self):
        try:
            obj = TrainingPipeline()
            obj.start_training_pipeline()
            st.text("Training Completed!")
            logging.info(f"Recommended successfully!")
        except Exception as e:
            raise AppException(e, sys) from e

    def recommendations_engine(self, selected_books):
        try:
            recommended_books, poster_url = self.recommend_book(selected_books)
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.text(recommended_books[1])
                st.image(poster_url[1])
            with col2:
                st.text(recommended_books[2])
                st.image(poster_url[2])

            with col3:
                st.text(recommended_books[3])
                st.image(poster_url[3])
            with col4:
                st.text(recommended_books[4])
                st.image(poster_url[4])
            with col5:
                st.text(recommended_books[5])
                st.image(poster_url[5])
        except Exception as e:
            raise AppException(e, sys) from e


if __name__ == "__main__":
    import streamlit as st
    import base64

    def add_bg_from_local(image_file):
        with open(image_file, "rb") as image:
            encoded_string = base64.b64encode(image.read()).decode()
        css = f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{encoded_string}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
            font-family: 'Segoe UI', sans-serif;
        }}
        .title {{
            font-size: 40px;
            text-align: center;
            color: black;
            text-shadow: 2px 2px 6px #000000;
            margin-top: 20px;
        }}
        .subtitle {{
            font-size: 18px;
            text-align: center;
            color: black;
            margin-bottom: 40px;
        }}
        .centered-box {{
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 20px 50px;
            background-color: rgba(255, 255, 255, 0.85);
            border-radius: 12px;
            max-width: 700px;
            margin: 0 auto;
        }}
        .custom-button {{
            width: 100%;
            padding: 10px;
            font-size: 16px;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 8px;
            align-items: center;
            justify-content: center;
        }}
        </style>
        """
        st.markdown(css, unsafe_allow_html=True)

    # Apply background
    # add_bg_from_local(
    #     r"./background.jpg")

    # Title and Subtitle
    st.markdown("<div class='title'> Book Recommender System</div>",
                unsafe_allow_html=True)

    obj = Recommendation()

    # Centered content box
    with st.container():
        # st.markdown("<div class='centered-box'>", unsafe_allow_html=True)

        if st.button(' Train Recommender System'):
            obj.train_engine()

        book_names = pickle.load(
            open(os.path.join('templates', 'book_names.pkl'), 'rb'))

        selected_books = st.selectbox(" Select a Book You Like", book_names)

        if st.button(' Show Recommendation'):
            obj.recommendations_engine(selected_books)

        st.markdown("</div>", unsafe_allow_html=True)
