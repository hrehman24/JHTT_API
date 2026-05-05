"""Reusable utility helpers for API modules and tests."""

from flask import current_app


def build_root_payload(base_url: str = "http://localhost:5000/Beatify/api/v1") -> dict:
    """Create a reusable payload for the API root endpoint."""
    return {
        "api_name": "Beatify Music API",
        "version": "v1",
        "description": "A RESTful API for managing artists, albums, tracks, users and playlists.",
        "how_to_use": {
            "methods": "Use GET to read, POST to create, PUT to update, DELETE to remove.",
            "content_type": "All POST and PUT requests must use Content-Type: application/json",
            "example": "To create an artist: POST /Beatify/api/v1/artists with body {\"name\": \"Eminem\"}",
        },
        "endpoints": {
            "Artists": f"{base_url}/artists",
            "Albums": f"{base_url}/albums",
            "Tracks": f"{base_url}/tracks",
            "Users": f"{base_url}/users",
            "Playlists": f"{base_url}/playlists",
            "Docs": f"{base_url}/docs",
        },
        "single_item": "Add /<id> to any endpoint above, e.g. /Beatify/api/v1/artists/1",
    }


def json_response(payload: dict):
    """Return Flask JSON response with a dict payload."""
    pretty_json = current_app.json.dumps(payload, indent=2) + "\n"
    return current_app.response_class(pretty_json, mimetype="application/json")
