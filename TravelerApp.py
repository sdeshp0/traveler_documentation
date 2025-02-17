import streamlit as st
st.set_page_config(layout='wide', page_title='Traveler FAQ App', initial_sidebar_state='collapsed')

import pandas as pd
import warnings

#Suppress FutureWarning messages
warnings.simplefilter(action='ignore', category=FutureWarning)

df_glossary = pd.read_csv('glossary.csv')
glossary_tags = [t.lower() for t in df_glossary['Tag']]
df_glossary.index = glossary_tags
df_glossary.drop('Tag', inplace=True, axis=1)
df_glossary.index.name='Tag'
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
    st.write('Enter a query tag to get a list of associated questions')
    st.write('Partial query tags are supported, eg. a query of "pokemon" will check all tags containing "pokemon" '
             'and give you a list of all tags containing "pokemon".')
    st.write('Note that the query is not case-sensitive.')

    query = st.text_input(label='Enter query text')
    run_query = st.button(label='Search for query text in glossary')
    st.divider()

    if run_query:

        glossary_tags = df_glossary.index
        queried_tags = [t for t in glossary_tags if query.lower() in t]

        if len(queried_tags) == 1 and query.lower() in glossary_tags:
            st.success('Query "{}" was found in glossary tag list. '
                       'Listing questions associated with query'.format(query))

            ql = df_glossary.loc[query.lower(), 'Question']
            ql = ql.strip("[]")
            ql = [int(i) for i in ql.split(", ")]

            c1, c2 = st.columns(2)

            for q in ql:
                st.markdown("<h5 style='text-align: left; color: black;'> Question {} </h5>".format(q),
                            unsafe_allow_html=True)
                c1, c2 = st.columns(2)

                with c1:
                    st.write('Question:')
                    st.write(df_questions.loc[q, ['Question']].values[0])

                with c2:
                    st.write('Answer:')
                    st.write(df_questions.loc[q, ['Answer']].values[0])
                st.write('Related Tags:')
                st.write(df_questions.loc[q, ['RelatedTags']].values[0])
                st.divider()

            #st.table(data=df_questions.loc[ql, ['Question', 'Answer', 'RelatedTags']])

        elif len(queried_tags) >= 1:
            if query.lower() in glossary_tags:
                st.warning('Query "{}" is a tag in the glossary. '
                           'Query text was also found in other tags'.format(query.lower()))

                with st.expander(label='Hide questions associated with tag "{}"?'.format(query), expanded=True):
                    st.success('Listing questions associated with query tag "{}"'.format(query))

                    ql = df_glossary.loc[query.lower(), 'Question']
                    ql = ql.strip("[]")
                    ql = [int(i) for i in ql.split(", ")]

                    c1, c2 = st.columns(2)

                    for q in ql:
                        st.markdown("<h5 style='text-align: left; color: black;'> Question {} </h5>".format(q),
                                    unsafe_allow_html=True)
                        c1, c2 = st.columns(2)

                        with c1:
                            st.markdown("<p style='text-align: left; color: black;'>Question:</p>".format(q),
                                        unsafe_allow_html=True)
                            st.write(df_questions.loc[q, ['Question']].values[0])

                        with c2:
                            st.markdown("<p style='text-align: left; color: black;'>Answer:</p>".format(q),
                                        unsafe_allow_html=True)
                            st.write(df_questions.loc[q, ['Answer']].values[0])
                        st.write('Related Tags:')
                        st.write(df_questions.loc[q, ['RelatedTags']].values[0])
                        st.divider()

                    #st.table(data=df_questions.loc[ql, ['Question', 'Answer', 'RelatedTags']])

                st.warning('Did you mean to search for any of the following tags?')
                st.write([t for t in queried_tags if t != query.lower()])
            else:
                st.warning('Query text does not match any of the tags. Did you mean to search for any of the following '
                           'tags?')
                st.write([t for t in queried_tags if t != query.lower()])
                #st.write(queried_tags)

        else:
            st.error('Queried text is not in the glossary tag list')
            st.stop()

with t2:
    st.table(data=df_glossary)

with t3:
    st.table(data=df_questions)

with t4:
    st.markdown("<h2 style='text-align: center; color: grey;'> Release Ver 0.3 </h2>", unsafe_allow_html=True)

    st.subheader('Credits')
    st.write('TheStraightElf - Author of the Traveler fanfiction story')
    st.write('Stuffsearcher - Archivist in the Traveler Discord community, who compiled the source documentation used in '
             'this app')

    st.subheader('Link to Traveler Fanfiction')
    st.write('https://www.fanfiction.net/s/8466693/1/Traveler')

    st.subheader('App Maintainer')
    st.write('SID (sidprojects01@gmail.com')
    st.divider()