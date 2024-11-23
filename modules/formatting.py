# Copyright (c) 2024 Linh Pham
# podcast-bot is released under the terms of the MIT License
# SPDX-License-Identifier: MIT
#
# vim: set noai syntax=python ts=4 sw=4:
"""Post Formatting Module."""
from datetime import timedelta
from string import Formatter
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
        formatted_description = (
            f"{formatted_description[:max_description_length].strip()}...\n"
        )
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
        formatted_description = (
            f"{formatted_description[:max_description_length].strip()}...\n"
        )
    else:
        formatted_description = f"{formatted_description.strip()}\n"

    return template.render(
        podcast_name=podcast_name,
        title=title,
        description=formatted_description,
        url=episode["url"],
    )


def timedelta_to_str(
    time_delta: timedelta,
    format_string: str = "{D:02}d {H:02}h {M:02}m {S:02}s",
    input_type: str = "timedelta",
) -> str:
    """Return a formatted string for datetime.timedelta object.

    Convert a datetime.timedelta object or a regular number to a custom-
    formatted string, just like the stftime() method does for datetime.datetime
    objects.

    The fmt argument allows custom formatting to be specified.  Fields can
    include seconds, minutes, hours, days, and weeks.  Each field is optional.

    Some examples:
        '{D:02}d {H:02}h {M:02}m {S:02}s' --> '05d 08h 04m 02s' (default)
        '{W}w {D}d {H}:{M:02}:{S:02}'     --> '4w 5d 8:04:02'
        '{D:2}d {H:2}:{M:02}:{S:02}'      --> ' 5d  8:04:02'
        '{H}h {S}s'                       --> '72h 800s'

    The inputtype argument allows tdelta to be a regular number instead of the
    default, which is a datetime.timedelta object.  Valid inputtype strings:
        's', 'seconds',
        'm', 'minutes',
        'h', 'hours',
        'd', 'days',
        'w', 'weeks'

    Credit: MarredCheese (CC-BY-SA 3.0)
    Source: https://stackoverflow.com/a/42320260
    """
    # Convert tdelta to integer seconds.
    if input_type == "timedelta":
        remainder = int(time_delta.total_seconds())
    elif input_type in ["s", "seconds"]:
        remainder = int(time_delta)
    elif input_type in ["m", "minutes"]:
        remainder = int(time_delta) * 60
    elif input_type in ["h", "hours"]:
        remainder = int(time_delta) * 3600
    elif input_type in ["d", "days"]:
        remainder = int(time_delta) * 86400
    elif input_type in ["w", "weeks"]:
        remainder = int(time_delta) * 604800

    f = Formatter()
    desired_fields: list[str | None] = [
        field_tuple[1] for field_tuple in f.parse(format_string)
    ]
    possible_fields = ("W", "D", "H", "M", "S")
    constants: dict[str, int] = {"W": 604800, "D": 86400, "H": 3600, "M": 60, "S": 1}
    values: dict = {}
    for field in possible_fields:
        if field in desired_fields and field in constants:
            values[field], remainder = divmod(remainder, constants[field])

    return f.format(format_string, **values)
