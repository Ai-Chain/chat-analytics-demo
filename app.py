"""Streamlit demo of the chat-analytics app."""
import re
from datetime import datetime
from typing import List

import pandas as pd
import streamlit as st
from pydantic import parse_obj_as
from steamship import App, AppInstance, Steamship

from api_spec import Message

APP_HANDLE = "chat-analytics-app"


def _get_app_instance():
    client = Steamship(
        api_key=st.secrets["steamship_api_key"],
        api_base=st.secrets["steamship_api_base"],
        app_base=st.secrets["steamship_app_base"],
        web_base=st.secrets["steamship_web_base"],
    )
    config = {
        "oneai_api_key": st.secrets["oneai_api_key"],
        "hf_api_bearer_token": st.secrets["hf_api_bearer_token"],
        "hf_model_path": "typeform/distilbert-base-uncased-mnli"
    }
    app = App.get(client, handle=APP_HANDLE).data
    assert app is not None
    assert app.id is not None
    app_instance = AppInstance.create(client, app_id=app.id, config=config).data
    return app_instance


st.set_page_config(layout="wide")

EXAMPLES = {
    "chat_stream_1": """enias:
Hi Team!

enias:
Thanks for getting back to us on the styling issue we had last week. Font colours are so important for productivity.

enias:
I noticed ab.bot being very verbose lately

enias:
Is there a way to decrease the verbosity level?

enias:
I want ab.bot to ignore thank you messages and stop asking our customers to assign messages to threads.

enias:
Our clients are not technical so working with threads is difficult.

enias:
Thanks again, looking forward to your response!

enias:
Oh, before I forget. Is there a settings to change the font size?
    """
}

example = st.selectbox("Example", options=EXAMPLES)

text = st.text_area(
    label="Conversation",
    value=EXAMPLES[example] if example else "Type your conversation here.",
    height=500,
)


def visualize_chat_stream(chat_stream: List[Message]):
    """Visualize a chat stream using a pandas dataframe."""
    df = pd.DataFrame([message.dict() for message in chat_stream])
    st.dataframe(df)


def test_analyze(chat_stream: List[Message]) -> List[Message]:
    """Test analyze endpoint."""
    app_instance = _get_app_instance()

    response = app_instance.post(
        "analyze",
        chat_stream=[message.dict(format_dates=True, format_enums=True) for message in chat_stream],
    )
    processed_chat_stream = parse_obj_as(List[Message], response.data["chat_stream"])

    return processed_chat_stream


if st.button(label="Analyze! 🚀"):
    # Parse the conversation
    text = text.strip()
    messages = [piece.strip() for piece in re.split(r"\n\s*\n", text)]
    messages = [re.sub(r"\w+:\s*", "", piece) for piece in messages]

    chat_stream = [
        Message(
            message_id=str(i),
            timestamp=datetime(2022, 6, 15, 16, 18, 44, 155),
            user_id="1",
            text=message,
        )
        for i, message in enumerate(messages)
    ]
    with st.expander("Original chat stream", expanded=True):
        visualize_chat_stream(chat_stream)

    with st.spinner("Wait for it..."):
        processed_chat_stream = test_analyze(chat_stream)
        visualize_chat_stream(processed_chat_stream)
        st.balloons()
