import streamlit as st
import pandas as pd
import numpy as np
import pickle
import warnings

#Fix Streamlit-Torch Issue
import torch
torch.classes.__path__ = []

#Suppress FutureWarning messages
warnings.simplefilter(action='ignore', category=FutureWarning)

st.set_page_config(layout='wide', page_title='Query FAQ')
st.logo('data/pokeball_logo.svg')

# Add Markdown formatting
st.markdown('''
<style>
[data-testid="stMarkdownContainer"] ul{
    padding-left:40px;
}
</style>
''', unsafe_allow_html=True)

with st.spinner('Loading Query Search Algorithms'):
    from FAQSearch import HybridSearch
    from precompute_models import load_summarizer

    # The Summarizer is rather heavier than the other models. Use cache so it only needs to load once
    @st.cache_resource
    def get_summarizer():
        return load_summarizer()
    summarizer = get_summarizer()

    @st.cache_resource
    def load_precompute():
        fe = np.load('data/faq_embeddings.npy')
        v = pickle.load(open('data/tfidf_vectorizer.pkl', 'rb'))
        tm = pickle.load(open('data/tfidf_matrix.pkl', 'rb'))
        return fe, v, tm
    embeddings, vectorizer, tfidf_matrix = load_precompute()


if 'glossary' not in st.session_state:
    df_glossary = pd.read_csv('data/glossary.csv')
    st.session_state['glossary'] = df_glossary
else:
    df_glossary = st.session_state['glossary']

if 'faq' not in st.session_state:
    df_questions = pd.read_csv('data/travelerfaq.csv', index_col='Num')
    st.session_state['faq'] = df_questions
else:
    df_questions = st.session_state['faq']

df_glossary.reset_index(inplace=True)
glossary_tags = [t.lower() for t in df_glossary['Tag']]
df_glossary.index = glossary_tags
df_glossary.drop('Tag', inplace=True, axis=1)
df_glossary.index.name = 'Tag'
df_questions.index.name = None

st.markdown("<h1 style='text-align: center; color: grey;'> Traveler FAQ </h1>", unsafe_allow_html=True)
st.divider()

st.markdown("<p style='text-align: left; color: grey;'> This is a query tool that let's you query the Traveler FAQ "
            "using experimental methods based on Natural Language Processing algorithms for text search and "
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

with st.expander('Experimental Queries'):
    st.markdown("<h2 style='text-align: center; color: grey;'> Experimental query methods </h2>", unsafe_allow_html=True)

    st.markdown("<p style='text-align: left; color: grey;'> This is an experimental query tool based on NLP toolkits "
                "and algorithms. This allows you to query using statements or questions. The queries are then  "
                "processed and evaluated against the text in the FAQ to filter and display relevant questions and  "
                "answers from the FAQ. As this query method is experimental, the results may not be as reliable.</p.",
                unsafe_allow_html=True)
    st.write('Note that this search method does not directly use Generative AI. Neither the FAQ nor the user query '
             'is sent to an Generative AI using an API service. Rather, this app uses pre-trained and pre-computed '
             'models.')

    if st.checkbox('Show more details?'):
        st.write('This is a hybrid search technique that combines keyword-based and vector embedding-based'
                 ' approaches. High confidence matches in the FAQ are prioritized.')
        st.write('The two different search techniques that are combined in this hybrid search are: ')
        st.write('1) TF-IDF: Term Frequency - Inverse Document Frequency')
        st.markdown('* Weighs words based on their relative importance in the document')
        st.markdown('* identifies relevant entries in the FAQ based on keyword similarity between the query and '
                    'document.')
        st.write('2) Embedding-Based Search')
        st.markdown('* Matches queries to FAQ based on semantic meaning rather than keyword overlaps and similarity.')
        st.markdown('*  Works by converting the FAQ text into sentence embeddings, improving context-awareness.')
        st.write()
        st.write('The hybrid approach creates a similarity matrix and sentence embeddings for questions and '
                 'answers in the FAQ and applies the same techniques to the user query. The two different '
                 'algorithms each look for similarities between the user query and the FAQ text, returning a '
                 'set of scored matches that are evaluated versus a preset similarity threshold - this is a '
                 'kind of acceptance criteria for determining if a given row of the FAQ is a good match for '
                 'the user query.')
        st.write()
        st.write('The summary response takes the answers from the top matches shown and attempts to provide a '
                 'short summary of the answers. The summary uses the pre-trained model: '
                 '"sshleifer/distilibart-cnn-12-6" from the HuggingFace Transformers library. This is a distilled '
                 'version of the Facebook BART model that has been fine-tuned on the CNN/DailyMail news '
                 'summarization dataset.')
        st.write()
        st.write('Note that the summary is only as good as the quality of the matches returned by the hybrid search '
                 'algorithm.')
    st.divider()

    query = st.text_input('Enter your question:')
    st.divider()

    if query:

        st.markdown(
            "<h2 style='text-align: center; color: grey;'> Hybrid Search "
            "</h2>", unsafe_allow_html=True)

        hybrid_search = HybridSearch(query=query,
                                     summarizer=summarizer,
                                     faq_df=df_questions,
                                     faq_embeddings=embeddings,
                                     tfidf_vectorizer=vectorizer,
                                     tfidf_matrix=tfidf_matrix
                                     )
        hybrid_result = hybrid_search.results

        hybrid_summary = hybrid_result['summary']
        hybrid_table = hybrid_result['matches']

        if not hybrid_table.empty:
            if st.checkbox('Display a summarized response?'):
                st.write(hybrid_summary)
            st.divider()
            st.write('Here are the relevant matches from the FAQ')

            for q in hybrid_table.index.values:
                st.markdown("<h5 style='text-align: left; color: black;'> Question {} </h5>".format(q),
                            unsafe_allow_html=True)
                c1, c2 = st.columns(2)

                with c1:
                    st.markdown("<p style='text-align: left; color: black;'>Question:</p>",
                                unsafe_allow_html=True)
                    st.write(hybrid_table.loc[q, ['Question']].values[0])

                with c2:
                    st.markdown("<p style='text-align: left; color: black;'>Answer:</p>",
                                unsafe_allow_html=True)
                    st.write(hybrid_table.loc[q, ['Answer']].values[0])
                st.write('Related Tags:')
                st.write(hybrid_table.loc[q, ['RelatedTags']].values[0])
                st.divider()

        else:
            st.write(hybrid_summary)

