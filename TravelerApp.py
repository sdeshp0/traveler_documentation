import streamlit as st
import warnings
import pandas as pd

st.set_page_config(layout='wide', page_title='Traveler App', initial_sidebar_state='expanded')

#Suppress FutureWarning messages
warnings.simplefilter(action='ignore', category=FutureWarning)

@st.cache_data(show_spinner='Reading Data')
def load_data():
    df1 = pd.read_csv('data/glossary.csv')
    df2 = pd.read_csv('data/travelerfaq.csv', index_col='Num')
    df3 = pd.read_csv('data/travelerchapterupdates.csv', index_col='Chapter')
    return df1, df2, df3

df_glossary, df_questions, df_updates = load_data()

st.session_state['glossary'] = df_glossary
st.session_state['faq'] = df_questions
st.session_state['updates'] = df_updates

st.markdown("<h1 style='text-align: center; color: grey;'> Traveler Fanfiction App </h1>", unsafe_allow_html=True)
st.divider()

st.markdown("<p style='text-align: left; color: grey;'> The Traveler Fanfiction App is intended as a resource for "
            "fans and followers of the Traveler fanfiction story. Please use the sidebar to access the various pages."
            "</p>", unsafe_allow_html=True)
st.divider()

with st.expander('About and Credits'):

    st.markdown("<h1 style='text-align: center; color: grey;'> About </h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; color: grey;'> Release Ver 1.1 </h2>", unsafe_allow_html=True)

    st.subheader('Credits')
    st.write('TheStraightElf - Author of the Traveler fanfiction story')
    st.write('Stuffsearcher - Archivist in the Traveler Discord community, who compiled the Traveler FAQ')

    st.subheader('Link to Traveler Fanfiction')
    st.write('https://www.fanfiction.net/s/8466693/1/Traveler')

    st.subheader('Traveler FAQ documentation is up to date as of the following:')
    st.write('General: 2023-10-10')
    st.write('New Island: 2021-09-09')
    st.write('Spoilers: 2021-07-30')
    st.write('Art: 2021-07-30')
    st.write('Stories: 2021-07-30')
    st.write('Indigo Stadium: 2021-07-30')
    st.write('Off Topic: 2021-07-30')
    st.write('Oak Corral: 2021-07-30')
    st.write('Media: 2021-07-30')
    st.write('Traveler Drabble Reviews: 2021-07-30')

    st.subheader('App Maintainer')
    st.write('SID (sidprojects01@gmail.com)')
    st.divider()


