import streamlit as st
import streamlit.components.v1 as components
import pandas as pd

st.set_page_config('Albums of the Year', layout="wide")
show_years = '2022'

@st.cache
def load_data():
    df = pd.read_csv('album_data.csv')
    df['Album URL'] = df['Album URL'].fillna('')
    return df.sort_values(['Album Key', 'Points'], ascending=False)

data = load_data()

@st.cache
def grab_unique_genres():
    genres = list(data['Genre'].unique())
    genres.append('All')
    genres.sort(key=lambda x: "0" if x == 'All' else x)
    return genres

@st.cache
def grab_unique_publications():
    publications = list(data['Publication'].unique())
    publications.append('All')
    publications.sort(key=lambda x: "0" if x == 'All' else x)
    return publications

genres = grab_unique_genres()
publications = grab_unique_publications()
global_page_length = 50

with st.sidebar:
    show_years = st.selectbox('Year', [2022, 2013])
    show_genres = st.selectbox('Genres', genres, index=0)
    show_publications = st.selectbox('Publications', publications, index=0)
    sort_method = st.radio('Sort Method', ['Total Placement', 'Average Placement'], index=0)

def clean_data(show_genres, show_publications, show_years, sort_method):
    if 'list_start' in st.session_state:
        del st.session_state.list_start
    if show_genres == 'All':
        show_genres = list(data['Genre'].unique())
    else:
        show_genres = [show_genres]
    if show_publications == 'All':
        show_publications = list(data['Publication'].unique())
    else:
        show_publications = [show_publications]
    if sort_method == 'Total Placement':
        return data[(data['Genre'].isin(show_genres)) & (data['Publication'].isin(show_publications)) & (data['Year'] == int(show_years))].groupby(['Album Key', 'Artist', 'Album', 'Genre', 'Image URL', 'Album URL'])[['Points']].sum().sort_values('Points', ascending=False).reset_index()
    elif sort_method == 'Average Placement':
        return data[(data['Genre'].isin(show_genres)) & (data['Publication'].isin(show_publications)) & (data['Year'] == int(show_years))].groupby(['Album Key', 'Artist', 'Album', 'Genre', 'Image URL', 'Album URL'])[['Points']].mean().sort_values('Points', ascending=False).reset_index()

new_data = clean_data(show_genres, show_publications, show_years, sort_method)

print('list start' in st.session_state)
if 'list_start' not in st.session_state:
    st.session_state.list_start = 0

st.session_state.list_end = st.session_state.list_start + global_page_length

print('not triggered', st.session_state.list_start, st.session_state.list_end)



def show_albums(list_start, list_end):
    for position in range(list_start, min(list_end, len(new_data))):
        artist = new_data['Artist'][position]
        album = new_data['Album'][position]
        genre = new_data['Genre'][position]
        image = new_data['Image URL'][position]
        album_url = new_data['Album URL'][position]
        # artist_album = data['Artist'][position] + ' - ' + data['Album'][position]
        col1, col2 = st.columns([1,1.4], gap='large')
        with col1:
            st.image(image, use_column_width=True)
        with col2:
            st.subheader(f'#{position + 1}')
            st.subheader(artist)
            st.subheader(album)
            st.subheader(f'Genre: {genre}')
            container = st.expander('Accolades', expanded=False)
            with container:
                temp_df = data[(data['Album'] == album) & (data['Artist'] == artist)].reset_index()
                for position in range(len(temp_df)):
                    publication = temp_df['Publication'][position]
                    rank = temp_df['Rank'][position]
                    st.write(f'{publication}: {rank}')
            container = st.expander('Listen', expanded=False)
            with container:
                if album_url != '':
                    components.iframe(album_url, height=400)
                else:
                    st.write('No streaming available for this album :(')

show_albums(st.session_state.list_start, st.session_state.list_end)

if st.session_state.list_end < len(new_data):
    if st.button('Show more albums'):
        if st.session_state.list_end < len(new_data):
            st.session_state.list_start += global_page_length
            st.session_state.list_end += global_page_length
            print('triggered', st.session_state.list_start, st.session_state.list_end)
            show_albums(st.session_state.list_start, st.session_state.list_end)
