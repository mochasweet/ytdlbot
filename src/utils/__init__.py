#!/usr/bin/env python3
# coding: utf-8

# ytdlbot - __init__.py.py


import logging
import pathlib
import re
import shutil
import tempfile
import time
import uuid
from http.cookiejar import MozillaCookieJar
from urllib.parse import quote_plus, urlparse

import ffmpeg


def sizeof_fmt(num: int, suffix="B"):
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, "Yi", suffix)


def timeof_fmt(seconds: int | float):
    periods = [("d", 86400), ("h", 3600), ("m", 60), ("s", 1)]
    result = ""
    for period_name, period_seconds in periods:
        if seconds >= period_seconds:
            period_value, seconds = divmod(seconds, period_seconds)
            result += f"{int(period_value)}{period_name}"
    return result


def is_youtube(url: str) -> bool:
    try:
        if not url or not isinstance(url, str):
            return False

        parsed = urlparse(url)
        return parsed.netloc.lower() in {'youtube.com', 'www.youtube.com', 'youtu.be'}

    except Exception:
        return False


def adjust_formats(formats):
    # high: best quality 1080P, 2K, 4K, 8K
    # medium: 720P
    # low: 480P

    mapping = {"high": [], "medium": [720], "low": [480]}
    # formats.insert(0, f"bestvideo[ext=mp4][height={m}]+bestaudio[ext=m4a]")
    # formats.insert(1, f"bestvideo[vcodec^=avc][height={m}]+bestaudio[acodec^=mp4a]/best[vcodec^=avc]/best")
    #
    # if settings[2] == "audio":
    #     formats.insert(0, "bestaudio[ext=m4a]")
    #
    # if settings[2] == "document":
    #     formats.insert(0, None)


def current_time(ts=None):
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ts))


def clean_tempfile():
    patterns = ["ytdl*", "spdl*", "leech*", "direct*"]
    temp_path = pathlib.Path(TMPFILE_PATH or tempfile.gettempdir())

    for pattern in patterns:
        for item in temp_path.glob(pattern):
            if time.time() - item.stat().st_ctime > 3600:
                shutil.rmtree(item, ignore_errors=True)


def shorten_url(url, CAPTION_URL_LENGTH_LIMIT):
    # Shortens a URL by cutting it to a specified length.
    shortened_url = url[: CAPTION_URL_LENGTH_LIMIT - 3] + "..."

    return shortened_url


def extract_filename(response):
    try:
        content_disposition = response.headers.get("content-disposition")
        if content_disposition:
            filename = re.findall("filename=(.+)", content_disposition)[0]
            return filename
    except (TypeError, IndexError):
        pass  # Handle potential exceptions during extraction

    # Fallback if Content-Disposition header is missing
    filename = response.url.rsplit("/")[-1]
    if not filename:
        filename = quote_plus(response.url)
    return filename


def extract_url_and_name(message_text):
    # Regular expression to match the URL
    url_pattern = r"(https?://[^\s]+)"
    # Regular expression to match the new name after '-n'
    name_pattern = r"-n\s+(.+)$"

    # Find the URL in the message_text
    url_match = re.search(url_pattern, message_text)
    url = url_match.group(0) if url_match else None

    # Find the new name in the message_text
    name_match = re.search(name_pattern, message_text)
    new_name = name_match.group(1) if name_match else None

    return url, new_name
