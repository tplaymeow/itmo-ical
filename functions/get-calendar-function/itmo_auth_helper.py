import html
import os
import re
import urllib.parse
from base64 import urlsafe_b64encode
from hashlib import sha256
import logging

import requests

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

_CLIENT_ID = "student-personal-cabinet"
_REDIRECT_URI = "https://my.itmo.ru/login/callback"
_PROVIDER = "https://id.itmo.ru/auth/realms/itmo"


def generate_code_verifier() -> str:
    return urlsafe_b64encode(os.urandom(40)).rstrip(b"=").decode("ascii")


def get_code_challenge(code_verifier: str) -> str:
    digest = sha256(code_verifier.encode("ascii")).digest()
    return urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")


def extract_form_action(text: str) -> str:
    session_code = re.search(r"session_code=([^&\"']+)", text).group(1)
    execution = re.search(r"execution=([^&\"']+)", text).group(1)
    tab_id = re.search(r"tab_id=([^&\"']+)", text).group(1)
    return f"{_PROVIDER}/login-actions/authenticate?session_code={session_code}&execution={execution}&tab_id={tab_id}&client_id={_CLIENT_ID}"


def extract_auth_code(redirect_url: str) -> str:
    query = urllib.parse.urlparse(redirect_url).query
    redirect_params = urllib.parse.parse_qs(query)
    return redirect_params["code"][0]


def get_access_token(login: str, password: str) -> str:
    logger.info("Generating code_verifier and code_challenge")
    code_verifier = generate_code_verifier()
    code_challenge = get_code_challenge(code_verifier)

    logger.info("Fetching auth page")
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

    logger.info("Extraction form action")
    form_action = extract_form_action(auth_resp.text)
    logger.info(f"Extracted action url: {form_action}")

    logger.info("Requesting auth information")
    form_resp = requests.post(
        url=form_action,
        data={"username": login, "password": password},
        cookies=auth_resp.cookies,
        allow_redirects=False,
    )
    if form_resp.status_code != 302:
        raise ValueError(f"Wrong Keycloak form response: {form_resp.status_code} {form_resp.text}")

    logger.info("Extracting auth code")
    auth_code = extract_auth_code(form_resp.headers["Location"])

    logger.info("Fetching auth tokens")
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
