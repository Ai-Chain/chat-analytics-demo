"""Streamlit demo of the audio-analytics app."""

import pandas as pd
import streamlit as st
from steamship import SteamshipError

from src.audio_utils import analyze_podcast, visualize_tags

PLACEHOLDER_PODCAST_URL = "https://www.youtube.com/watch?v=-UX0X45sYe4"

ENVIRONMENT = "prod"


def main():
    st.title("Podcast insights 👀")
    st.text("Welcome to my first podcast analytics app!")

    podcast_url = st.text_input(label="Youtube url", placeholder=PLACEHOLDER_PODCAST_URL)
    podcast_url = podcast_url or PLACEHOLDER_PODCAST_URL
    with st.expander("Expert settings"):
        n_speakers = st.number_input(label="Number of speakers", value=2)

    on_parse = st.button(label="Go! 🥊")
    if on_parse:
        st.video(podcast_url)

        with st.spinner(text="Analyzing podcast 🔬 ..."):
            conversation, tags, block = analyze_podcast(podcast_url, n_speakers)

            if block:
                with st.expander("Transcription:"):
                    try:
                        st.markdown(conversation)
                    except SteamshipError as e:
                        st.error(f"Transcription failed : {e}")

                with st.expander("Structured transcription:"):
                    speaker_tags = [tag for tag in tags if tag.kind == "speaker"]
                    speaker_tags = sorted(speaker_tags, key=lambda x: x.start_idx)
                    d = []
                    start_idx_set = set()
                    for speaker_tag in speaker_tags:
                        if speaker_tag.start_idx not in start_idx_set:
                            start_idx_set.add(speaker_tag.start_idx)
                            d.append(speaker_tag)

                    speaker_tags = d
                    if speaker_tags:
                        speaker_tags = sorted(speaker_tags, key=lambda x: x.start_idx)
                        text = [
                            {
                                "speaker": speaker_tag.name,
                                "utterance": conversation[speaker_tag.start_idx: speaker_tag.end_idx],
                            }
                            for speaker_tag in speaker_tags
                        ]
                        st.dataframe(pd.DataFrame(text))

                st.subheader("Summary")
                highlights = [tag for tag in tags if tag.kind == "summarize"]
                highlights = sorted(highlights, key=lambda x: x.start_idx)
                st.markdown("\n".join([highlight.name for highlight in highlights]))

                visualize_tags(conversation, tags, "Topic segments:", "dialogue-segmentation", "Segment",
                               show_label=False)

                visualize_tags(conversation, tags, "Highlights:", "highlights", "Highlight", show_label=False)

                visualize_tags(conversation, tags, "Emotions:", "emotions", "Emotion")

                visualize_tags(conversation, tags, "Entities:", "entities", "Entity")

                visualize_tags(conversation, tags, "Names:", "names", "Name")

                visualize_tags(conversation, tags, "Topics:", "article-topics", "Topic", show_tag=False)

                visualize_tags(conversation, tags, "Keywords:", "keywords", "Keyword", show_label=False)

                visualize_tags(conversation, tags, "Sentiments:", "sentiments", "Sentiment")

                visualize_tags(conversation, tags, "Numbers:", "numbers", "Number")


if __name__ == '__main__':
    main()
