import re
import requests

from urllib.parse import urlparse

IDENTITY_PATH = ("https://services.sentinel-hub.com/oauth/auth?client_id=c525444c-6bd4-4290-b56f-11b792491465"
                 "&redirect_uri=https%3A%2F%2Fapps.sentinel-hub.com%2Fmosaic-hub%2Foauth2callback.html"
                 "&scope=&response_type=token&state=")
LOGIN_PATH = "https://services.sentinel-hub.com/oauth/auth/login"
SESSION_NAME = "session"
CSRT_PATTERN = re.compile("value=\"(.*)\" name=\"csrt\">")
LOCATION_HEADER = "Location"


def get_token(username, password):
    session = requests.Session()
    resp = session.get(IDENTITY_PATH)
    csrt = CSRT_PATTERN.findall(resp.text)
    if not csrt:
        exit(0)

    payload = {"csrt": csrt[0], "username": username, "password": password}
    resp = session.post(LOGIN_PATH, data=payload, allow_redirects=False)

    if LOCATION_HEADER in resp.headers:
        url = urlparse(resp.headers[LOCATION_HEADER])
        return url.fragment.split("&")[0].split("=")[1]
    else:
        raise ValueError("Wrong username or password")

