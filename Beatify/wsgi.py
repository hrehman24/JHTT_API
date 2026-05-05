"""WSGI entrypoint for production application servers."""

from .api import app

__all__ = ["app"]
