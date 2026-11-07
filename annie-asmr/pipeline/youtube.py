"""YouTube Data + Analytics API sign-in.

On the Mac: one browser sign-in, token kept in .secrets/.
In a cloud session: set YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET and YOUTUBE_REFRESH_TOKEN as environment
variables in the cloud environment's settings (never in chat or git). See README 'Cloud access'.
"""
from __future__ import annotations

import os

from .config import project_path

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/youtube.force-ssl",      # posting your approved comment replies
    "https://www.googleapis.com/auth/yt-analytics.readonly",
]


def credentials():
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
    except ImportError:
        raise SystemExit("Install the YouTube libraries first: pip install -r requirements.txt")
    env_refresh = os.environ.get("YOUTUBE_REFRESH_TOKEN", "").strip()
    if env_refresh:
        missing = [k for k in ("YOUTUBE_CLIENT_ID", "YOUTUBE_CLIENT_SECRET") if not os.environ.get(k, "").strip()]
        if missing:
            raise SystemExit(f"YOUTUBE_REFRESH_TOKEN is set but {', '.join(missing)} is not. Add it in the "
                             "cloud environment settings.")
        creds = Credentials(None, refresh_token=env_refresh, token_uri="https://oauth2.googleapis.com/token",
                            client_id=os.environ["YOUTUBE_CLIENT_ID"].strip(),
                            client_secret=os.environ["YOUTUBE_CLIENT_SECRET"].strip())
        creds.refresh(Request())
        return creds
    secrets = project_path(os.environ.get("YOUTUBE_CLIENT_SECRETS", ".secrets/client_secret.json"))
    token = project_path(os.environ.get("YOUTUBE_TOKEN", ".secrets/youtube-token.json"))
    creds = None
    if token.exists():
        creds = Credentials.from_authorized_user_file(str(token), SCOPES)
    if creds and creds.valid:
        return creds
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        if not secrets.exists():
            raise SystemExit(f"No OAuth client at {secrets}. See README: 'YouTube API setup'.")
        flow = InstalledAppFlow.from_client_secrets_file(str(secrets), SCOPES)
        creds = flow.run_local_server(port=0, prompt="consent")
    token.parent.mkdir(parents=True, exist_ok=True)
    token.write_text(creds.to_json())
    os.chmod(token, 0o600)
    return creds


def _build():
    try:
        from googleapiclient.discovery import build
    except ImportError:
        raise SystemExit("Install the YouTube libraries first: pip install -r requirements.txt")
    return build


def data_api():
    build = _build()
    return build("youtube", "v3", credentials=credentials(), cache_discovery=False)


def analytics_api():
    build = _build()
    return build("youtubeAnalytics", "v2", credentials=credentials(), cache_discovery=False)


def my_channel(yt) -> dict:
    items = yt.channels().list(part="id,snippet,statistics,contentDetails", mine=True).execute().get("items", [])
    if not items:
        raise SystemExit("The signed-in Google account has no YouTube channel. Sign in as Annie ASMR.")
    return items[0]
