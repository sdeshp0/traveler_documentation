import streamlit as st
st.set_page_config(layout='wide', page_title='Query FAQ')
import warnings

#Suppress FutureWarning messages
warnings.simplefilter(action='ignore', category=FutureWarning)

df_glossary = st.session_state['glossary']
df_questions = st.session_state['faq']
df_glossary.reset_index(inplace=True)
glossary_tags = [t.lower() for t in df_glossary['Tag']]
df_glossary.index = glossary_tags
df_glossary.drop('Tag', inplace=True, axis=1)
df_glossary.index.name='Tag'
df_questions.index.name = None

st.markdown("<h1 style='text-align: center; color: grey;'> Traveler FAQ </h1>", unsafe_allow_html=True)
st.divider()

st.markdown("<p style='text-align: left; color: grey;'> This is a query tool that let's you query the Traveler FAQ "
            "based on keyword tags associated with each question and answer</p>", unsafe_allow_html=True)
st.divider()

t1, t2, t3 = st.tabs(['Query FAQ', 'View Glossary', 'View FAQ'])

with t1:
    st.markdown("<h2 style='text-align: center; color: grey;'> Query FAQ </h2>", unsafe_allow_html=True)
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

            ql = df_glossary.loc[query.lower(), 'RelatedQuestions']
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

                    ql = df_glossary.loc[query.lower(), 'RelatedQuestions']
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
    st.markdown("<h2 style='text-align: center; color: grey;'> Tag Glossary </h2>", unsafe_allow_html=True)
    st.dataframe(data=df_glossary, use_container_width=True)

with t3:
    st.markdown("<h2 style='text-align: center; color: grey;'> Traveler FAQ </h2>", unsafe_allow_html=True)
    st.dataframe(data=df_questions, use_container_width=True)