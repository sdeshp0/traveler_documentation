import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import warnings

# Suppress FutureWarning messages
warnings.simplefilter(action='ignore', category=FutureWarning)

st.set_page_config(layout='wide', page_title='Chapter Updates')
st.logo('data/pokeball_logo.svg')


def generate_chart(df):
    # Parse data
    dates = [datetime.strptime(d, '%b %d, %Y') for d in df['Date*']]
    count = [int(x.replace(',', '')) for x in df['Word Count**']]
    tot_count = [int(x.replace(',', '')) for x in df['Running Total Word Count***']]
    avg_count = [int(x.replace(',', '')) for x in df['Running Avg Word Count']]
    titles = df['Title'].tolist()

    # Format numbers as "12.345k" or "1.234M"
    def fmt_k(n):
        if n >= 1_000_000:
            return f"{n / 1_000_000:.3f}M"
        elif n >= 1_000:
            return f"{n / 1_000:.3f}k"
        else:
            return str(n)

    # Build customdata matrix for unified tooltip
    # Each row: [title, word_count_k, running_avg_k, running_total_k]
    customdata = list(zip(
        titles,
        [fmt_k(c) for c in count],
        [fmt_k(a) for a in avg_count],
        [fmt_k(t) for t in tot_count]
    ))

    # Unified hovertemplate
    hovertemplate = (
        "<b>Date:</b> %{x|%B %d, %Y}<br>"
        "<b>Title:</b> %{customdata[0]}<br><br>"
        "<b>Word Count:</b> %{customdata[1]}<br>"
        "<b>Running Average:</b> %{customdata[2]}<br>"
        "<b>Running Total:</b> %{customdata[3]}<br>"
        "<extra></extra>"
    )

    fig = go.Figure()

    # --- Bar Chart: Word Count ---
    fig.add_bar(
        x=dates,
        y=count,
        name='Word Count',
        marker_color='darkblue',
        customdata=customdata,
        hoverinfo='skip'
    )

    # --- Line Chart: Running Avg ---
    fig.add_scatter(
        x=dates,
        y=avg_count,
        mode='lines',
        name='Running Avg Word Count',
        line=dict(color='red', width=2),
        customdata=customdata,
        hoverinfo='skip'
    )

    # --- Line Chart: Running Total (Secondary Axis) ---
    fig.add_scatter(
        x=dates,
        y=tot_count,
        mode='lines',
        name='Running Total Word Count',
        line=dict(color='black', width=2),
        yaxis='y2',
        customdata=customdata,
        hovertemplate=hovertemplate
    )

    # --- Layout ---
    fig.update_layout(
        title='Traveler Fanfiction Chapter Updates',
        xaxis=dict(title='Date'),
        yaxis=dict(title='Word Count'),
        yaxis2=dict(
            title='Running Total Word Count',
            overlaying='y',
            side='right'
        ),
        legend=dict(
            x=0,
            y=1,
            xanchor="left",
            yanchor="top"
        ),
        hovermode='x unified',
        margin=dict(l=60, r=60, t=60, b=60)
    )

    return fig


def velocity_chart(df):
    # Parse data
    dates = [datetime.strptime(d, '%b %d, %Y') for d in df['Date*']]
    w_vel = [int(x) for x in df['Word Velocity****']]
    avg_vel = [int(x) for x in df['Running Average Word Velocity****']]
    titles = df['Title'].tolist()

    # Number formatter for tooltip
    def fmt_k(n):
        if n >= 1_000_000:
            return f"{n/1_000_000:.3f}M"
        elif n >= 1_000:
            return f"{n/1_000:.3f}k"
        else:
            return str(n)

    # Customdata for unified tooltip
    # Each row: [title, velocity_k, avg_velocity_k]
    customdata = list(zip(
        titles,
        [fmt_k(v) for v in w_vel],
        [fmt_k(a) for a in avg_vel]
    ))

    # Unified tooltip (shown only on the line trace)
    hovertemplate = (
        "<b>Date:</b> %{x|%B %d, %Y}<br>"
        "<b>Title:</b> %{customdata[0]}<br><br>"
        "<b>Word Velocity:</b> %{customdata[1]}<br>"
        "<b>Running Average:</b> %{customdata[2]}<br>"
        "<extra></extra>"
    )

    fig = go.Figure()

    # --- Bar Chart: Word Velocity ---
    fig.add_bar(
        x=dates,
        y=w_vel,
        name='Chapter Word Velocity',
        marker_color='darkblue',
        hoverinfo='skip',        # hide bar tooltip
        customdata=customdata
    )

    # --- Line Chart: Running Average ---
    fig.add_scatter(
        x=dates,
        y=avg_vel,
        mode='lines',
        name='Running Avg Word Velocity',
        line=dict(color='red', width=2),
        customdata=customdata,
        hovertemplate=hovertemplate
    )

    # --- Layout ---
    fig.update_layout(
        title='Traveler Fanfiction Chapter Word Velocity',
        xaxis=dict(title='Date'),
        yaxis=dict(title='Word Velocity (words/day)'),
        hovermode='x unified',
        legend=dict(
            x=0,
            y=1,
            xanchor="left",
            yanchor="top"
        ),
        margin=dict(l=60, r=60, t=60, b=60)
    )

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

st.subheader('Chapter Update Table')
st.dataframe(df_updates[chapter_cols], use_container_width=True)
st.divider()

st.subheader('Chapter Update Charts')
with st.expander('Display Chapter Update Chart'):
    st.plotly_chart(generate_chart(df_updates), use_container_width=True)

with st.expander('Display Chapter Word Velocity Chart'):
    st.plotly_chart(velocity_chart(df_updates), use_container_width=True)

st.divider()

st.write('----- General Notes -----')
st.write('\* Chapter date is based on the earliest review posted on FFN.')

st.write('** word counts based on https://wordcounter.net/. Counts may include section break text, '
         'but exclude author\'s notes.')

st.write('*** Note that the total word count might differ from what is shown on FFN. '
         'This is because FFN uses a different methodology to count words that results in a roughly 2% higher word '
         'count as compared to most word processors. See Reddit post by SteelbadgerMk2 in this thread for more '
         'detail - https://www.reddit.com/r/FanFiction/comments/nkp1w2/word_count_on_ao3_and_ffnet/.')

st.write('**** Word velocity is defined as chapter word count / days since previous chapter')

st.write('----- Chapter Specific Notes -----')
st.write('The earliest review for chapter 46 was posted on Jan 2, 2019. Switched to next earliest review date of '
         'Mar 24, 2019 because a same-day update does not make sense given the author\'s notes from '
         'chapters 45 and 46.')

st.divider()
