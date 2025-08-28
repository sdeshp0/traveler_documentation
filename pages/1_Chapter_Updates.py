import streamlit as st
import pandas as pd
from matplotlib import pyplot as plt
from datetime import datetime
import warnings

# Suppress FutureWarning messages
warnings.simplefilter(action='ignore', category=FutureWarning)

st.set_page_config(layout='wide', page_title='Chapter Updates')
st.logo('data/pokeball_logo.svg')


def generate_chart(df):
    dates = [datetime.strptime(d, '%b %d, %Y') for d in df['Date*']]
    count = [int(x.replace(',', '')) for x in df['Word Count**']]
    tot_count = [int(x.replace(',', '')) for x in df['Running Total Word Count***']]
    avg_count = [int(x.replace(',', '')) for x in df['Running Avg Word Count']]
    chapters = df.index.tolist()
    titles = df['Title'].tolist()

    fig, ax1 = plt.subplots()

    # column chart
    ax1.bar(dates, count, color='darkblue', label='Word Count', width=10)
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Word Count', color='black')
    ax1.tick_params(axis='y', labelcolor='black')

    # Running Avg Line

    ax1.plot(dates, avg_count, color='red', label='Running Avg Word Count')
    ax1.legend(loc='upper left')

    # Running Total Line

    ax2 = ax1.twinx()
    ax2.plot(dates, tot_count, color='black', label='Running Total Word Count')
    ax2.set_ylabel('Running Total Word Count', color='black')
    ax2.tick_params(axis='y', labelcolor='black')
    ax2.legend(loc='upper right')

    plt.title('Traveler Fanfiction Chapter Updates')
    plt.tight_layout()
    return fig


if 'updates' not in st.session_state:
    df_updates = pd.read_csv('data/travelerchapterupdates.csv', index_col='Chapter')
    st.session_state['updates'] = df_updates
else:
    df_updates = st.session_state['updates']

chapter_cols = [c for c in df_updates.columns if 'Notes' not in c]


st.markdown("<h1 style='text-align: center; color: grey;'> Traveler Chapter Update History </h1>", unsafe_allow_html=True)
st.divider()

st.markdown("<p style='text-align: left; color: grey;'> This is the chapter update history of the Traveler "
            "fanfiction story</p>", unsafe_allow_html=True)
st.divider()

with st.expander('Display Chapter Update Chart'):
    st.pyplot(generate_chart(df_updates))
st.divider()

st.subheader('Chapter Update Table')
st.dataframe(df_updates[chapter_cols], use_container_width=True)

st.write('----- General Notes -----')
st.write('*Chapter date is based on the earliest review posted on FFN.')

st.write('**word counts based on https://wordcounter.net/. Counts may include section break text, '
         'but exclude author\'s notes.')

st.write('*** Note that the total word count might differ from what is shown on fanfiction.net. '
         'This is because ffn uses a different methodology to count words that results in a roughly 2% higher word '
         'count as compared to most word processors. See Reddit post by SteelbadgerMk2 in this thread for more '
         'detail - https://www.reddit.com/r/FanFiction/comments/nkp1w2/word_count_on_ao3_and_ffnet/.')

st.write('----- Chapter Specific Notes -----')
st.write('The earliest review for chapter 46 was posted on Jan 2, 2019. Switched to next earliest review date of '
         'Mar 24, 2019 because a same-day update does not make sense given the author\'s notes from '
         'chapters 45 and 46.')

st.divider()
