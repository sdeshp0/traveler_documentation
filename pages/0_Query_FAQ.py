import streamlit as st
import pandas as pd
import warnings

# Suppress FutureWarning messages
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
    from FAQSearch import GlossarySearch

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
            "The most reliable approach is to query based on the glossary tags. Other query methods can be found"
            "on the experimental query page.</p>", unsafe_allow_html=True)
st.divider()

with st.expander('View FAQ'):
    t1, t2 = st.tabs(['View Glossary', 'View FAQ'])

    with t1:
        st.markdown("<h2 style='text-align: center; color: grey;'> Tag Glossary </h2>", unsafe_allow_html=True)
        glossary_table = df_glossary.drop('index', axis=1)
        st.dataframe(data=glossary_table, width='stretch')

    with t2:
        st.markdown("<h2 style='text-align: center; color: grey;'> Traveler FAQ </h2>", unsafe_allow_html=True)
        st.dataframe(data=df_questions, width='stretch')

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

        query = query.lower()
        glossary_search = GlossarySearch(query=query, glossary_df=df_glossary, faq_df=df_questions)

        qt = glossary_search.queryTags
        ql = glossary_search.questionNums
        qr = glossary_search.result

        if ql:
            st.success('Queried text "{}" was found in the glossary tag list. '
                       'Listing questions associated with this query:'.format(query.lower()))

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
