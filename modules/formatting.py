# Copyright (c) 2024 Linh Pham
# podcast-bot is released under the terms of the MIT License
# SPDX-License-Identifier: MIT
#
# vim: set noai syntax=python ts=4 sw=4:
"""Post Formatting Module."""
from typing import Any

from html2text import HTML2Text
from jinja2 import Environment, FileSystemLoader, Template, select_autoescape


def unsmart_quotes(text: str) -> str:
    """Replaces "smart" quotes with normal quotes."""
    text: str = text.replace("’", "'")
    text = text.replace("”", '"')
    text = text.replace("“", '"')
    return text


def format_bluesky_post(
    episode: dict[str, Any],
    podcast_name: str,
    max_description_length: int,
    template_path: str,
    template_file: str,
) -> str:
    """Returns a formatted post with episode information."""
    formatter: HTML2Text = HTML2Text()
    formatter.ignore_emphasis = True
    formatter.ignore_images = True
    formatter.ignore_links = True
    formatter.ignore_tables = True
    formatter.body_width = 0

    env: Environment = Environment(
        loader=FileSystemLoader(template_path),
        autoescape=select_autoescape(),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template: Template = env.get_template(template_file)

    # Replace "smart" quotes with regular quotes
    title: str = unsmart_quotes(text=episode["title"])
    description: str = unsmart_quotes(text=episode["description"])
    formatted_description: str = formatter.handle(description)

    # Fix issue with HTML2Text causing + to be rendered as \+
    formatted_description = formatted_description.replace(r"\+", "+")

    if len(formatted_description) > max_description_length:
        formatted_description = f"{formatted_description[:max_description_length].strip()}...\n"
    else:
        formatted_description = f"{formatted_description.strip()}\n"

    return template.render(
        podcast_name=podcast_name,
        title=title,
        description=formatted_description,
        url=episode["url"],
    )


def format_mastodon_post(
    episode: dict[str, Any],
    podcast_name: str,
    max_description_length: int,
    template_path: str,
    template_file: str,
) -> str:
    """Returns a formatted post with episode information."""
    formatter: HTML2Text = HTML2Text()
    formatter.ignore_emphasis = True
    formatter.ignore_images = True
    formatter.ignore_links = True
    formatter.ignore_tables = True
    formatter.body_width = 0

    env: Environment = Environment(
        loader=FileSystemLoader(template_path),
        autoescape=select_autoescape(),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template: Template = env.get_template(template_file)

    # Replace "smart" quotes with regular quotes
    title: str = unsmart_quotes(text=episode["title"])
    description: str = unsmart_quotes(text=episode["description"])
    formatted_description: str = formatter.handle(description)

    # Fix issue with HTML2Text causing + to be rendered as \+
    formatted_description = formatted_description.replace(r"\+", "+")

    if len(formatted_description) > max_description_length:
        formatted_description = f"{formatted_description[:max_description_length].strip()}...\n"
    else:
        formatted_description = f"{formatted_description.strip()}\n"

    return template.render(
        podcast_name=podcast_name,
        title=title,
        description=formatted_description,
        url=episode["url"],
    )
