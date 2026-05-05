from __future__ import annotations

from collections import Counter
from typing import Any

import requests
from flask import Flask, jsonify

BASE_URL = "http://130.162.240.153:5000/Beatify/api/v1"
TIMEOUT = 10

app = Flask(__name__)


def _get(path: str) -> tuple[int, Any]:
    try:
        response = requests.get(f"{BASE_URL}{path}", timeout=TIMEOUT)
    except requests.RequestException as exc:
        return 503, {"message": f"Beatify API unavailable: {exc}"}

    try:
        data = response.json()
    except ValueError:
        data = response.text

    return response.status_code, data


def _fetch_list(path: str) -> tuple[bool, list[dict[str, Any]]]:
    status, data = _get(path)
    if not (200 <= status < 300 and isinstance(data, list)):
        return False, []
    return True, data


@app.get("/")
def root() -> Any:
    return jsonify(
        {
            "service": "Beatify Auxiliary Service",
            "version": "1.0",
            "endpoints": {
                "summary": "/analytics/summary",
                "top_artists": "/analytics/top-artists",
                "recommendations": "/recommendations/user/<user_id>",
            },
        }
    )


@app.get("/analytics/summary")
def summary() -> Any:
    ok_artists, artists = _fetch_list("/artists")
    ok_albums, albums = _fetch_list("/albums")
    ok_tracks, tracks = _fetch_list("/tracks")
    ok_users, users = _fetch_list("/users")
    ok_playlists, playlists = _fetch_list("/playlists")

    if not all([ok_artists, ok_albums, ok_tracks, ok_users, ok_playlists]):
        return jsonify({"message": "Unable to fetch data from Beatify API"}), 503

    avg_track_length = 0.0
    if tracks:
        lengths = [t.get("length", 0) for t in tracks if isinstance(t.get("length", 0), int)]
        avg_track_length = round(sum(lengths) / len(lengths), 2) if lengths else 0.0

    payload = {
        "counts": {
            "artists": len(artists),
            "albums": len(albums),
            "tracks": len(tracks),
            "users": len(users),
            "playlists": len(playlists),
        },
        "metrics": {
            "average_track_length_seconds": avg_track_length,
            "tracks_per_album_ratio": round(len(tracks) / len(albums), 2) if albums else 0,
        },
    }
    return jsonify(payload)


@app.get("/analytics/top-artists")
def top_artists() -> Any:
    ok_albums, albums = _fetch_list("/albums")
    ok_tracks, tracks = _fetch_list("/tracks")
    ok_artists, artists = _fetch_list("/artists")

    if not all([ok_albums, ok_tracks, ok_artists]):
        return jsonify({"message": "Unable to build top artists analytics"}), 503

    album_to_artist = {}
    for album in albums:
        if "id" in album and "artist_id" in album:
            album_to_artist[album["id"]] = album["artist_id"]

    artist_counter: Counter[int] = Counter()
    for track in tracks:
        album_id = track.get("album_id")
        artist_id = album_to_artist.get(album_id)
        if artist_id is not None:
            artist_counter[artist_id] += 1

    artist_name = {
        artist.get("id"): str(artist.get("name", "Unknown"))
        for artist in artists
        if isinstance(artist.get("id"), int)
    }

    top_items = [
        {
            "artist_id": artist_id,
            "artist_name": artist_name.get(artist_id, f"Artist #{artist_id}"),
            "track_count": count,
        }
        for artist_id, count in artist_counter.most_common(5)
    ]

    return jsonify({"items": top_items, "count": len(top_items)})


@app.get("/recommendations/user/<int:user_id>")
def recommendations(user_id: int) -> Any:
    status, user_data = _get(f"/users/{user_id}")
    if status == 404:
        return jsonify({"message": "User not found in Beatify API"}), 404
    if not (200 <= status < 300 and isinstance(user_data, dict)):
        return jsonify({"message": "Unable to fetch user from Beatify API"}), 503

    ok_tracks, tracks = _fetch_list("/tracks")
    if not ok_tracks:
        return jsonify({"message": "Unable to fetch tracks from Beatify API"}), 503

    playlist_track_ids: set[int] = set()
    for playlist in user_data.get("playlists", []):
        playlist_id = playlist.get("id")
        if playlist_id is None:
            continue
        p_status, playlist_detail = _get(f"/playlists/{playlist_id}")
        if 200 <= p_status < 300 and isinstance(playlist_detail, dict):
            for track in playlist_detail.get("tracks", []):
                track_id = track.get("id")
                if isinstance(track_id, int):
                    playlist_track_ids.add(track_id)

    candidates = [
        t
        for t in tracks
        if isinstance(t.get("id"), int)
        if isinstance(t.get("length"), int)
        and t["length"] >= 180
        and t["id"] not in playlist_track_ids
    ]

    candidates = sorted(candidates, key=lambda item: item["length"], reverse=True)[:5]
    items = [
        {
            "track_id": t.get("id"),
            "name": t.get("name"),
            "length": t.get("length"),
            "reason": "Popular length and not present in your playlists",
        }
        for t in candidates
    ]

    return jsonify(
        {
            "user_id": user_id,
            "algorithm": "Exclude owned tracks, then prefer longer tracks (>=180s)",
            "items": items,
        }
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7000, debug=True)
