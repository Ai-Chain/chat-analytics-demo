"""Streamlit demo of the audio-analytics app."""

import streamlit as st
from steamship import File, Steamship

GUEST_TO_FILE_ID = {
    "Elon Musk": '1169DB52-2AF4-49BF-A8EC-82393AF77715'
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
            names = {tag.value["value"] for tag in tags if tag.kind == "names"}
            selected_names = st.multiselect("Topic", options=names, default=["SpaceX"])

            for name_tag in dict(sorted({
                                            tag.start_idx: tag for tag in tags if
                                            tag.kind == "names" and tag.value["value"] in selected_names
                                        }.items(), key=lambda x: x)).values():
                timestamp_tags = [
                    tag
                    for tag in tags
                    if tag.kind == "timestamp"
                       and tag.start_idx >= name_tag.start_idx
                       and tag.end_idx <= name_tag.end_idx
                ]
                if timestamp_tags:
                    t_start = float(timestamp_tags[0].value["start_time"])

                    st.subheader(name_tag.value["value"])
                    st.write(f"https://youtu.be/ycPr5-27vSI?t={t_start:.0f}")
                    st.video(data=f"https://youtu.be/ycPr5-27vSI?t={t_start:.0f}", start_time=int(t_start))
                else:
                    st.write("Nothing found 😭")


if __name__ == '__main__':
    main()
