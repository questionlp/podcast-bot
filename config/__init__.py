# Copyright (c) 2022-2024 Linh Pham
# podcast-bot is released under the terms of the MIT License
# SPDX-License-Identifier: MIT
#
# vim: set noai syntax=python ts=4 sw=4:
"""Application Configuration Module."""
import json
import sys
from pathlib import Path
from typing import NamedTuple

_DEFAULT_USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64; rv:130.0) Gecko/20100101 Firefox/130.0"


class BlueskySettings(NamedTuple):
    """Bluesky Client Settings."""

    username: str
    app_password: str
    api_url: str = "https://bsky.social"
    template_file: str = "templates/post-bluesky.txt.jinja"
    max_description_length: int = 150


class MastodonSettings(NamedTuple):
    """Mastodon Client Settings."""

    api_url: str
    use_oauth: bool = False
    secrets_file: str | None = "secrets/usercred.secret"
    client_secret: str | None = None
    access_token: str | None = None
    template_file: str = "templates/post-mastodon.txt.jinja"
    max_description_length: int = 250


class FeedSettings(NamedTuple):
    """Podcast Feed Settings."""

    name: str
    short_name: str
    feed_url: str
    enabled: bool = True
    recent_days: int = 5
    max_episodes: int = 20
    guid_filter: str = ""
    bluesky_settings: BlueskySettings | None = None
    mastodon_settings: MastodonSettings | None = None


class AppSettings(NamedTuple):
    """Application Settings."""

    database_file: str = "dbfiles/feed_info.sqlite3"
    database_clean_days: int = 90
    log_file: str = "logs/app.log"
    user_agent: str = _DEFAULT_USER_AGENT
    feeds: list[FeedSettings] | None = None


class AppConfig:
    """Application podcast feeds settings."""

    def parse(self, feeds_file: str = "settings.json") -> list[FeedSettings]:
        """Parse application settings."""
        feeds_path = Path.cwd() / feeds_file
        with feeds_path.open(mode="r", encoding="utf-8") as _feeds_file:
            feeds = json.load(_feeds_file)
            if not feeds:
                print("ERROR: Podcast Feeds Settings JSON file could not be parsed.")
                sys.exit(1)

            if not isinstance(feeds, list):
                print("ERROR: Podcast Feeds Settings JSON file is not valid.")
                sys.exit(1)

        feeds_settings: list[FeedSettings] = []
        for podcast_feed in feeds:
            feed = dict(podcast_feed)
            if (
                "feed_name" not in feed
                or "podcast_name" not in feed
                or "podcast_feed_url" not in feed
            ):
                print("ERROR: Podcast feed information is not valid.")
                sys.exit(1)

            if "mastodon_api_base_url" not in feed:
                print("ERROR: Feed settings does not contain a Mastodon API base URL.")
                sys.exit(1)

            if "mastodon_use_secrets_file" in feed:
                use_secrets_file = bool(feed["mastodon_use_secrets_file"])
            else:
                use_secrets_file = True

            secrets_file = None
            if use_secrets_file and "mastodon_secret" in feed:
                secrets_file = feed["mastodon_secret"].strip()
            elif use_secrets_file and "mastodon_secrets_file" in feed:
                secrets_file = feed["mastodon_secrets_file"].strip()

            if use_secrets_file and not secrets_file:
                print("ERROR: Mastodon secrets file path setting not found.")
                sys.exit(1)

            if not use_secrets_file and (
                "mastodon_client_secret" not in feed or "mastodon_access_token" not in feed
            ):
                print("ERROR: Mastodon client secret or access token setting not found.")

            feed_settings = FeedSettings(
                name=feed["feed_name"].strip(),
                podcast_name=feed["podcast_name"].strip(),
                enabled=bool(feed.get("enabled", True)),
                feed_url=feed["podcast_feed_url"].strip(),
                mastodon_use_secrets_file=use_secrets_file,
                mastodon_secrets_file=(secrets_file if use_secrets_file and secrets_file else None),
                mastodon_client_secret=feed.get("mastodon_client_secret", "").strip(),
                mastodon_access_token=feed.get("mastodon_access_token", "").strip(),
                mastodon_api_base_url=feed.get("mastodon_api_base_url", "").strip(),
                database_file=feed.get("database_file", "feed_info.sqlite3").strip(),
                database_clean_days=int(feed.get("database_clean_days", 90)),
                log_file=feed.get("log_file", "logs/podcast_bot.log").strip(),
                recent_days=int(feed.get("recent_days", 90)),
                max_episodes=int(feed.get("max_episodes", 50)),
                max_description_length=int(feed.get("max_description_length", 275)),
                guid_filter=feed.get("podcast_guid_filter", "").strip(),
                user_agent=feed.get("user_agent", _DEFAULT_USER_AGENT).strip(),
                template_directory=feed.get("template_directory", "templates").strip(),
                template_file=feed.get("template_file", "post.txt.jinja").strip(),
            )
            feeds_settings.append(feed_settings)

        return feeds_settings

    def __str__(self) -> str:
        return self.__class__.__name__
