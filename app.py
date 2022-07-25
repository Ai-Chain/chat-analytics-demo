"""Streamlit demo of the chat-analytics app."""
import re
from datetime import datetime
from time import perf_counter

import streamlit as st

from api_spec import Message
from src.data import EXAMPLES
from src.utils import visualize_chat_stream, analyze_chat_stream

st.set_page_config(layout="wide",
                   page_title='Chat Analytics Demo',
                   page_icon="🚢"
                   )

st.title("Chat Analytics Demo")
example = st.selectbox("Sample", options=EXAMPLES)

text = st.text_area(
    label="Conversation",
    value=EXAMPLES[example] if example else "Type your conversation here.",
    height=500,
)

if st.button(label="Analyze! 🚀"):
    # Parse the conversation
    text = text.strip()
    chat_stream = [
        Message(
            message_id=str(i),
            timestamp=datetime(2022, 6, 15, 16, 18, 44, 155),
            user_id=user,
            text=message,
        )
        for i, (user, message) in enumerate(re.findall(r"(\w+):\s*(.*)", text))
    ]
    with st.expander("Original chat stream", expanded=False):
        visualize_chat_stream(chat_stream)

    with st.spinner("Processing..."):
        t0 = perf_counter()
        processed_chat_stream = analyze_chat_stream(chat_stream)
        t_delta = perf_counter() - t0
        st.title(f"Results [{t_delta:.2f}s]")
        visualize_chat_stream(processed_chat_stream)
        st.balloons()
