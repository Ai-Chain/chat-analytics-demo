"""Streamlit demo of the chat-analytics app."""
import re
from datetime import datetime
from itertools import groupby
from pathlib import Path

import streamlit as st

from api_spec import Message, Intent, Sentiment
from src.auth import check_auth, update_usage, check_usage
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
        page_icon=Path("data/logo.png").open("rb").read()
    )
    footer()

    html_string = """
    <!-- Hotjar Tracking Code for https://steamship.com -->
    <script>
        (function(h,o,t,j,a,r){
            h.hj=h.hj||function(){(h.hj.q=h.hj.q||[]).push(arguments)};
            h._hjSettings={hjid:3131229,hjsv:6};
            a=o.getElementsByTagName('head')[0];
            r=o.createElement('script');r.async=1;
            r.src=t+h._hjSettings.hjid+j+h._hjSettings.hjsv;
            a.appendChild(r);
        })(window,document,'https://static.hotjar.com/c/hotjar-','.js?sv=');
    </script>
    """
    st.markdown(html_string, unsafe_allow_html=True)

    print(Path("data/logo.png").resolve())

    placeholder = st.empty()
    st.session_state["placeholder"] = placeholder
    check_usage(st.session_state.get("usage_stats"))

    check_auth()

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
            if update_usage():
                processed_chat_stream = analyze_chat_stream(chat_stream)

                intent_to_messages = {k: list(v) for k, v in
                                      groupby(sorted(processed_chat_stream, key=lambda x: x.intent),
                                              lambda x: x.intent)}
                st.markdown("")

                display_intent_stats(intent_to_messages)

                display_sentiment_stats(processed_chat_stream)

                display_messages_by_intent(intent_to_messages)

                st.markdown("""---""")

                display_threads(processed_chat_stream)


if __name__ == '__main__':
    main()
