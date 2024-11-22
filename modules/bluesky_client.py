# Copyright (c) 2024 Linh Pham
# podcast-bot is released under the terms of the MIT License
# SPDX-License-Identifier: MIT
#
# vim: set noai syntax=python ts=4 sw=4:
"""Bluesky Client Module."""
from atproto import Client, client_utils


class BlueskyClient:
    """Client for Bluesky."""

    def __init__(self, api_url: str, username: str, app_password: str) -> None:
        if api_url and username and app_password:
            self.login(api_url=api_url, username=username, app_password=app_password)

    def login(self, api_url: str, username: str, app_password: str) -> None:
        """Log into Bluesky."""
        self._client = Client(base_url=api_url)
        self._client.login(login=username, password=app_password)

    def post(self, body: str, episode_url: str) -> None:
        """Log into Bluesky and publish a new post."""
        _post = (
            client_utils.TextBuilder()
            .text(body)
            .text("\n")
            .link(text="Episode Download", url=episode_url)
        )
        _ = self._client.send_post(text=_post)
