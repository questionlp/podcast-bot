# Copyright (c) 2022-2024 Linh Pham
# podcast-bot is released under the terms of the MIT License
# SPDX-License-Identifier: MIT
#
# vim: set noai syntax=python ts=4 sw=4:
"""Application Configuration Module."""
import json
import sys
from pathlib import Path
from typing import NamedTuple, Any

_DEFAULT_USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64; rv:132.0) Gecko/20100101 Firefox/132.0"


class BlueskySettings(NamedTuple):
    """Bluesky Client Settings."""

    username: str
    app_password: str
    api_url: str
    template_path: str
    template_file: str
    max_description_length: int


class MastodonSettings(NamedTuple):
    """Mastodon Client Settings."""

    api_url: str
    use_oauth: bool = False
    secrets_file: str | None
    client_secret: str | None
    access_token: str | None
    template_path: str
    template_file: str
    max_description_length: int


class FeedSettings(NamedTuple):
    """Podcast Feed Settings."""

    name: str
    short_name: str
    feed_url: str
    enabled: bool
    recent_days: int
    max_episodes: int
    guid_filter: str
    bluesky_settings: BlueskySettings | None
    mastodon_settings: MastodonSettings | None


class AppSettings(NamedTuple):
    """Application Settings."""

    database_file: str = "dbfiles/feed_info.sqlite3"
    database_clean_days: int = 90
    log_file: str = "logs/app.log"
    user_agent: str = _DEFAULT_USER_AGENT
    feeds: list[FeedSettings] | None = None


class AppConfig:
    """Application Configuration Settings."""

    def parse_bluesky(self, bluesky_settings: dict[str, Any]) -> BlueskySettings | None:
        """Parse Bluesky settings from a dictionary."""

        if not bluesky_settings:
            return None

        _username: str | None = bluesky_settings.get("username", None)
        if not _username:
            raise ValueError("Missing or blank Bluesky username.")

        _app_password: str | None = bluesky_settings.get("app_password", None)
        if not _app_password:
            raise ValueError("Missing or blank Bluesky app password.")

        return BlueskySettings(
            username=_username.strip(),
            app_password=_app_password.strip(),
            api_url=bluesky_settings.get("api_url", "https://bsky.social").strip(),
            template_path=bluesky_settings.get("template_path", "templates").strip(),
            template_file=bluesky_settings.get("template_file", "post-bluesky.txt.jinja").strip(),
            max_description_length=int(bluesky_settings.get("max_description_length", 150)),
        )

    def parse_mastodon(self, mastodon_settings: dict[str, Any]) -> MastodonSettings | None:
        """Parse Mastodon settings from a dictionary."""

        if not mastodon_settings:
            return None

        _api_url: str | None = mastodon_settings("api_url", None)
        if not _api_url:
            raise ValueError("Missing or blank Mastodon API URL.")

        _use_oauth: bool = mastodon_settings("use_oauth", False)
        _secrets_file: str | None = mastodon_settings("secrets_file", None)
        _client_secret: str | None = mastodon_settings("client_secret", None)
        _access_token: str | None = mastodon_settings("access_token", None)

        if _use_oauth and not _secrets_file:
            raise ValueError(
                "Missing or blank Mastodon secrets file. Required for OAuth authentication."
            )

        if not _use_oauth and not _client_secret:
            raise ValueError("Missing or blank Mastodon client secret.")

        if not _use_oauth and not _access_token:
            raise ValueError("Missing or blank Mastodon access token.")

        return MastodonSettings(
            api_url=_api_url.strip(),
            use_oauth=_use_oauth,
            secrets_file=_secrets_file.strip(),
            client_secret=_client_secret.strip(),
            access_token=_access_token.strip(),
            template_path=mastodon_settings.get("template_path", "templates").strip(),
            template_file=mastodon_settings.get("template_file", "post-mastodon.txt.jinja").strip(),
            max_description_length=int(mastodon_settings.get("max_description_length", 250)),
        )

    def parse_feed(self, feed_settings: list[dict[str, Any]]) -> FeedSettings | None:
        """Parse podcast feed settings from a dictionary."""

        if "bluesky_settings" not in feed_settings and "mastodon_settings" not in feed_settings:
            raise ValueError(
                "Bluesky and Mastodon settings are not defined. "
                "Either Bluesky or Mastodon settings are required."
            )

        _bluesky_settings: BlueskySettings | None = self.parse_bluesky(
            feed_settings.get("bluesky_settings", None)
        )
        _mastodon_settings: MastodonSettings | None = self.parse_mastodon(
            feed_settings.get("mastodon_settings", None)
        )

        if not _bluesky_settings and not _mastodon_settings:
            raise ValueError(
                "Bluesky and Mastodon settings are invalid. "
                "Either Bluesky or Mastodon settings are required."
            )

        _name: str | None = feed_settings.get("name", None)
        if not _name:
            raise ValueError("Missing or blank podcast name.")

        _short_name: str | None = feed_settings.get("short_name", None)
        if not _short_name:
            raise ValueError("Missing or blank podcast short name.")

        _feed_url: str | None = feed_settings.get("feed_url", None)
        if not _feed_url:
            raise ValueError("Missing or blank podcast feed URL.")

        return FeedSettings(
            name=_name.strip(),
            short_name=_short_name.strip(),
            feed_url=_feed_url.strip(),
            enabled=bool(feed_settings.get("enabled", True)),
            recent_days=int(feed_settings.get("recent_days", 5)),
            max_episodes=int(feed_settings.get("max_episodes", 20)),
            guid_filter=str(feed_settings.get("guid_filter", "")).strip(),
            bluesky_settings=_bluesky_settings,
            mastodon_settings=_mastodon_settings,
        )

    def parse_app(self, settings_file: str = "settings.json") -> AppSettings:
        """Parse application configuration file."""

        settings_path = Path.cwd() / settings_file
        with settings_path.open(mode="r", encoding="utf-8") as _settings_file:
            _app_settings = json.load(_settings_file)
            if not _app_settings:
                print("ERROR: Application settings JSON file could not be parsed.")
                sys.exit(1)

            if not isinstance(_app_settings, list):
                print("ERROR: Application settings JSON file is not valid.")
                sys.exit(1)

        if "feeds" not in _app_settings:
            raise ValueError("Podcast feeds setting is not been defined.")

        _feeds = _app_settings.get("feeds", [])
        if not _feeds:
            raise ValueError("Podcast feeds setting does not contain any feeds.")

        _feeds_settings = []
        for _feed in _feeds:
            _feeds_settings.append(self.parse_feed(feed_settings=_feed))

        if not _feeds_settings:
            raise ValueError("Podcast feeds setting could not be parsed.")

        return AppSettings(
            database_file=str(
                _app_settings.get("database_file", "dbfiles/feed_info.sqlite3")
            ).strip(),
            database_clean_days=int(_app_settings.get("database_clean_days", 90)),
            log_file=str(_app_settings.get("log_file", "logs/app.log")).strip(),
            user_agent=str(_app_settings.get("user_agent", _DEFAULT_USER_AGENT)).strip(),
            feeds=_feeds_settings,
        )

    def __str__(self) -> str:
        return self.__class__.__name__
