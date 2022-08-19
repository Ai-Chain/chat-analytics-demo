"""Streamlit demo of the chat-analytics app."""
import re
from datetime import datetime
from itertools import groupby

import streamlit as st

from api_spec import Message, Intent, Sentiment
from src.chat_utils import analyze_chat_stream
from src.data import EXAMPLES
from src.ui import display_intent_stats, display_sentiment_stats, display_threads, display_messages_by_intent, footer

INTERESTING_INTENTS = {Intent.COMPLAINT: {"title": "😡 Complaints", "color": 'rgba(38, 24, 74, 0.8)'},
                       Intent.QUESTION: {"title": "❓ Questions", "color": 'rgba(71, 58, 131, 0.8)'},
                       Intent.PRAISE: {"title": "😘 Praise", "color": 'rgba(122, 120, 168, 0.8)'},
                       }

INTERESTING_SENTIMENTS = {Sentiment.NEGATIVE: {"title": "Negative", "color": '#FF4E4E'},
                          Sentiment.NEUTRAL: {"title": "Positive", "color": '#CECECE'},
                          Sentiment.POSITIVE: {"title": "Neutral", "color": '#55D078'},
                          }


def main():
    st.set_page_config(
        page_title='Chat Analytics',
        page_icon="🚢"
    )

    st.title("Chat Analytics")
    example = st.selectbox("Example", options=EXAMPLES)

    text = st.text_area(
        label="Conversation",
        value=EXAMPLES[example] if example else "Type your conversation here.",
        height=500,
    )

    if st.button(label="Analyze! 🚀"):
        text = text.strip()
        chat_stream = [
            Message(
                message_id=str(i),
                timestamp=datetime.now(),
                user_id=user,
                text=message,
            )
            for i, (user, message) in enumerate(re.findall(r"(\w+):\s*(.*)", text))
        ]
        with st.spinner("Processing..."):
            processed_chat_stream = analyze_chat_stream(chat_stream)

            intent_to_messages = {k: list(v) for k, v in
                                  groupby(sorted(processed_chat_stream, key=lambda x: x.intent), lambda x: x.intent)}
            st.markdown("")

            display_intent_stats(intent_to_messages)

            display_sentiment_stats(processed_chat_stream)

            display_messages_by_intent(intent_to_messages)

            st.markdown("""---""")

            display_threads(processed_chat_stream)
    footer()


if __name__ == '__main__':
    main()
