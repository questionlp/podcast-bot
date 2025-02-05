# Copyright (c) 2022-2025 Linh Pham
# podcast-bot is released under the terms of the MIT License
# SPDX-License-Identifier: MIT
#
# vim: set noai syntax=python ts=4 sw=4:
"""Application Command-Line Parsing Module."""

from argparse import ArgumentParser, Namespace


def parse() -> Namespace:
    """Parse command-line arguments, options and flags using ArgumentParser."""
    parser: ArgumentParser = ArgumentParser(
        description=(
            "Fetch items from a podcast feed and publish new items "
            "to Mastodon and/or Bluesky."
        )
    )
    parser.add_argument(
        "-s",
        "--settings",
        type=str,
        default="settings.json",
        help="Application settings file (default: settings.json)",
    )
    parser.add_argument(
        "--debug", action="store_true", help="Enable debug output to stdout"
    )
    parser.add_argument(
        "--skip-clean",
        action="store_true",
        help="Skip database clean-up after processing and posting episodes",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Parse podcast feed but do not post anything",
    )
    parser.add_argument(
        "--version",
        action="store_true",
        help="Prints out the version of the application and exits.",
    )

    return parser.parse_args()
