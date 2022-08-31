"""Collection of helper functions to analyze a stream of chat messages on Steamship."""
from typing import List

import streamlit as st
from pydantic import parse_obj_as
from steamship import AppInstance, Steamship

from api_spec import Message

APP_HANDLE = "chat-analytics-app-t"


@st.cache(ttl=3600, allow_output_mutation=True)
def get_app_instance(api_key: str) -> AppInstance:
    """Get an instance of the chat-analytics-app."""
    client = Steamship(
        api_key=api_key,
        api_base="https://api.steamship.com/api/v1/",
        app_base="https://steamship.run/",
        web_base="https://app.steamship.com/",
    )
    return AppInstance.create(client, app_handle=APP_HANDLE, handle=APP_HANDLE, upsert=True).data


def analyze_chat_stream(chat_stream: List[Message]) -> List[Message]:
    """Test analyze endpoint."""
    app_instance = get_app_instance(api_key=st.secrets["steamship_api_key"])

    response = app_instance.post(
        "analyze",
        chat_stream=[message.dict(format_dates=True, format_enums=True) for message in chat_stream],
    )
    processed_chat_stream = parse_obj_as(List[Message], response.data["chat_stream"])

    return processed_chat_stream
