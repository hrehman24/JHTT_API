# Beatify Music API

This module contains the core application code for the Beatify Music API, a RESTful API for managing artists, albums, tracks, users and playlists.

## Current Package Structure

- **api.py** - API registration, root endpoint, and startup function.
- **models.py** - Flask app and SQLAlchemy models/configuration.
- **utils.py** - Shared helpers for root payload and JSON responses.
- **resources/** - Split resource modules (`artists.py`, `albums.py`, `tracks.py`, `users.py`, `playlists.py`).

## Base URL

```
/Beatify/api/v1
```

## API Docs Endpoints

- Swagger UI: `/Beatify/api/v1/docs`
- OpenAPI YAML: `/Beatify/api/v1/openapi.yaml`

## Resources

### User

Represents a registered user who can own playlists.

**Fields:** `id`, `name`

| Endpoint | Method | Description |
|---|---|---|
| `/users` | GET | Get all users |
| `/users` | POST | Create a new user |
| `/users` | DELETE | Delete all users |
| `/users/<id>` | GET | Get a single user (includes their playlists) |
| `/users/<id>` | PUT | Update a user's name |
| `/users/<id>` | DELETE | Delete a user |
---

### Playlist

Represents a playlist that can contain tracks and be shared between users.

**Fields:** `id`, `name`, `description` (optional)

| Endpoint | Method | Description |
|---|---|---|
| `/playlists` | GET | Get all playlists |
| `/playlists` | POST | Create a new playlist (optionally link to a user via `user_id`) |
| `/playlists` | DELETE | Delete all playlists |
| `/playlists/<id>` | GET | Get a single playlist |
| `/playlists/<id>` | PUT | Update a playlist |
| `/playlists/<id>` | DELETE | Delete a playlist |

---

### Artist

Represents artists and their related albums.

| Endpoint | Method | Description |
|---|---|---|
| `/artists` | GET |Get ALL artists |
| `/artists` | POST |Create a singular artist |
| `/artists` | DELETE |Delete all artists |
| `/artists/<id>` | GET |Get singular artist |
| `/artists/<id>` | PUT |Update an artist |
| `/artists/<id>` | DELETE |Delete singular artist |

---

### Album

Represents albums and their relation to artists.

| Endpoint | Method | Description |
|---|---|---|
| `/albums` | GET |Get ALL albums |
| `/albums` | POST |Create singular album |
| `/albums/<id>` | GET |Get singular album |
| `/albums/<id>` | PUT |Update singular album |
| `/albums/<id>` | DELETE |Delete singular album |

---

### Track

Represents tracks and their relation to albums.

| Endpoint | Method | Description |
|---|---|---|
| `/tracks` | GET |Get ALL tracks |
| `/tracks` | POST |Create singular track |
| `/tracks` | DELETE |Delete all tracks |
| `/tracks/<id>` | GET |Get singular track |
| `/tracks/<id>` | PUT |Update singular track |
| `/tracks/<id>` | DELETE |Delete singular track |
