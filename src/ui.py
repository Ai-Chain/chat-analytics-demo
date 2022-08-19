from itertools import groupby
from typing import Union, List

import plotly.graph_objects as go
import streamlit as st

from api_spec import Intent, Sentiment

INTERESTING_INTENTS = {Intent.COMPLAINT: {"title": "😡 Complaints", "color": 'rgba(38, 24, 74, 0.8)'},
                       Intent.QUESTION: {"title": "❓ Questions", "color": 'rgba(71, 58, 131, 0.8)'},
                       Intent.PRAISE: {"title": "😘 Praise", "color": 'rgba(122, 120, 168, 0.8)'},
                       }

INTERESTING_SENTIMENTS = {Sentiment.NEGATIVE: {"title": "Negative", "color": '#FF4E4E'},
                          Sentiment.NEUTRAL: {"title": "Positive", "color": '#CECECE'},
                          Sentiment.POSITIVE: {"title": "Neutral", "color": '#55D078'},
                          }


def display_sentiment_stats(processed_chat_stream):
    sentiments = [message.sentiment for message in processed_chat_stream]
    counts = [sentiments.count(sentiment) / len(sentiments) * 100
              for sentiment in INTERESTING_SENTIMENTS
              ]
    plot_graph(counts, list(INTERESTING_SENTIMENTS),
               [props["color"] for props in INTERESTING_SENTIMENTS.values()])


def display_intent_stats(intent_to_messages):
    cols = st.columns(len(INTERESTING_INTENTS))
    for col, (intent, props) in zip(cols, INTERESTING_INTENTS.items()):
        col.metric(props["title"], len(intent_to_messages[intent]),
                   delta=None, delta_color="normal", help=None)


def display_threads(processed_chat_stream):
    st.markdown("#### Threads")
    st.markdown("Messages clustered by their topic")
    for thread_ix, (_, messages) in enumerate(groupby(processed_chat_stream, lambda x: x.root_message_id)):
        with st.expander(f"🧵 Thread {thread_ix}"):
            for message in messages:
                st.markdown(f"[{message.user_id}] "
                            f"  {message.text}")


def plot_graph(x: List[Union[int, float]], y: List[str], colors: List[str]) -> None:
    fig = go.Figure()

    for ix, xd in enumerate(x):
        fig.add_trace(go.Bar(
            x=[xd], y=[0],
            orientation='h',
            marker=dict(
                color=colors[ix],
            ),
            hovertemplate="<br>".join([
                f"Label: {y[ix]}",
                "Relative Frequency: %{x}%",
            ])
        ))

    fig.update_layout(
        xaxis=dict(
            showgrid=False,
            showline=False,
            showticklabels=False,
            zeroline=False,
        ),
        yaxis=dict(
            showgrid=False,
            showline=False,
            showticklabels=False,
            zeroline=False,
        ),
        barmode='stack',
        margin=dict(l=0, r=0, t=0, b=0),
        showlegend=False,
        autosize=False,
        height=50,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )

    annotations = []

    space = 0
    for xd, yd in zip(x, y):
        # labeling the rest of percentages for each bar (x_axis)
        annotations.append(dict(xref='x', yref='y',
                                x=space + (xd / 2), y=0,
                                text=f"{yd} ({xd}%)",
                                font=dict(family='Arial',
                                          size=14,
                                          color='rgb(248, 248, 255)'),
                                showarrow=False))
        space += xd

    fig.update_layout(annotations=annotations)

    st.plotly_chart(fig)


def footer():
    hide_streamlit_style = """
            <style>

footer {
	visibility: hidden;
	}
footer:after {
	content:'Made with ❤️ on Steamship';
	color: rgba(0,0,0,1);
	visibility: visible;
	display: block;
	position: relative;
	padding: 5px;
	top: 2px;
}
            </style>

"""
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)


def display_messages_by_intent(intent_to_messages):
    tabs = st.tabs(
        [f"{props['title']} ({len(intent_to_messages[intent])})" for intent, props in
         INTERESTING_INTENTS.items()])
    for tab, props, messages in zip(tabs, INTERESTING_INTENTS.values(), intent_to_messages.values()):
        with tab:
            st.header(props["title"])
            for message in messages:
                st.markdown(f"[{message.user_id}] "
                            f"  {message.text}")
