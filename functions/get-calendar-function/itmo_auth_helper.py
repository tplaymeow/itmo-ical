import html
import os
import re
import urllib.parse
from base64 import urlsafe_b64encode
from hashlib import sha256

import requests

_CLIENT_ID = "student-personal-cabinet"
_REDIRECT_URI = "https://my.itmo.ru/login/callback"
_PROVIDER = "https://id.itmo.ru/auth/realms/itmo"
_FORM_ACTION_REGEX = re.compile(r'<form\s+.*?\s+action="(?P<action>.*?)"', re.DOTALL)


def generate_code_verifier():
    code_verifier = urlsafe_b64encode(os.urandom(40)).decode("utf-8")
    return re.sub("[^a-zA-Z0-9]+", "", code_verifier)


def get_code_challenge(code_verifier: str):
    code_challenge_bytes = sha256(code_verifier.encode("utf-8")).digest()
    code_challenge = urlsafe_b64encode(code_challenge_bytes).decode("utf-8")
    return code_challenge.replace("=", "")  # remove base64 padding


def extract_form_action(text: str) -> str:
    form_action_match = _FORM_ACTION_REGEX.search(text)
    return html.unescape(form_action_match.group("action"))


def extract_auth_code(redirect_url: str) -> str:
    query = urllib.parse.urlparse(redirect_url).query
    redirect_params = urllib.parse.parse_qs(query)
    return redirect_params["code"][0]


def get_access_token(login: str, password: str) -> str:
    code_verifier = generate_code_verifier()
    code_challenge = get_code_challenge(code_verifier)

    auth_resp = requests.get(
        _PROVIDER + "/protocol/openid-connect/auth",
        params={
            "protocol": "oauth2",
            "response_type": "code",
            "client_id": _CLIENT_ID,
            "redirect_uri": _REDIRECT_URI,
            "scope": "openid",
            "state": "im_not_a_browser",
            "code_challenge_method": "S256",
            "code_challenge": code_challenge,
        },
    )
    auth_resp.raise_for_status()

    form_action = extract_form_action(auth_resp.text)

    form_resp = requests.post(
        url=form_action,
        data={"username": login, "password": password},
        cookies=auth_resp.cookies,
        allow_redirects=False,
    )
    if form_resp.status_code != 302:
        raise ValueError(f"Wrong Keycloak form response: {form_resp.status_code} {form_resp.text}")

    auth_code = extract_auth_code(form_resp.headers["Location"])

    token_resp = requests.post(
        url=_PROVIDER + "/protocol/openid-connect/token",
        data={
            "grant_type": "authorization_code",
            "client_id": _CLIENT_ID,
            "redirect_uri": _REDIRECT_URI,
            "code": auth_code,
            "code_verifier": code_verifier,
        },
        allow_redirects=False,
    )
    token_resp.raise_for_status()
    return token_resp.json()["access_token"]
