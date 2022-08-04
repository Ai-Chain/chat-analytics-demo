"""Streamlit demo of the audio-analytics app."""
from collections import defaultdict, Counter

import pandas as pd
import streamlit as st
from steamship import File, Steamship

GUEST_TO_FILE_ID = {
    "Elon Musk": '1169DB52-2AF4-49BF-A8EC-82393AF77715',
}

GUEST_TO_YOUTUBE_URL = {
    "Elon Musk": "https://youtu.be/ycPr5-27vSI",
}

STYLED_EMOTIONS = {
    "happiness": "Happy 😁",
    "unknown": "Not sure 🤧"
}

STYLED_SENTIMENTS = {
    "POS": "Positive 👍",
    "NEG": "Negative 👎",
    "NEUTRAL": "Neutral 🇨🇭"
}

ENVIRONMENT = "prod"


@st.cache(ttl=3600, allow_output_mutation=True)
def load_files(client: Steamship):
    return {guest_id: File.get(client, file_id).data for guest_id, file_id in GUEST_TO_FILE_ID.items()}


def main():
    password = st.text_input(label="Password", type="password")
    if password == "LetTheMagicBegin":
        st.title("The Joe Rogan bible 📒")
        st.text("Let's see what Joe Rogan's guest have to say about specific topics!")

        client = Steamship(
            api_key=st.secrets["steamship_api_key_audio"],
            api_base="https://api.steamship.com/api/v1/",
            app_base="https://steamship.run/",
            web_base="https://app.steamship.com/"
        )
        guest_to_file = load_files(client)

        guest = st.selectbox("Guest", options=GUEST_TO_FILE_ID.keys())

        if not guest:
            st.markdown("Please select a guest.")
        else:
            file = guest_to_file[guest]
            block = file.blocks[0]
            tags = block.tags

            type = st.radio("Type", options=["Name", "Sentiment"])
            if type == "Name":

                names = {tag.value["value"] for tag in tags if tag.kind == "names"}
                selected_names = st.multiselect("Topic", options=names)

                topics = {
                    tag.name for tag in tags if tag.kind == "article-topics"
                }
                st.markdown(f"## {' #'.join(topics)}")
                if selected_names:
                    _list_clips_for_topics(guest, selected_names, tags)
            else:
                st.write("Sentiment")
                sentiments = {tag.name for tag in tags if tag.kind == "sentiments"}
                selected_sentiment = st.selectbox("Sentiment", options=sentiments,
                                                  format_func=lambda x: STYLED_SENTIMENTS[x])

                names = set()
                for sentiment_tag in dict(sorted({
                                                     tag.start_idx: tag
                                                     for tag in tags if
                                                     tag.kind == "sentiments" and tag.name in selected_sentiment
                                                 }.items(), key=lambda x: x)).values():
                    if name_tags := [tag.value["value"]
                                     for tag in tags if
                                     tag.kind == "names"
                                     and tag.start_idx >= sentiment_tag.start_idx
                                     and tag.end_idx <= sentiment_tag.end_idx]:
                        names.update(set(name_tags))

                st.write(f"{guest.title()} feels {STYLED_SENTIMENTS[selected_sentiment]} about the following topics:")
                df = pd.DataFrame(names, columns=["Topics"])
                st.table(df)

                _list_clips_for_topics(guest, names, tags)


def _list_clips_for_topics(guest, selected_names, tags):
    global_aggregated_tags = defaultdict(list)

    for name_tag in dict(sorted({
                                    tag.start_idx: tag
                                    for tag in tags if
                                    tag.kind == "names" and tag.value["value"] in selected_names
                                }.items(), key=lambda x: x)).values():

        timestamp_tags = sorted([
            tag
            for tag in tags
            if tag.kind == "timestamp"
               and tag.start_idx >= name_tag.start_idx
               and tag.end_idx <= name_tag.end_idx
        ], key=lambda x: float(x.value.get("start_time", 1_000_000) or 1_000_000))
        aggregated_overlapping_tags = defaultdict(list)

        for tag in [
            tag
            for tag in tags
            if tag.kind not in {"names", "article-topics", "timestamp"}
            if (tag.start_idx is None or tag.start_idx <= name_tag.start_idx)
               and (tag.end_idx is None or tag.end_idx >= name_tag.end_idx)
        ]:
            aggregated_overlapping_tags[tag.kind].append(
                {"name": tag.name, "value": tag.value}
            )

            global_aggregated_tags[tag.kind].append(
                {"name": tag.name, "value": tag.value}
            )

        if timestamp_tags:
            t_start = float(timestamp_tags[0].value["start_time"])

            st.subheader(name_tag.value["value"])

            emotion = aggregated_overlapping_tags.get('emotions', [{}])[0].get("name") or 'unknown'
            st.write(f"Emotion: {STYLED_EMOTIONS.get(emotion, emotion)}")
            sentiment = aggregated_overlapping_tags.get('sentiments', [{}])[0].get("name") or 'NEUTRAL'
            st.write(f"Sentiment: {STYLED_SENTIMENTS[sentiment]}")

            speaker = aggregated_overlapping_tags.get('speaker', [{}])[0].get("name") or 'unkown'
            st.write(f"Speaker: {'Joe Rogan' if speaker == 'spk_1' else 'Elon Musk'}")

            youtube_url = GUEST_TO_YOUTUBE_URL[guest]
            st.write(f"{youtube_url}?t={t_start:.0f}")
            st.video(data=f"{youtube_url}?t={t_start:.0f}", start_time=int(t_start))
        else:
            st.write("Nothing found 😭")

    st.markdown("#### Emotion report")
    c = Counter(emotion["name"] for emotion in global_aggregated_tags.get("emotions", []))
    st.write(dict(c.most_common(None)))

    st.markdown("#### Sentiment report")
    c = Counter(emotion["name"] for emotion in global_aggregated_tags.get("sentiments", []))
    st.write(dict(c.most_common(None)))


if __name__ == '__main__':
    main()
