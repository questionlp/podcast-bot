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

    def __init__(self, db_file: str = None) -> None:
        """Class initialization method."""
        if db_file and not Path(db_file).exists():
            self.initialize(db_file)
            self.connection: Connection = sqlite3.connect(db_file)
        if db_file and Path(db_file).exists():
            self.connection: Connection = sqlite3.connect(db_file)
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

    def connect(self, db_file: str) -> None:
        """Returns a connection to the feed database."""
        if Path(db_file).exists():
            self.connection = sqlite3.connect(db_file)

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
        self, api_url: str, username: str, app_password: str, db_file: str
    ) -> None:
        self._api_url: str = api_url
        self._db_file: str = db_file
        self._username: str = username

        if api_url and username and app_password:
            self.login(
                api_url=api_url,
                username=username,
                app_password=app_password,
                db_file=db_file,
            )

    def login(
        self, api_url: str, username: str, app_password: str, db_file: str
    ) -> None:
        """Log into Bluesky."""
        self._api_url: str = api_url
        self._db_file: str = db_file
        self._username = username

        _session = BlueskyClientSession(db_file=db_file)
        _session_token: str | None = _session.retrieve(username=username)

        self._client = Client(base_url=api_url)
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
        _session = BlueskyClientSession(db_file=self._db_file)
        _session_token = self._client.export_session_string()
        _session.save(username=self._username, session_token=_session_token)
