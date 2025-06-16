import streamlit as st
import warnings

#Fix Streamlit-Torch Issue
import torch
torch.classes.__path__ = []

#Suppress FutureWarning messages
warnings.simplefilter(action='ignore', category=FutureWarning)

st.set_page_config(layout='wide', page_title='Query FAQ')
st.logo('data/pokeball_logo.svg')

with st.spinner('Loading Query Search Algorithms'):
    from FAQSearch import GlossarySearch, TFIDFsearch, EmbeddingSearch, HybridSearch

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
            "using different approaches. The most reliable approach is to query based on the glossary tags. Other"
            " approaches are experimental based on Natural Language Processing algorithms for text search and "
            " similarity.</p>", unsafe_allow_html=True)
st.divider()

with st.expander('View FAQ'):
    t1, t2 = st.tabs(['View Glossary', 'View FAQ'])

    with t1:
        st.markdown("<h2 style='text-align: center; color: grey;'> Tag Glossary </h2>", unsafe_allow_html=True)
        glossary_table = df_glossary.drop('index', axis=1)
        st.dataframe(data=glossary_table, use_container_width=True)

    with t2:
        st.markdown("<h2 style='text-align: center; color: grey;'> Traveler FAQ </h2>", unsafe_allow_html=True)
        st.dataframe(data=df_questions, use_container_width=True)

st.divider()

with st.expander('Query using Glossary Tags'):
    st.markdown("<h2 style='text-align: center; color: grey;'> Query FAQ </h2>", unsafe_allow_html=True)
    st.write('Enter a query tag to get a list of associated questions')
    st.write('Partial query tags are supported, eg. a query of "pokemon" will check all tags containing "pokemon" '
             'and give you a list of all tags containing "pokemon".')
    st.write('Note that the query is not case-sensitive.')

    query = st.text_input(label='Enter query tag to search using glossary:')
    st.divider()

    if query:
        glossary_search = GlossarySearch(query)

        qt = glossary_search.queryTags
        ql = glossary_search.questionNums
        qr = glossary_search.result

        if ql:
            st.success('Queried text "{}" was found in the glossary tag list. '
                       'Listing questions associated with this query:'.format(query))

            if len(qt) > 1:
                st.warning('Queried text "{}" was also found in other tags. '
                           'Please check the list below the displayed results.'.format(query.lower()))

            for q in ql:
                st.markdown("<h5 style='text-align: left; color: black;'> Question {} </h5>".format(q),
                            unsafe_allow_html=True)

                c1, c2 = st.columns(2)

                with c1:
                    st.write('Question:')
                    st.write(qr.loc[q, ['Question']].values[0])
                with c2:
                    st.write('Answer:')
                    st.write(qr.loc[q, ['Answer']].values[0])

                st.write('Related Tags:')
                st.write(qr.loc[q, ['RelatedTags']].values[0])
                st.divider()

            if len(qt) > 1:
                st.warning('Did you mean to search for any of the following?'.format(query.lower()))
                st.write([t for t in qt if t != query.lower()])
        else:
            st.error('Queried text is not in the glossary tag list. Please try another query.')

st.divider()

with st.expander('Experimental Queries'):
    st.markdown("<h2 style='text-align: center; color: grey;'> Experimental query methods </h2>", unsafe_allow_html=True)

    st.markdown("<p style='text-align: left; color: grey;'> These are experimental queries based on NLP tools and "
                " algorithms. This allows you to query using statements or questions. The queries are then processed "
                "and evaluated against the text in the FAQ to filter and display relevant questions and answers from "
                "the FAQ. As these query methods are experimental, the results may not be as reliable.</p>",
                unsafe_allow_html=True)
    st.write('Note that these search algorithms do NOT use AI or Generative AI models.')
    st.divider()

    query = st.text_input('Enter your question:')
    algorithm = st.selectbox(label='Choose Query Algorithm',
                             options=['TF-IDF', 'Embedding-Based', 'Hybrid'],
                             index=2)
    st.divider()

    if query:

        if algorithm == 'TF-IDF':

            st.markdown("<h2 style='text-align: center; color: grey;'> TF-IDF: Term Frequency - Inverse Document Frequency "
                        "</h2>", unsafe_allow_html=True)
            st.write('Weighs words based on their relative importance in the document and identifies relevant entries'
                    'in the FAQ based on text similarity between the query and document text.')

            tfidf_search = TFIDFsearch(query)
            tfidf_result = tfidf_search.results

            if not tfidf_result.empty:
                st.write('Here are some relevant entries based on your query ordered by relevance:')

                for q in tfidf_result.index.values:
                    st.markdown("<h5 style='text-align: left; color: black;'> Question {} </h5>".format(q),
                                unsafe_allow_html=True)
                    c1, c2 = st.columns(2)

                    with c1:
                        st.markdown("<p style='text-align: left; color: black;'>Question:</p>",
                                    unsafe_allow_html=True)
                        st.write(tfidf_result.loc[q, ['Question']].values[0])

                    with c2:
                        st.markdown("<p style='text-align: left; color: black;'>Answer:</p>",
                                    unsafe_allow_html=True)
                        st.write(tfidf_result.loc[q, ['Answer']].values[0])
                    st.write('Related Tags:')
                    st.write(tfidf_result.loc[q, ['RelatedTags']].values[0])
                    st.divider()

            else:
                st.write('No relevant entries were found for your query. Please try again with a different query.')

        elif algorithm == 'Embedding-Based':

            st.markdown(
                "<h2 style='text-align: center; color: grey;'> Embedding-Based Search "
                "</h2>", unsafe_allow_html=True)
            st.write('Matches queries to FAQ based on semantic meaning rather than keyword overlaps and similarity.'
                     ' This approach works by converting the FAQ text into sentence embeddings, enabling more'
                     ' context-aware searches.')

            embedding_search = EmbeddingSearch(query)
            embedding_result = embedding_search.results

            if not embedding_result.empty:
                st.write('Here are some relevant entries based on your query ordered by relevance:')

                for q in embedding_result.index.values:
                    st.markdown("<h5 style='text-align: left; color: black;'> Question {} </h5>".format(q),
                                unsafe_allow_html=True)
                    c1, c2 = st.columns(2)

                    with c1:
                        st.markdown("<p style='text-align: left; color: black;'>Question:</p>",
                                    unsafe_allow_html=True)
                        st.write(embedding_result.loc[q, ['Question']].values[0])

                    with c2:
                        st.markdown("<p style='text-align: left; color: black;'>Answer:</p>",
                                    unsafe_allow_html=True)
                        st.write(embedding_result.loc[q, ['Answer']].values[0])
                    st.write('Related Tags:')
                    st.write(embedding_result.loc[q, ['RelatedTags']].values[0])
                    st.divider()

            else:
                st.write('No relevant entries were found for your query. Please try again with a different query.')

        else:

            st.markdown(
                "<h2 style='text-align: center; color: grey;'> Hybrid Search "
                "</h2>", unsafe_allow_html=True)
            st.write('Combines the keyword-based and embedding-based approaches and prioritizes high-confidence matches'
                     'from each method.')

            hybrid_search = HybridSearch(query)
            hybrid_result = hybrid_search.results

            if not hybrid_result.empty:
                st.write('Here are some relevant entries based on your query ordered by relevance:')

                for q in hybrid_result.index.values:
                    st.markdown("<h5 style='text-align: left; color: black;'> Question {} </h5>".format(q),
                                unsafe_allow_html=True)
                    c1, c2 = st.columns(2)

                    with c1:
                        st.markdown("<p style='text-align: left; color: black;'>Question:</p>",
                                    unsafe_allow_html=True)
                        st.write(hybrid_result.loc[q, ['Question']].values[0])

                    with c2:
                        st.markdown("<p style='text-align: left; color: black;'>Answer:</p>",
                                    unsafe_allow_html=True)
                        st.write(hybrid_result.loc[q, ['Answer']].values[0])
                    st.write('Related Tags:')
                    st.write(hybrid_result.loc[q, ['RelatedTags']].values[0])
                    st.divider()

            else:
                st.write('No relevant entries were found for your query. Please try again with a different query.')

