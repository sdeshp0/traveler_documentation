import streamlit as st
st.set_page_config(layout='wide', page_title='Traveler FAQ App', initial_sidebar_state='collapsed')

import pandas as pd
import warnings

#Suppress FutureWarning messages
warnings.simplefilter(action='ignore', category=FutureWarning)

df_glossary = pd.read_csv('glossary.csv', index_col='Tag')
df_questions = pd.read_csv('questions_manual_fix.csv', index_col='QuestionNumber')
df_questions.index.name = None

st.markdown("<h1 style='text-align: center; color: grey;'> Traveler FAQ App </h1>", unsafe_allow_html=True)
st.divider()

st.markdown("<p style='text-align: center; color: grey;'> Welcome to the Traveler App </p>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: grey;'> The Traveler App is a tool that allows the user to query the "
            "Traveler FAQ documentation</p>", unsafe_allow_html=True)
st.divider()

t1, t2, t3, t4 = st.tabs(['Query Glossary Tags', 'Display Glossary Table', 'Display Question Table', 'About'])

with t1:
    st.markdown("<h2 style='text-align: center; color: grey;'> Query Documentation </h2>", unsafe_allow_html=True)
    st.write('Enter a query tag to get a list of associated questions. Note that the query is case-sensitive')

    query = st.text_input(label='Enter Query')
    run_query = st.button(label='Search Documentation for Query')

    if run_query:

        if query in df_glossary.index:
            st.success('Query "{}" found in glossary. Listing Questions associated with Query'.format(query))

            ql = df_glossary.loc[query, 'Question']
            ql = ql.strip("[]")
            ql = [int(i) for i in ql.split(", ")]

            st.table(data=df_questions.loc[ql, ['Question', 'Answer', 'RelatedTags']])

        else:
            st.error('Queried text is not in the Glossary')
            st.stop()

with t2:
    st.table(data=df_glossary)

with t3:
    st.table(data=df_questions)

with t4:
    st.markdown("<h2 style='text-align: center; color: grey;'> Release Ver 0.1 </h2>", unsafe_allow_html=True)

    st.subheader('Link to Traveler Fanfiction')
    st.write('https://www.fanfiction.net/s/8466693/1/Traveler')

    st.subheader('App Maintainer')
    st.write('SID (sidprojects01@gmail.com')
    st.divider()