#!/usr/bin/env python3
"""Compatibility entry point for offline maintenance of the static website.

The former WordPress downloader has been retired: running it would restore
third-party theme and plugin assets removed during the 2026-11-06 rebuild.
The maintained HTML pages and original assets are now the source of truth.
"""
from modernize import main


if __name__ == '__main__':
    main()
