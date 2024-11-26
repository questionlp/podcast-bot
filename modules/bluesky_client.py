# Copyright (c) 2024 Linh Pham
# podcast-bot is released under the terms of the MIT License
# SPDX-License-Identifier: MIT
#
# vim: set noai syntax=python ts=4 sw=4:
"""Bluesky Client Module."""
import sqlite3
from pathlib import Path
from sqlite3 import Connection, Cursor

from atproto import Client, client_utils


class BlueskyClientSession:
    """Bluesky Client Session."""

    def __init__(self, session_file: str = None) -> None:
        """Class initialization method."""
        if session_file and not Path(session_file).exists():
            self.initialize(session_file)
            self.connection: Connection = sqlite3.connect(session_file)
        if session_file and Path(session_file).exists():
            self.connection: Connection = sqlite3.connect(session_file)
            self._migrate()

    def initialize(self, db_file: str) -> None:
        """Initialize feed database with the required table."""
        if Path(db_file).exists():
            return

        database: Connection = sqlite3.connect(db_file)
        database.execute(
            "CREATE TABLE bluesky_sessions(username str PRIMARY KEY, session_token str)"
        )
        database.commit()
        database.close()

    def _migrate(self) -> None:
        """Run any required database migration steps."""

    def connect(self, session_file: str) -> None:
        """Returns a connection to the feed database."""
        if Path(session_file).exists():
            self.connection = sqlite3.connect(session_file)

    def retrieve(self, username: str) -> str | None:
        """Retrieve stored Bluesky client session token."""
        if username:
            result: Cursor = self.connection.execute(
                "SELECT session_token FROM bluesky_sessions WHERE username = ? LIMIT 1",
                (username,),
            )
            _token = result.fetchone()

            if _token:
                return _token[0]

            return None

        return None

    def save(self, username: str, session_token: str) -> None:
        """Update or insert Bluesky client session token."""
        if username and session_token:
            self.connection.execute(
                """
                INSERT INTO bluesky_sessions (username, session_token)
                VALUES (?, ?)
                ON CONFLICT (username) DO
                UPDATE
                SET username = excluded.username,
                session_token = excluded.session_token
                """,
                (username, session_token),
            )
            self.connection.commit()


class BlueskyClient:
    """Client for Bluesky."""

    def __init__(
        self,
        api_url: str,
        username: str,
        app_password: str,
        session_file: str,
        use_session_token: bool,
    ) -> None:
        self._api_url: str = api_url
        self._session_file: str = session_file
        self._username: str = username
        self._use_session_token: bool = use_session_token

        if api_url and username and app_password:
            self.login(
                api_url=api_url,
                username=username,
                app_password=app_password,
                session_file=session_file,
                use_session_token=use_session_token,
            )

    def login(
        self,
        api_url: str,
        username: str,
        app_password: str,
        session_file: str,
        use_session_token: bool,
    ) -> None:
        """Log into Bluesky."""
        self._api_url: str = api_url
        self._session_file: str = session_file
        self._username = username
        self._use_session_token: bool = use_session_token

        self._client = Client(base_url=api_url)
        if use_session_token:
            _session = BlueskyClientSession(session_file=session_file)
            _session_token: str | None = _session.retrieve(username=username)

            if _session_token:
                self._client.login(session_string=_session_token)
        else:
            self._client.login(login=username, password=app_password)

    def post(self, body: str, episode_url: str) -> None:
        """Log into Bluesky and publish a new post."""
        _post: client_utils.TextBuilder = (
            client_utils.TextBuilder()
            .text(body)
            .text("\n")
            .link(text="Episode Download", url=episode_url)
        )
        _ = self._client.send_post(text=_post)

    def save_session(self) -> None:
        """Save session token for current user."""
        if self._use_session_token:
            _session = BlueskyClientSession(session_file=self._session_file)
            _session_token = self._client.export_session_string()
            _session.save(username=self._username, session_token=_session_token)
