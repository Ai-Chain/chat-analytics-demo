from typing import List

import pandas as pd
import streamlit as st
from pydantic import parse_obj_as
from steamship import AppInstance, Steamship, App

from api_spec import Message
from src.constants import APP_HANDLE, HF_MODEL_PATH


@st.cache(ttl=3600, allow_output_mutation=True)
def get_app_instance(api_key: str, api_base: str, app_base: str, web_base: str, oneai_api_key: str,
                     hf_api_bearer_token: str) -> AppInstance:
    """Get an instance of the chat-analytics-app."""
    client = Steamship(
        api_key=api_key,
        api_base=api_base,
        app_base=app_base,
        web_base=web_base
    )
    config = {
        "oneai_api_key": oneai_api_key,
        "hf_api_bearer_token": hf_api_bearer_token,
        "hf_model_path": HF_MODEL_PATH
    }
    app = App.get(client, handle=APP_HANDLE).data
    app_instance = AppInstance.create(client, app_id=app.id, config=config).data
    return app_instance


def visualize_chat_stream(chat_stream: List[Message]):
    """Visualize a chat stream using a pandas dataframe."""
    df = pd.DataFrame([message.dict() for message in chat_stream])
    df = df.drop(["timestamp"], axis=1)
    st.dataframe(df)


def analyze_chat_stream(chat_stream: List[Message]) -> List[Message]:
    """Test analyze endpoint."""
    app_instance = get_app_instance(api_key=st.secrets["steamship_api_key"],
                                    api_base=st.secrets["steamship_api_base"],
                                    app_base=st.secrets["steamship_app_base"],
                                    web_base=st.secrets["steamship_web_base"],
                                    oneai_api_key=st.secrets["oneai_api_key"],
                                    hf_api_bearer_token=st.secrets["hf_api_bearer_token"])

    response = app_instance.post(
        "analyze",
        chat_stream=[message.dict(format_dates=True, format_enums=True)
                     for message in chat_stream],
    )
    processed_chat_stream = parse_obj_as(List[Message], response.data["chat_stream"])

    return processed_chat_stream
