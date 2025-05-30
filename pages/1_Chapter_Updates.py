import streamlit as st
from matplotlib import pyplot as plt
from datetime import datetime
import warnings

#Suppress FutureWarning messages
warnings.simplefilter(action='ignore', category=FutureWarning)

st.set_page_config(layout='wide', page_title='Chapter Updates')
st.logo(image='data/pokeball_logo.png')

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

df_updates = st.session_state['updates']

chapter_cols = [c for c in df_updates.columns if 'Notes' not in c]
chapter_notes = df_updates['Chapter Notes'].copy().dropna()
chapter_notes.index.name='Ch'

general_notes = df_updates['General Notes'].copy().dropna()
general_notes.index.name=None

st.markdown("<h1 style='text-align: center; color: grey;'> Traveler Chapter Update History </h1>", unsafe_allow_html=True)
st.divider()

st.markdown("<p style='text-align: left; color: grey;'> This is the chapter update history of the Traveler "
            "fanfiction story</p>", unsafe_allow_html=True)
st.divider()

st.subheader('Chapter Update Table')
st.dataframe(df_updates[chapter_cols], use_container_width=True)
st.divider()

with st.expander('Display Chapter Update Chart'):
    st.pyplot(generate_chart(df_updates))
st.divider()

with st.expander('Display Chapter Notes'):
    st.dataframe(chapter_notes, use_container_width=True)
st.divider()

with st.expander('Display General Notes'):
    st.dataframe(general_notes, use_container_width=True)