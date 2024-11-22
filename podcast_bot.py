# Copyright (c) 2022-2024 Linh Pham
# podcast-bot is released under the terms of the MIT License
# SPDX-License-Identifier: MIT
#
# vim: set noai syntax=python ts=4 sw=4:
"""Podcast Feed Bot."""
import datetime
import logging
from argparse import Namespace
from pprint import pformat
from typing import Any

import modules.command
from modules.bluesky_client import BlueskyClient
from modules.database import FeedDatabase
from modules.formatting import format_bluesky_post, format_mastodon_post
from modules.mastodon_client import MastodonClient
from modules.podcast_feed import PodcastFeed
from modules.settings import AppConfig, AppSettings, FeedSettings

APP_VERSION: str = "1.0.0-alpha"
logger: logging.Logger = logging.getLogger(__name__)


def configure_logging(log_file: str = "logs/app.log", debug: bool = False) -> logging.FileHandler:
    """Configure application logging."""
    log_handler: logging.FileHandler = logging.FileHandler(log_file)
    log_format: logging.Formatter = logging.Formatter(
        fmt="%(asctime)s %(levelname)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )
    log_handler.setFormatter(log_format)
    if debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    logger.addHandler(log_handler)
    return log_handler


def retrieve_new_episodes(
    feed_episodes: list[dict[str, Any]],
    feed_database: FeedDatabase,
    feed_name: str = None,
    guid_filter: str = "",
    days: int = 7,
    dry_run: bool = False,
) -> list[dict[str, Any]]:
    """Retrieve new episodes from a podcast feed."""
    seen_guids: list[str] = feed_database.retrieve_guids(feed_name=feed_name)
    seen_enclosure_urls: list[str] = feed_database.retrieve_enclosure_urls(feed_name=feed_name)

    logger.debug("Seen GUIDs:\n%s", pformat(seen_guids, compact=True))
    logger.debug("Seen Enclosure URLs:\n%s", pformat(seen_enclosure_urls, compact=True))

    episodes: list[dict[str, Any]] = []

    for episode in feed_episodes:
        guid: str = episode["guid"]
        enclosure_url: str = episode["enclosures"][0]["url"].strip()
        publish_date: datetime.datetime = datetime.datetime.fromtimestamp(episode["published"])

        if datetime.datetime.now() - publish_date <= datetime.timedelta(days=days):
            # Only process episodes in which the GUID or the enclosure URL are
            # not in the episodes database table
            if guid not in seen_guids or enclosure_url not in seen_enclosure_urls:
                # Use guid_filter to match against the episode GUID to filter
                # out any random or incorrect GUIDs. This is a workaround to
                # reduce issues encountered with American Public Media feeds
                if guid_filter is not None and guid_filter.lower() in guid.lower():
                    info: dict[str, Any] = {
                        "guid": guid,
                        "published": publish_date,
                        "title": episode["title"].strip(),
                        "duration": datetime.timedelta(seconds=episode["total_time"]),
                        "url": enclosure_url,
                    }

                    if "description_html" in episode:
                        info["description"] = episode["description_html"].strip()
                    else:
                        info["description"] = episode["description"].strip()

                    episodes.append(info)
                    logger.debug(
                        "Episode info for GUID %s:\n%s",
                        guid,
                        pformat(info, sort_dicts=False, compact=True),
                    )

                    if not dry_run:
                        # Only add the enclosure URL if it's not already in
                        # the episodes table to prevent duplicate entries.
                        if enclosure_url not in seen_enclosure_urls:
                            feed_database.insert(
                                guid=guid,
                                enclosure_url=enclosure_url,
                                feed_name=feed_name,
                                timestamp=datetime.datetime.now(),
                            )
                        else:
                            feed_database.insert(
                                guid=guid,
                                feed_name=feed_name,
                                timestamp=datetime.datetime.now(),
                            )

    return episodes


def process_feeds(
    feeds: FeedSettings,
    feed_database: FeedDatabase,
    dry_run: bool = False,
):
    """Process podcast feeds and post new episodes."""
    for feed in feeds:
        logger.debug("Starting")
        if dry_run:
            logger.debug("Running in dry mode.")

        logger.debug("Podcast Name: %s", feed.podcast_name)

        if not feed.enabled:
            logger.debug("Feed disabled. Skipping.")
            continue

        # Pull episodes from the configured podcast feed
        podcast: PodcastFeed = PodcastFeed()

        logger.debug("Feed URL: %s", feed.feed_url)

        # Check to see if the podcast feed has been updated since the
        # last run. Only process the feed of the feed has been updated.
        _now: datetime.datetime = datetime.datetime.now(datetime.timezone.utc)
        previous_last_modified: datetime.datetime | None = feed_database.get_last_modified(
            feed_name=feed.name
        )
        current_last_modified: datetime.datetime | None = podcast.last_modified(
            feed_url=feed.feed_url
        )

        logger.debug(
            "Previous Last Modified: %s",
            previous_last_modified if previous_last_modified else "N/A",
        )
        logger.debug("Current Last Modified: %s", current_last_modified)

        if previous_last_modified and current_last_modified <= previous_last_modified:
            logger.debug("Feed has not been updated since last run.")
            continue

        episodes: list[dict[str, Any]] = podcast.fetch(
            feed_url=feed.feed_url,
            max_episodes=feed.max_episodes,
            user_agent=feed.user_agent,
        )

        bluesky_client: BlueskyClient | None = None
        if feed.bluesky_settings:
            # Setup Bluesky Client
            logger.debug("Bluesky API URL: %s", feed.bluesky_settings.api_url)
            bluesky_client = BlueskyClient(
                api_url=feed.bluesky_settings.api_url,
                username=feed.bluesky_settings.username,
                app_password=feed.bluesky_settings.app_password,
            )

        mastodon_client: MastodonClient | None = None
        if feed.mastodon_settings:
            # Connect to Mastodon Client
            logger.debug("Mastodon API URL: %s", feed.mastodon_settings.api_url)
            if feed.mastodon_settings.use_oauth:
                mastodon_client = MastodonClient(
                    api_url=feed.mastodon_settings.api_url,
                    client_secret=None,
                    access_token=feed.mastodon_settings.secrets_file,
                )
            else:
                mastodon_client = MastodonClient(
                    api_url=feed.mastodon_settings.api_url,
                    client_secret=feed.mastodon_settings.client_secret,
                    access_token=feed.mastodon_settings.access_token,
                )

        if episodes:
            new_episodes: list[dict[str, Any]] = retrieve_new_episodes(
                feed_episodes=episodes,
                feed_database=feed_database,
                feed_name=feed.name,
                guid_filter=feed.guid_filter,
                days=feed.recent_days,
                dry_run=dry_run,
            )
            new_episodes.reverse()

            logger.debug("New Episodes:\n%s", pformat(new_episodes))

            for episode in new_episodes:
                if bluesky_client:
                    post_text: str = format_bluesky_post(
                        podcast_name=feed.name,
                        episode=episode,
                        max_description_length=feed.bluesky_settings.max_description_length,
                        template_path=feed.bluesky_settings.template_path,
                        template_file=feed.bluesky_settings.template_file,
                    )

                    if not dry_run:
                        logger.info("Posting %s.", episode)
                        bluesky_client.post(body=post_text, episode_url=episode["url"])

                if mastodon_client:
                    post_text: str = format_mastodon_post(
                        podcast_name=feed.podcast_name,
                        episode=episode,
                        max_description_length=feed.max_description_length,
                        template_path=feed.template_directory,
                        template_file=feed.template_file,
                    )

                    if not dry_run:
                        logger.info("Posting %s.", episode)
                        mastodon_client.post(content=post_text)

        if not dry_run:
            feed_database.upsert_last_modified(feed_name=feed.name, last_modified=_now)


def main() -> None:
    """Fetch podcast episodes and post new episodes."""
    arguments: Namespace = modules.command.parse()

    if arguments.version:
        print(f"Version {APP_VERSION}")
        return

    dry_run: bool = arguments.dry_run

    app_config = AppConfig()
    app_settings: AppSettings = app_config.parse_app(settings_file=arguments.settings)

    log_handler: logging.FileHandler = configure_logging(
        app_settings.log_file, debug=arguments.debug
    )

    # Check to see if the feed database file exists. Create file if
    # the file does not exist
    feed_database: FeedDatabase = FeedDatabase(app_settings.database_file)

    process_feeds(
        feeds=app_settings.feeds,
        feed_database=feed_database,
        dry_run=dry_run,
    )

    if not dry_run and not arguments.skip_clean:
        feed_database.clean(days_to_keep=app_settings.database_clean_days)

    log_handler.close()
    logger.removeHandler(log_handler)


if __name__ == "__main__":
    main()
