import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import imdb
from PIL import Image
import requests
from sklearn.metrics.pairwise import cosine_similarity
movied=pd.read_csv('movies.csv')

st.title('WBSFLIX')
option = st.sidebar.multiselect('Do you want to see top 5 movies in WEBFLIX?', ['Yes', 'No'])
st.sidebar.subheader('Movie options')
movie_title1 = st.sidebar.selectbox('Select movie title:', movied['title'].unique.tolist())
number= st.sidebar.text_input('Select number of reccomendation:')
user_id = st.sidebar.text_input('Write user ID:')
user_id=int(user_id) if user_id.isdigit() else 0
number= int(number) if number.isdigit() else 0

ia = imdb.IMDb()


st.write(option)
def five_top(): 
    if option==['Yes']:
        movied=pd.read_csv('movies.csv')
        ratings = pd.read_csv('ratings.csv')
        links = pd.read_csv('links.csv')
        tags = pd.read_csv('tags.csv')
        rating=ratings.groupby('movieId')['rating'].mean()
        mov_rat=movied.merge(ratings, how='left', on='movieId')
        mov_lin = movied.merge(links, on='movieId')
        mov__lin_rat = mov_lin.merge(rating, on = 'movieId')
        numb = ratings.groupby('movieId')[['userId']].count()
        mov__lin_rat=mov__lin_rat.merge(numb, on='movieId')
        mov__lin_rat.columns=['movieId','title','genres','imdbId','tmdbId','rating','number_of_ratings']
        movies_rating = mov__lin_rat.loc[mov__lin_rat['number_of_ratings']>=50]
        movies_rating = movies_rating.sort_values('rating',ascending=False).head(5)
        movies_list = movies_rating['imdbId'].tolist()
        st.write('Top 5 movies according to our customers:')
        row = st.empty()
        col1, col2, col3, col4, col5 = st.columns(5)

        for i,movie in enumerate(movies_list):
            movie_obj = ia.get_movie(movie)
            poster_url = movie_obj['full-size cover url']
            img = Image.open(requests.get(poster_url, stream=True).raw)
            new_size = (150, 200)
            img = img.resize(new_size)
            movie_title = movies_rating['title'].tolist()

            if i ==0:
                col1.image(img, caption=movie_title[0], width=100)
            elif i ==1:
                col2.image(img, caption=movie_title[1], width=100)
            elif i ==2:
                col3.image(img, caption=movie_title[2], width=100)
            elif i ==3:
                col4.image(img, caption=movie_title[3], width=100)
            else:
                col5.image(img, caption=movie_title[4], width=100)
        pass
    elif option == ['No']:
        'You are right, better have a look at something reccomeneded specifically for YOU'
        
five_top()   
      



def user_choice (user_id, number):
    movied=pd.read_csv('movies.csv')
    ratings = pd.read_csv('ratings.csv')
    links = pd.read_csv('links.csv')
    tags = pd.read_csv('tags.csv')
    users_items = pd.pivot_table(data=ratings, 
                                 values='rating', 
                                 index='userId', 
                                 columns='movieId')
    users_items.fillna(0, inplace=True)
    

    user_similarities = pd.DataFrame(cosine_similarity(users_items),
                                 columns=users_items.index, 
                                 index=users_items.index)
    weights = (
    user_similarities.query("userId != @user_id")[user_id] / sum(user_similarities.query("userId != @user_id")[user_id])
          )
    not_seen_movies = users_items.loc[users_items.index!=user_id, users_items.loc[user_id,:]==0]
    weighted_avg = pd.DataFrame(not_seen_movies.T.dot(weights), columns =[ 'predicted_weight'])
    weigh_merged= weighted_avg.sort_values('predicted_weight', ascending=False).nlargest(number, columns='predicted_weight')
    weigh_merged=weigh_merged.merge(movied, on='movieId')[['movieId','title','predicted_weight']]
    weigh_merged = weigh_merged['title']
    
    return weigh_merged
    pass





def item_choice(movie_title1,number):
    movied=pd.read_csv('movies.csv')
    ratings = pd.read_csv('ratings.csv')
    tags = pd.read_csv('tags.csv')   
    corrmatrix = pd.pivot_table(ratings, values='rating', columns='movieId', index='userId')
    top5 = [318, 858, 2959, 1276, 750]
    movie_ID = movied.loc[movied['title'].str.contains(movie_title1.title()), 'movieId'].tolist()
    for i in range(len(movie_ID)):
        try:
            movie_rat = corrmatrix[movie_ID[i]]
            movie_rat.dropna(inplace=True)
            similar_movies = corrmatrix.corrwith(movie_rat)
            similar_movies.dropna(inplace=True)
            sim_movies = similar_movies.sort_values(ascending=False)
            sim_movies.drop(movie_ID,inplace=True)
            corr_movie = pd.DataFrame(sim_movies, columns=['PearsonR'])
            corr_movie=corr_movie.loc[~(corr_movie.index.isin(top5))]
            corr_movie = corr_movie.sort_values('PearsonR', ascending=False )['PearsonR'].nlargest(number)
            ol = pd.DataFrame(corr_movie)
            ista = ol.merge(movied, on='movieId')
            ista = ista[['title']]
            return ista
        except KeyError:
            continue
    
if number>0:
    if user_id:
        st.write(f'This is top {number} movies for user {user_id}')  
        result = user_choice(user_id , number)

        st.dataframe(result)
    if movie_title1:
        st.write(f'This is top {number} movies becouse you like {movie_title1}')  
        result_movie = item_choice(movie_title1 , number)

        st.dataframe(result_movie)
