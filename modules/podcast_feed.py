# Copyright (c) 2022-2024 Linh Pham
# podcast-bot is released under the terms of the MIT License
# SPDX-License-Identifier: MIT
#
# vim: set noai syntax=python ts=4 sw=4:
# pylint: disable=R1732
"""Podcast Feed Module."""
import datetime
from typing import Any

import podcastparser
import requests
from dateutil import parser
from dateutil.parser import ParserError
from settings import _DEFAULT_USER_AGENT


class PodcastFeed:
    """Podcast Feed Fetcher."""

    def fetch(
        self, feed_url: str, max_episodes: int = 50, user_agent: str = _DEFAULT_USER_AGENT
    ) -> list[dict[str, Any]] | None:
        """Fetch items from the requested podcast feed."""
        with requests.get(
            url=feed_url, headers={"User-Agent": user_agent}, stream=True, timeout=30
        ) as response:
            response.raw.decode_content = True
            _feed: dict[str, Any] = podcastparser.parse(
                url=feed_url, stream=response.raw, max_episodes=max_episodes
            )

        return _feed.get("episodes")

    def last_modified(
        self, feed_url: str, user_agent: str = _DEFAULT_USER_AGENT
    ) -> datetime.datetime | None:
        """Retrieve last modified date and time for the requested feed."""
        feed: requests.Response = requests.head(
            url=feed_url, headers={"User-Agent": user_agent}, timeout=30, allow_redirects=True
        )

        if feed and feed.status_code == 200:
            _last_modified: str | None = feed.headers.get("Last-Modified", None)
            if _last_modified:
                try:
                    return parser.parse(_last_modified)
                except ParserError:
                    return datetime.datetime.now(datetime.timezone.utc)

        return datetime.datetime.now(datetime.timezone.utc)

    def __str__(self):
        return self.__class__.__name__
