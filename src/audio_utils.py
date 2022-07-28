import pandas as pd
import streamlit as st
from steamship import AppInstance, Steamship, Block

APP_HANDLE = "audio-analytics-app"


@st.cache(ttl=3600, allow_output_mutation=True)
def get_app_instance(
        api_key: str,
        aws_access_key_id: str,
        aws_secret_access_key: str,
        aws_s3_bucket_name: str,
        n_speakers: int,
        aws_region: str,
        oneai_api_key: str,
        oneai_skills: str
) -> AppInstance:
    """Get an instance of the chat-analytics-app."""
    client = Steamship(
        api_key=api_key,
        api_base="https://api.steamship.com/api/v1/",
        app_base="https://steamship.run/",
        web_base="https://app.steamship.com/"
    )
    config = {
        "aws_access_key_id": aws_access_key_id,
        "aws_secret_access_key": aws_secret_access_key,
        "aws_s3_bucket_name": aws_s3_bucket_name,
        "speaker_detection": True,
        "n_speakers": n_speakers,
        "aws_region": aws_region,
        "oneai_api_key": oneai_api_key,
        "oneai_skills": oneai_skills,
    }
    return AppInstance.create(client, app_handle=APP_HANDLE, config=config).data


def analyze_podcast(podcast_url: str, n_speakers: int):
    app_instance = get_app_instance(
        api_key=st.secrets["steamship_api_key_audio"],
        aws_access_key_id=st.secrets["aws_access_key_id"],
        aws_secret_access_key=st.secrets["aws_secret_access_key"],
        aws_s3_bucket_name=st.secrets["aws_s3_bucket_name"],
        n_speakers=n_speakers,
        aws_region=st.secrets["aws_region"],
        oneai_api_key=st.secrets["oneai_api_key"],
        oneai_skills=st.secrets["oneai_skills"])
    response = app_instance.post("analyze_youtube", url=podcast_url)
    block = Block.parse_obj(response.data)
    tags = block.tags
    conversation = block.text
    return conversation, tags, block


def visualize_tags(conversation, tags, title: str, tag_kind: str, tag_title: str, show_label: bool = True,
                   show_tag: bool = True):
    st.markdown(f"### {title}")
    tags = [tag for tag in tags if tag.kind == tag_kind]
    try:
        tags = sorted(tags, key=lambda x: x.start_idx)
    except TypeError:
        pass
    df = pd.DataFrame([{
        "Label": tag.name,
        tag_title: conversation[tag.start_idx:tag.end_idx]}
        for i, tag in enumerate(tags)])
    if not show_label:
        df = df.drop(["Label"], axis=1)
    if not show_tag:
        df = df.drop([tag_title], axis=1)
    st.dataframe(df)
