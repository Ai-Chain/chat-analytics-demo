import asyncio
import base64
import random
import time
from pathlib import Path
from typing import Union, Dict

import gspread
import streamlit as st
from httpx_oauth.clients.google import GoogleOAuth2
from httpx_oauth.oauth2 import GetAccessTokenError

USAGE_LIMIT = 10
APP_ID = "chat"


def get_worksheet():
    with Path("gcred_test.json").open("w") as f:
        f.write(st.secrets["gcred_json"])
    gc = gspread.service_account(filename='./gcred_test.json')
    sh = gc.open_by_key('1Dnf4gqdicSXwL4-2laeIYGR0bOeLU6tI_GtxGme4m7s')
    worksheet = sh.worksheet("Contacts")
    return worksheet


def check_usage(usage_stats: Dict[str, Union[str, int]]):
    placeholder = st.session_state["placeholder"]
    if usage_stats:
        if usage_stats[APP_ID] > USAGE_LIMIT:
            placeholder.markdown(
                f"Signed in as {usage_stats['e-mail']} - Usage quota exceeded, [contact support](mailto:developers@steamship.com) for more credits.")
        else:
            placeholder.markdown(
                f"Signed in as {usage_stats['e-mail']} - Usage quota {usage_stats[APP_ID]}/{USAGE_LIMIT}")
    else:
        placeholder.markdown("Not logged in yet")


def get_user_stats(email: str):
    worksheet = get_worksheet()
    labels = worksheet.row_values(1)

    user_stats = worksheet.find(email, in_column=0, case_sensitive=False)
    if not user_stats:
        time.sleep(random.randint(0, 10))
        user_stats = worksheet.find(email, in_column=0, case_sensitive=False)

    if user_stats:
        user_id = user_stats.row
        usage_stats = worksheet.row_values(user_stats.row)
        print(usage_stats)
    else:
        usage_stats = [email] + [0] * (len(labels) - 1)
        worksheet.append_row(usage_stats)
        user_id = worksheet.find(email, in_column=0, case_sensitive=False).row

    usage_stats = {**{
        label: int(value) if isinstance(value, int) or value.isdigit() else value for label, value in
        zip(labels, usage_stats)
    }, "id": user_id}

    check_usage(usage_stats)
    return usage_stats


def update_usage():
    usage_stats = st.session_state["usage_stats"]
    print(f"Increasing usage for {usage_stats['e-mail']}")
    worksheet = get_worksheet()
    user_id = usage_stats["id"]
    usage_stats[APP_ID] += 1
    worksheet.update(f'A{user_id}:{user_id}', [list(usage_stats.values())[:-1]])

    st.session_state["usage_stats"] = usage_stats
    return check_usage(usage_stats)


def get_google_oauth_client():
    client_id = st.secrets["google_oauth_client_id"]
    client_secret = st.secrets["google_oauth_client_secret"]
    return GoogleOAuth2(client_id, client_secret)


def check_auth() -> None:
    client = get_google_oauth_client()

    redirect_uri = st.secrets["redirect_uri"]
    authorization_url = asyncio.run(
        client.get_authorization_url(
            redirect_uri, scope=["email", "profile"]
        )
    )

    if "user_email" not in st.session_state:
        try:
            code = st.experimental_get_query_params()["code"]
            token = asyncio.run(client.get_access_token(code, redirect_uri))

            if token.is_expired():
                show_login_prompt(authorization_url)
            else:
                _, user_email = asyncio.run(client.get_id_email(token["access_token"]))
                st.session_state["user_email"] = user_email

        except (KeyError, GetAccessTokenError):
            show_login_prompt(authorization_url)

    user_email = st.session_state["user_email"]
    user_stats = get_user_stats(user_email)
    st.session_state["usage_stats"] = user_stats


def show_login_prompt(authorization_url):
    st.markdown("Please sign in to use our app:")

    image = Path("google_login_button.png")
    file_ = image.open("rb")
    contents = file_.read()
    data_url = base64.b64encode(contents).decode("utf-8")
    file_.close()

    st.write(
        f"""<a target="_blank"
                                  href="{authorization_url}">
                                  <image src="data:image/gif;base64,{data_url}" width="200px">
                                  </a>""",
        unsafe_allow_html=True,
    )
    st.stop()
