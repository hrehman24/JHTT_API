"""
This module contains automated tests for the API to make sure its foundation is working correctly.
"""
# Note: a lot of help is taken from AI to complete these tests, but I have adapted and edited them to fit the actual implementation of the API. 
# I have also added some extra test cases that I thought were necessary to cover more edge cases and ensure the robustness of the API.

import pytest
import json
import os
import runpy
import sys
import tempfile
from unittest.mock import Mock
from sqlalchemy.exc import IntegrityError

project_root = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, project_root)
os.chdir(project_root)

from Beatify.models import app, db, Artist, Album, Track, User, Playlist
import Beatify.api as main_app
from Beatify.resources import artists as artists_resource
from Beatify.resources import playlists as playlists_resource
from Beatify.resources import users as users_resource
from Beatify.utils import build_root_payload, json_response

@pytest.fixture
def client():
    """
    Creates a test client with a fresh database for each test.
    """
    originalUri = app.config["SQLALCHEMY_DATABASE_URI"]
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"  # in memory database for testing

    with app.app_context():
        db.engine.dispose()
        db.session.close()
        db.create_all()

        testClient = app.test_client()
        yield testClient

        db.session.remove()
        db.drop_all()
        db.engine.dispose()
    app.config["SQLALCHEMY_DATABASE_URI"] = originalUri

BASE = "/Beatify/api/v1"

def PostJson(client, url, data):
    """Helper to send POST with JSON body"""
    return client.post(BASE + url, data=json.dumps(data), content_type="application/json")


def PutJson(client, url, data):
    """Helper to send PUT with JSON body"""
    return client.put(BASE + url, data=json.dumps(data), content_type="application/json")


def GetUrl(client, url):
    """Helper to send GET with the API prefix"""
    return client.get(BASE + url)


def DeleteUrl(client, url):
    """Helper to send DELETE with the API prefix"""
    return client.delete(BASE + url)


def PutPlain(client, url, data):
    """Helper to send PUT with non-JSON content"""
    return client.put(BASE + url, data=data, content_type="text/plain")


def PostPlain(client, url, data):
    """Helper to send POST with non-JSON content"""
    return client.post(BASE + url, data=data, content_type="text/plain")


class TestApiModule:

    def test_root_index_payload(self, client):
        """GET / returns API metadata payload"""
        resp = client.get("/")
        assert resp.status_code == 200
        assert resp.get_json()["api_name"] == "Beatify Music API"

    def test_start_api_calls_create_all_and_run(self, monkeypatch):
        """start_api initializes DB and starts server with debug flag"""
        create_all_mock = Mock()
        run_mock = Mock()
        print_mock = Mock()

        monkeypatch.setattr(main_app.db, "create_all", create_all_mock)
        monkeypatch.setattr(main_app.app, "run", run_mock)
        monkeypatch.setattr("builtins.print", print_mock)

        main_app.start_api(debug=False)

        create_all_mock.assert_called_once()
        run_mock.assert_called_once_with(debug=False)
        print_mock.assert_called_once_with("App is running!")

    def test_api_main_guard_executes_startup(self, monkeypatch):
        """Executing Beatify.api as __main__ triggers start_api(debug=True)."""
        create_all_mock = Mock()
        run_mock = Mock()
        print_mock = Mock()

        monkeypatch.setattr("flask_restful.Api.add_resource", lambda *args, **kwargs: None)
        monkeypatch.setattr("Beatify.models.app.route", lambda *args, **kwargs: (lambda func: func))
        monkeypatch.setattr("Beatify.models.db.create_all", create_all_mock)
        monkeypatch.setattr("Beatify.models.app.run", run_mock)
        monkeypatch.setattr("builtins.print", print_mock)

        runpy.run_module("Beatify.api", run_name="__main__")

        create_all_mock.assert_called_once()
        run_mock.assert_called_once_with(debug=True)
        print_mock.assert_called_once_with("App is running!")


class _BadMap:
    """Map-like object that passes membership checks but fails key access."""

    def __contains__(self, key):
        return True

    def __getitem__(self, key):
        raise TypeError("bad access")

    def get(self, key, default=None):
        raise TypeError("bad access")


class _DummyRequest:
    def __init__(self, payload):
        self.is_json = True
        self.json = payload


class TestCoverageBranches:

    def test_models_repr_lines(self):
        assert repr(Artist(name="A")) == "[Artist A]"
        assert repr(Album(name="B", artist_id=1)) == "[Album B]"
        assert repr(Track(name="C", length=120, album_id=1)) == "[Track C]"
        assert repr(User(name="D")) == "[User D]"
        assert repr(Playlist(name="E")) == "[Playlist E]"

    def test_artist_post_invalid_type_branch(self, monkeypatch):
        monkeypatch.setattr(artists_resource, "request", _DummyRequest(_BadMap()))
        body, code = artists_resource.ArtistCollection().post()
        assert code == 400
        assert body["message"] == "Invalid data types for fields"

    def test_artist_put_invalid_type_branch(self, monkeypatch, client):
        with app.app_context():
            db.session.add(Artist(name="ArtistX"))
            db.session.commit()

        monkeypatch.setattr(artists_resource, "request", _DummyRequest(_BadMap()))
        body, code = artists_resource.ArtistItem().put(1)
        assert code == 400
        assert body["message"] == "Invalid data types for fields"

    def test_user_post_invalid_type_branch(self, monkeypatch):
        monkeypatch.setattr(users_resource, "request", _DummyRequest(_BadMap()))
        body, code = users_resource.UserCollection().post()
        assert code == 400
        assert body["message"] == "Invalid data types for fields"

    def test_user_put_invalid_type_branch(self, monkeypatch, client):
        with app.app_context():
            db.session.add(User(name="UserX"))
            db.session.commit()

        monkeypatch.setattr(users_resource, "request", _DummyRequest(_BadMap()))
        body, code = users_resource.UserItem().put(1)
        assert code == 400
        assert body["message"] == "Invalid data types for fields"

    def test_playlist_post_invalid_type_branch(self, monkeypatch, client):
        monkeypatch.setattr(playlists_resource, "request", _DummyRequest(_BadMap()))
        body, code = playlists_resource.PlaylistCollection().post()
        assert code == 400
        assert body["message"] == "Invalid data types for fields"

    def test_playlist_post_integrity_error_branch(self, monkeypatch, client):
        original_commit = db.session.commit
        original_rollback = db.session.rollback
        rollback_mock = Mock()

        def _raise_commit():
            raise IntegrityError("stmt", "params", Exception("boom"))

        monkeypatch.setattr(playlists_resource, "request", _DummyRequest({"name": "List1"}))
        monkeypatch.setattr(db.session, "commit", _raise_commit)
        monkeypatch.setattr(db.session, "rollback", rollback_mock)

        body, code = playlists_resource.PlaylistCollection().post()
        assert code == 400
        assert body["message"] == "Database integrity error"
        rollback_mock.assert_called_once()

        monkeypatch.setattr(db.session, "commit", original_commit)
        monkeypatch.setattr(db.session, "rollback", original_rollback)

    def test_playlist_put_invalid_type_branch(self, monkeypatch, client):
        with app.app_context():
            db.session.add(Playlist(name="List2"))
            db.session.commit()

        monkeypatch.setattr(playlists_resource, "request", _DummyRequest(_BadMap()))
        body, code = playlists_resource.PlaylistItem().put(1)
        assert code == 400
        assert body["message"] == "Invalid data types for fields"

    def test_playlist_put_integrity_error_branch(self, monkeypatch, client):
        with app.app_context():
            db.session.add(Playlist(name="List3"))
            db.session.commit()

        original_commit = db.session.commit
        original_rollback = db.session.rollback
        rollback_mock = Mock()

        def _raise_commit():
            raise IntegrityError("stmt", "params", Exception("boom"))

        monkeypatch.setattr(playlists_resource, "request", _DummyRequest({"name": "Renamed"}))
        monkeypatch.setattr(db.session, "commit", _raise_commit)
        monkeypatch.setattr(db.session, "rollback", rollback_mock)

        body, code = playlists_resource.PlaylistItem().put(1)
        assert code == 400
        assert body["message"] == "Database integrity error"
        rollback_mock.assert_called_once()

        monkeypatch.setattr(db.session, "commit", original_commit)
        monkeypatch.setattr(db.session, "rollback", original_rollback)

    def test_utils_functions_covered(self):
        payload = build_root_payload("http://example.test/Beatify/api/v1")
        assert payload["endpoints"]["Artists"].endswith("/artists")

        with app.app_context():
            response = json_response({"ok": True})
        assert response.get_json() == {"ok": True}


# --------------------------------------------------------------------------
#                   ARTIST TESTS
# --------------------------------------------------------------------------

class TestArtistCollection:

    def test_GetEmptyArtists(self, client):
        """GET /artists when no artists exist returns empty list"""
        resp = GetUrl(client, "/artists")
        assert resp.status_code == 200
        assert resp.get_json() == []

    def test_PostArtist(self, client):
        """POST /artists with valid data creates an artist"""
        resp = PostJson(client, "/artists", {"name": "Eminem"})
        assert resp.status_code == 201
        assert "Eminem" in resp.get_json()["message"]

    def test_GetArtistsAfterPost(self, client):
        """GET /artists returns list with one artist after posting"""
        PostJson(client, "/artists", {"name": "John Wick"})
        resp = GetUrl(client, "/artists")
        data = resp.get_json()
        assert len(data) == 1
        assert data[0]["name"] == "John Wick"

    def test_PostArtistNotJson(self, client):
        """POST /artists with non-JSON content returns 415"""
        resp = PostPlain(client, "/artists", "not json")
        assert resp.status_code == 415

    def test_PostArtistMissingName(self, client):
        """POST /artists without name field returns 400"""
        resp = PostJson(client, "/artists", {})
        assert resp.status_code == 400

    def test_PostArtistDuplicate(self, client):
        """POST /artists with duplicate name returns 400"""
        PostJson(client, "/artists", {"name": "FooArtist"})
        resp = PostJson(client, "/artists", {"name": "FooArtist"})
        assert resp.status_code == 400

    def test_DeleteAllArtists(self, client):
        """DELETE /artists removes all artists"""
        PostJson(client, "/artists", {"name": "Artist1"})
        PostJson(client, "/artists", {"name": "Artist2"})
        resp = DeleteUrl(client, "/artists")
        assert resp.status_code == 200
        # check the deletion if succeeded
        getResp = GetUrl(client, "/artists")
        assert getResp.get_json() == []

class TestArtistItem:

    def test_GetSingleArtist(self, client):
        """GET /artists/1 returns the artist"""
        PostJson(client, "/artists", {"name": "Eminem"})
        resp = GetUrl(client, "/artists/1")
        assert resp.status_code == 200
        assert resp.get_json()["name"] == "Eminem"

    def test_GetArtistNotFound(self, client):
        """GET /artists/999 returns 404"""
        resp = GetUrl(client, "/artists/999")
        assert resp.status_code == 404

    def test_PutArtist(self, client):
        """PUT /artists/1 updates the artist name"""
        PostJson(client, "/artists", {"name": "Eminem"})
        resp = PutJson(client, "/artists/1", {"name": "Slim Shady"})
        assert resp.status_code == 200
        # confirm the update
        getResp = GetUrl(client, "/artists/1")
        assert getResp.get_json()["name"] == "Slim Shady"

    def test_PutArtistNotFound(self, client):
        """PUT /artists/999 returns 404"""
        resp = PutJson(client, "/artists/999", {"name": "Nobody"})
        assert resp.status_code == 404

    def test_PutArtistNotJson(self, client):
        """PUT /artists/1 with non-JSON content returns 415"""
        PostJson(client, "/artists", {"name": "Eminem"})
        resp = PutPlain(client, "/artists/1", "hello")
        assert resp.status_code == 415

    def test_PutArtistMissingFields(self, client):
        """PUT /artists/1 without name field returns 400"""
        PostJson(client, "/artists", {"name": "Eminem"})
        resp = PutJson(client, "/artists/1", {})
        assert resp.status_code == 400

    def test_PutArtistDuplicateName(self, client):
        """PUT /artists/1 with name that already exists returns 400"""
        PostJson(client, "/artists", {"name": "Eminem"})
        PostJson(client, "/artists", {"name": "Drake"})
        resp = PutJson(client, "/artists/1", {"name": "Drake"})
        assert resp.status_code == 400

    def test_DeleteArtist(self, client):
        """DELETE /artists/1 removes the artist"""
        PostJson(client, "/artists", {"name": "Eminem"})
        resp = DeleteUrl(client, "/artists/1")
        assert resp.status_code == 200
        # confirm deletion
        getResp = GetUrl(client, "/artists/1")
        assert getResp.status_code == 404

    def test_DeleteArtistNotFound(self, client):
        """DELETE /artists/999 returns 404"""
        resp = DeleteUrl(client, "/artists/999")
        assert resp.status_code == 404


# --------------------------------------------------------------------------
#                   ALBUM TESTS
# --------------------------------------------------------------------------

class TestAlbumCollection:

    def test_GetEmptyAlbums(self, client):
        """GET /albums when empty returns empty list"""
        resp = GetUrl(client, "/albums")
        assert resp.status_code == 200
        assert resp.get_json() == []

    def test_PostAlbum(self, client):
        """POST /albums creates an album"""
        PostJson(client, "/artists", {"name": "FooArtist"})
        resp = PostJson(client, "/albums", {"name": "Recovery", "artist_id": 1})
        assert resp.status_code == 201

    def test_GetAlbumsAfterPost(self, client):
        """GET /albums returns the created album"""
        PostJson(client, "/artists", {"name": "FooArtist"})
        PostJson(client, "/albums", {"name": "Recovery", "artist_id": 1})
        resp = GetUrl(client, "/albums")
        data = resp.get_json()
        assert len(data) == 1
        assert data[0]["name"] == "Recovery"

    def test_PostAlbumNotJson(self, client):
        """POST /albums with non-JSON returns 415"""
        resp = PostPlain(client, "/albums", "nope")
        assert resp.status_code == 415

    def test_PostAlbumMissingFields(self, client):
        """POST /albums missing fields returns 400"""
        resp = PostJson(client, "/albums", {"name": "Recovery"})
        assert resp.status_code == 400

    def test_PostAlbumBadArtistId(self, client):
        """POST /albums with non-existent artist_id returns 400"""
        resp = PostJson(client, "/albums", {"name": "Recovery", "artist_id": 999})
        assert resp.status_code == 400

    def test_PostAlbumInvalidArtistIdType(self, client):
        """POST /albums with non-integer artist_id returns 400"""
        resp = PostJson(client, "/albums", {"name": "Recovery", "artist_id": "abc"})
        assert resp.status_code == 400

    def test_PostAlbumDuplicate(self, client):
        """POST /albums with same name and artist returns 400"""
        PostJson(client, "/artists", {"name": "FooArtist"})
        PostJson(client, "/albums", {"name": "Recovery", "artist_id": 1})
        resp = PostJson(client, "/albums", {"name": "Recovery", "artist_id": 1})
        assert resp.status_code == 400


class TestAlbumItem:

    def test_GetSingleAlbum(self, client):
        """GET /albums/1 returns the album"""
        PostJson(client, "/artists", {"name": "Eminem"})
        PostJson(client, "/albums", {"name": "Recovery", "artist_id": 1})
        resp = GetUrl(client, "/albums/1")
        assert resp.status_code == 200
        assert resp.get_json()["name"] == "Recovery"

    def test_GetAlbumNotFound(self, client):
        """GET /albums/999 returns 404"""
        resp = GetUrl(client, "/albums/999")
        assert resp.status_code == 404

    def test_PutAlbum(self, client):
        """PUT /albums/1 updates the album"""
        PostJson(client, "/artists", {"name": "Eminem"})
        PostJson(client, "/albums", {"name": "Recovery", "artist_id": 1})
        resp = PutJson(client, "/albums/1", {"name": "Relapse", "artist_id": 1})
        assert resp.status_code == 200

    def test_PutAlbumNotFound(self, client):
        """PUT /albums/999 returns 404"""
        resp = PutJson(client, "/albums/999", {"name": "Nope", "artist_id": 1})
        assert resp.status_code == 404

    def test_PutAlbumNotJson(self, client):
        """PUT /albums/1 with non-JSON returns 415"""
        PostJson(client, "/artists", {"name": "Eminem"})
        PostJson(client, "/albums", {"name": "Recovery", "artist_id": 1})
        resp = PutPlain(client, "/albums/1", "hello")
        assert resp.status_code == 415

    def test_PutAlbumMissingFields(self, client):
        """PUT /albums/1 missing required fields returns 400"""
        PostJson(client, "/artists", {"name": "Eminem"})
        PostJson(client, "/albums", {"name": "Recovery", "artist_id": 1})
        resp = PutJson(client, "/albums/1", {"name": "Recovery"})
        assert resp.status_code == 400

    def test_PutAlbumBadArtistId(self, client):
        """PUT /albums/1 with non-existent artist returns 400"""
        PostJson(client, "/artists", {"name": "Eminem"})
        PostJson(client, "/albums", {"name": "Recovery", "artist_id": 1})
        resp = PutJson(client, "/albums/1", {"name": "Recovery", "artist_id": 999})
        assert resp.status_code == 400

    def test_PutAlbumInvalidArtistIdType(self, client):
        """PUT /albums/1 with non-integer artist_id returns 400"""
        PostJson(client, "/artists", {"name": "Eminem"})
        PostJson(client, "/albums", {"name": "Recovery", "artist_id": 1})
        resp = PutJson(client, "/albums/1", {"name": "Recovery", "artist_id": "abc"})
        assert resp.status_code == 400

    def test_PutAlbumNoChanges(self, client):
        """PUT /albums/1 with same data returns 400 (no changes)"""
        PostJson(client, "/artists", {"name": "Eminem"})
        PostJson(client, "/albums", {"name": "Recovery", "artist_id": 1})
        resp = PutJson(client, "/albums/1", {"name": "Recovery", "artist_id": 1})
        assert resp.status_code == 400

    def test_DeleteAlbum(self, client):
        """DELETE /albums/1 removes the album"""
        PostJson(client, "/artists", {"name": "Eminem"})
        PostJson(client, "/albums", {"name": "Recovery", "artist_id": 1})
        resp = DeleteUrl(client, "/albums/1")
        assert resp.status_code == 200

    def test_DeleteAlbumNotFound(self, client):
        """DELETE /albums/999 returns 400"""
        resp = DeleteUrl(client, "/albums/999")
        assert resp.status_code == 400


# --------------------------------------------------------------------------
#                   TRACK TESTS
# --------------------------------------------------------------------------

class TestTrackCollection:

    def test_GetEmptyTracks(self, client):
        """GET /tracks when empty returns empty list"""
        resp = GetUrl(client, "/tracks")
        assert resp.status_code == 200
        assert resp.get_json() == []

    def test_PostTrack(self, client):
        """POST /tracks creates a track"""
        PostJson(client, "/artists", {"name": "Eminem"})
        PostJson(client, "/albums", {"name": "Recovery", "artist_id": 1})
        resp = PostJson(client, "/tracks", {"name": "Not Afraid", "length": 263, "album_id": 1})
        assert resp.status_code == 201

    def test_GetTracksAfterPost(self, client):
        """GET /tracks returns the track we posted"""
        PostJson(client, "/artists", {"name": "Eminem"})
        PostJson(client, "/albums", {"name": "Recovery", "artist_id": 1})
        PostJson(client, "/tracks", {"name": "Not Afraid", "length": 263, "album_id": 1})
        resp = GetUrl(client, "/tracks")
        data = resp.get_json()
        assert len(data) == 1
        assert data[0]["name"] == "Not Afraid"
        assert data[0]["length"] == 263

    def test_PostTrackNotJson(self, client):
        """POST /tracks with non-JSON returns 415"""
        resp = PostPlain(client, "/tracks", "nope")
        assert resp.status_code == 415

    def test_PostTrackMissingFields(self, client):
        """POST /tracks missing fields returns 400"""
        resp = PostJson(client, "/tracks", {"name": "Song"})
        assert resp.status_code == 400

    def test_PostTrackInvalidTypes(self, client):
        """POST /tracks with bad data types returns 400"""
        resp = PostJson(client, "/tracks", {"name": "Song", "length": "abc", "album_id": 1})
        assert resp.status_code == 400

    def test_PostTrackAlbumNotFound(self, client):
        """POST /tracks with non-existent album returns 404"""
        resp = PostJson(client, "/tracks", {"name": "Song", "length": 200, "album_id": 999})
        assert resp.status_code == 404

    def test_PostTrackDuplicate(self, client):
        """POST /tracks with duplicate name returns 400"""
        PostJson(client, "/artists", {"name": "Eminem"})
        PostJson(client, "/albums", {"name": "Recovery", "artist_id": 1})
        PostJson(client, "/tracks", {"name": "Not Afraid", "length": 263, "album_id": 1})
        resp = PostJson(client, "/tracks", {"name": "Not Afraid", "length": 300, "album_id": 1})
        assert resp.status_code == 400

    def test_DeleteAllTracks(self, client):
        """DELETE /tracks removes all tracks"""
        PostJson(client, "/artists", {"name": "Eminem"})
        PostJson(client, "/albums", {"name": "Recovery", "artist_id": 1})
        PostJson(client, "/tracks", {"name": "Not Afraid", "length": 263, "album_id": 1})
        resp = DeleteUrl(client, "/tracks")
        assert resp.status_code == 200
        getResp = GetUrl(client, "/tracks")
        assert getResp.get_json() == []


class TestTrackItem:

    def test_GetSingleTrack(self, client):
        """GET /tracks/1 returns the track"""
        PostJson(client, "/artists", {"name": "Eminem"})
        PostJson(client, "/albums", {"name": "Recovery", "artist_id": 1})
        PostJson(client, "/tracks", {"name": "Not Afraid", "length": 263, "album_id": 1})
        resp = GetUrl(client, "/tracks/1")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["name"] == "Not Afraid"
        assert data["length"] == 263

    def test_GetTrackNotFound(self, client):
        """GET /tracks/999 returns 404"""
        resp = GetUrl(client, "/tracks/999")
        assert resp.status_code == 404

    def test_PutTrack(self, client):
        """PUT /tracks/1 updates the track"""
        PostJson(client, "/artists", {"name": "Eminem"})
        PostJson(client, "/albums", {"name": "Recovery", "artist_id": 1})
        PostJson(client, "/tracks", {"name": "Not Afraid", "length": 263, "album_id": 1})
        resp = PutJson(client, "/tracks/1", {"name": "Love The Way", "length": 300, "album_id": 1})
        assert resp.status_code == 200

    def test_PutTrackNotFound(self, client):
        """PUT /tracks/999 returns 404"""
        resp = PutJson(client, "/tracks/999", {"name": "X", "length": 100, "album_id": 1})
        assert resp.status_code == 404

    def test_PutTrackNotJson(self, client):
        """PUT /tracks/1 with non-JSON returns 415"""
        PostJson(client, "/artists", {"name": "Eminem"})
        PostJson(client, "/albums", {"name": "Recovery", "artist_id": 1})
        PostJson(client, "/tracks", {"name": "Not Afraid", "length": 263, "album_id": 1})
        resp = PutPlain(client, "/tracks/1", "hello")
        assert resp.status_code == 415

    def test_PutTrackMissingFields(self, client):
        """PUT /tracks/1 missing fields returns 400"""
        PostJson(client, "/artists", {"name": "Eminem"})
        PostJson(client, "/albums", {"name": "Recovery", "artist_id": 1})
        PostJson(client, "/tracks", {"name": "Not Afraid", "length": 263, "album_id": 1})
        resp = PutJson(client, "/tracks/1", {"name": "Song"})
        assert resp.status_code == 400

    def test_PutTrackInvalidTypes(self, client):
        """PUT /tracks/1 with bad types returns 400"""
        PostJson(client, "/artists", {"name": "Eminem"})
        PostJson(client, "/albums", {"name": "Recovery", "artist_id": 1})
        PostJson(client, "/tracks", {"name": "Not Afraid", "length": 263, "album_id": 1})
        resp = PutJson(client, "/tracks/1", {"name": "Song", "length": "abc", "album_id": 1})
        assert resp.status_code == 400

    def test_PutTrackDuplicateName(self, client):
        """PUT /tracks/1 with duplicate name returns 400"""
        PostJson(client, "/artists", {"name": "Eminem"})
        PostJson(client, "/albums", {"name": "Recovery", "artist_id": 1})
        PostJson(client, "/tracks", {"name": "Not Afraid", "length": 263, "album_id": 1})
        PostJson(client, "/tracks", {"name": "Love Way", "length": 300, "album_id": 1})
        resp = PutJson(client, "/tracks/1", {"name": "Love Way", "length": 263, "album_id": 1})
        assert resp.status_code == 400

    def test_DeleteTrack(self, client):
        """DELETE /tracks/1 removes the track"""
        PostJson(client, "/artists", {"name": "Eminem"})
        PostJson(client, "/albums", {"name": "Recovery", "artist_id": 1})
        PostJson(client, "/tracks", {"name": "Not Afraid", "length": 263, "album_id": 1})
        resp = DeleteUrl(client, "/tracks/1")
        assert resp.status_code == 200

    def test_DeleteTrackNotFound(self, client):
        """DELETE /tracks/999 returns 404"""
        resp = DeleteUrl(client, "/tracks/999")
        assert resp.status_code == 404


# --------------------------------------------------------------------------
#                   USER TESTS
# --------------------------------------------------------------------------

class TestUserCollection:

    def test_GetEmptyUsers(self, client):
        """GET /users when empty returns empty list"""
        resp = GetUrl(client, "/users")
        assert resp.status_code == 200
        assert resp.get_json() == []

    def test_PostUser(self, client):
        """POST /users creates a user"""
        resp = PostJson(client, "/users", {"name": "John"})
        assert resp.status_code == 201
        assert "John" in resp.get_json()["message"]

    def test_GetUsersAfterPost(self, client):
        """GET /users returns the user we posted"""
        PostJson(client, "/users", {"name": "John"})
        resp = GetUrl(client, "/users")
        data = resp.get_json()
        assert len(data) == 1
        assert data[0]["name"] == "John"

    def test_PostUserNotJson(self, client):
        """POST /users with non-JSON returns 415"""
        resp = PostPlain(client, "/users", "nope")
        assert resp.status_code == 415

    def test_PostUserMissingFields(self, client):
        """POST /users without name returns 400"""
        resp = PostJson(client, "/users", {})
        assert resp.status_code == 400

    def test_PostUserDuplicate(self, client):
        """POST /users with duplicate name returns 400"""
        PostJson(client, "/users", {"name": "John"})
        resp = PostJson(client, "/users", {"name": "John"})
        assert resp.status_code == 400

    def test_DeleteAllUsers(self, client):
        """DELETE /users removes all users"""
        PostJson(client, "/users", {"name": "John"})
        PostJson(client, "/users", {"name": "Jane"})
        resp = DeleteUrl(client, "/users")
        assert resp.status_code == 200
        getResp = GetUrl(client, "/users")
        assert getResp.get_json() == []


class TestUserItem:

    def test_GetSingleUser(self, client):
        """GET /users/1 returns the user with playlists"""
        PostJson(client, "/users", {"name": "John"})
        resp = GetUrl(client, "/users/1")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["name"] == "John"
        assert data["playlists"] == []

    def test_GetUserNotFound(self, client):
        """GET /users/999 returns 404"""
        resp = GetUrl(client, "/users/999")
        assert resp.status_code == 404

    def test_PutUser(self, client):
        """PUT /users/1 updates the user name"""
        PostJson(client, "/users", {"name": "John"})
        resp = PutJson(client, "/users/1", {"name": "Johnny"})
        assert resp.status_code == 200
        getResp = GetUrl(client, "/users/1")
        assert getResp.get_json()["name"] == "Johnny"

    def test_PutUserNotFound(self, client):
        """PUT /users/999 returns 404"""
        resp = PutJson(client, "/users/999", {"name": "Nobody"})
        assert resp.status_code == 404

    def test_PutUserNotJson(self, client):
        """PUT /users/1 with non-JSON returns 415"""
        PostJson(client, "/users", {"name": "John"})
        resp = PutPlain(client, "/users/1", "hello")
        assert resp.status_code == 415

    def test_PutUserMissingFields(self, client):
        """PUT /users/1 without name returns 400"""
        PostJson(client, "/users", {"name": "John"})
        resp = PutJson(client, "/users/1", {})
        assert resp.status_code == 400

    def test_PutUserDuplicate(self, client):
        """PUT /users/1 with existing name returns 400"""
        PostJson(client, "/users", {"name": "John"})
        PostJson(client, "/users", {"name": "Jane"})
        resp = PutJson(client, "/users/1", {"name": "Jane"})
        assert resp.status_code == 400

    def test_DeleteUser(self, client):
        """DELETE /users/1 removes the user"""
        PostJson(client, "/users", {"name": "John"})
        resp = DeleteUrl(client, "/users/1")
        assert resp.status_code == 200
        getResp = GetUrl(client, "/users/1")
        assert getResp.status_code == 404

    def test_DeleteUserNotFound(self, client):
        """DELETE /users/999 returns 404"""
        resp = DeleteUrl(client, "/users/999")
        assert resp.status_code == 404

    def test_GetUserWithPlaylists(self, client):
        """GET /users/1 shows playlists linked to user"""
        PostJson(client, "/users", {"name": "John"})
        PostJson(client, "/playlists", {"name": "Chill", "user_id": 1})
        resp = GetUrl(client, "/users/1")
        data = resp.get_json()
        assert len(data["playlists"]) == 1
        assert data["playlists"][0]["name"] == "Chill"


# --------------------------------------------------------------------------
#                   PLAYLIST TESTS
# --------------------------------------------------------------------------

class TestPlaylistCollection:

    def test_GetEmptyPlaylists(self, client):
        """GET /playlists when empty returns empty list"""
        resp = GetUrl(client, "/playlists")
        assert resp.status_code == 200
        assert resp.get_json() == []

    def test_PostPlaylist(self, client):
        """POST /playlists creates a playlist"""
        resp = PostJson(client, "/playlists", {"name": "Chill Vibes"})
        assert resp.status_code == 201

    def test_PostPlaylistWithDescription(self, client):
        """POST /playlists with description"""
        resp = PostJson(client, "/playlists", {"name": "Chill", "description": "Relaxing music"})
        assert resp.status_code == 201
        # check the data
        getResp = GetUrl(client, "/playlists")
        data = getResp.get_json()
        assert data[0]["description"] == "Relaxing music"

    def test_PostPlaylistWithUserId(self, client):
        """POST /playlists with user_id links playlist to user"""
        PostJson(client, "/users", {"name": "John"})
        resp = PostJson(client, "/playlists", {"name": "My Mix", "user_id": 1})
        assert resp.status_code == 201
        # verify user has this playlist
        getResp = GetUrl(client, "/users/1")
        assert len(getResp.get_json()["playlists"]) == 1

    def test_PostPlaylistWithBadUserId(self, client):
        """POST /playlists with non-existent user returns 404"""
        resp = PostJson(client, "/playlists", {"name": "My Mix", "user_id": 999})
        assert resp.status_code == 404

    def test_PostPlaylistWithInvalidUserIdType(self, client):
        """POST /playlists with non-integer user_id returns 400"""
        resp = PostJson(client, "/playlists", {"name": "My Mix", "user_id": "abc"})
        assert resp.status_code == 400

    def test_GetPlaylistsAfterPost(self, client):
        """GET /playlists returns the playlist we created"""
        PostJson(client, "/playlists", {"name": "Chill"})
        resp = GetUrl(client, "/playlists")
        data = resp.get_json()
        assert len(data) == 1
        assert data[0]["name"] == "Chill"

    def test_PostPlaylistNotJson(self, client):
        """POST /playlists with non-JSON returns 415"""
        resp = PostPlain(client, "/playlists", "nope")
        assert resp.status_code == 415

    def test_PostPlaylistMissingFields(self, client):
        """POST /playlists without name returns 400"""
        resp = PostJson(client, "/playlists", {})
        assert resp.status_code == 400

    def test_DeleteAllPlaylists(self, client):
        """DELETE /playlists removes all playlists"""
        PostJson(client, "/playlists", {"name": "Mix1"})
        PostJson(client, "/playlists", {"name": "Mix2"})
        resp = DeleteUrl(client, "/playlists")
        assert resp.status_code == 200
        getResp = GetUrl(client, "/playlists")
        assert getResp.get_json() == []


class TestPlaylistItem:

    def test_GetSinglePlaylist(self, client):
        """GET /playlists/1 returns the playlist with tracks and users"""
        PostJson(client, "/playlists", {"name": "Chill"})
        resp = GetUrl(client, "/playlists/1")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["name"] == "Chill"
        assert data["tracks"] == []
        assert data["users"] == []

    def test_GetPlaylistNotFound(self, client):
        """GET /playlists/999 returns 404"""
        resp = GetUrl(client, "/playlists/999")
        assert resp.status_code == 404

    def test_PutPlaylist(self, client):
        """PUT /playlists/1 updates the playlist"""
        PostJson(client, "/playlists", {"name": "Chill"})
        resp = PutJson(client, "/playlists/1", {"name": "Super Chill"})
        assert resp.status_code == 200

    def test_PutPlaylistWithDescription(self, client):
        """PUT /playlists/1 updates name and description"""
        PostJson(client, "/playlists", {"name": "Chill"})
        resp = PutJson(client, "/playlists/1", {"name": "Chill", "description": "Updated desc"})
        assert resp.status_code == 200
        getResp = GetUrl(client, "/playlists/1")
        assert getResp.get_json()["description"] == "Updated desc"

    def test_PutPlaylistNotFound(self, client):
        """PUT /playlists/999 returns 404"""
        resp = PutJson(client, "/playlists/999", {"name": "Nope"})
        assert resp.status_code == 404

    def test_PutPlaylistNotJson(self, client):
        """PUT /playlists/1 with non-JSON returns 415"""
        PostJson(client, "/playlists", {"name": "Chill"})
        resp = PutPlain(client, "/playlists/1", "hello")
        assert resp.status_code == 415

    def test_PutPlaylistMissingFields(self, client):
        """PUT /playlists/1 without name returns 400"""
        PostJson(client, "/playlists", {"name": "Chill"})
        resp = PutJson(client, "/playlists/1", {})
        assert resp.status_code == 400

    def test_PutPlaylistAddTrack(self, client):
        """PUT /playlists/1 with track_id adds track to playlist"""
        PostJson(client, "/artists", {"name": "Eminem"})
        PostJson(client, "/albums", {"name": "Recovery", "artist_id": 1})
        PostJson(client, "/tracks", {"name": "Not Afraid", "length": 263, "album_id": 1})
        PostJson(client, "/playlists", {"name": "Chill"})
        resp = PutJson(client, "/playlists/1", {"name": "Chill", "track_id": 1})
        assert resp.status_code == 200
        # verify track is on the playlist
        getResp = GetUrl(client, "/playlists/1")
        data = getResp.get_json()
        assert len(data["tracks"]) == 1
        assert data["tracks"][0]["name"] == "Not Afraid"

    def test_PutPlaylistAddTrackAlreadyExists(self, client):
        """PUT /playlists/1 with track already in playlist doesnt duplicate"""
        PostJson(client, "/artists", {"name": "Eminem"})
        PostJson(client, "/albums", {"name": "Recovery", "artist_id": 1})
        PostJson(client, "/tracks", {"name": "Not Afraid", "length": 263, "album_id": 1})
        PostJson(client, "/playlists", {"name": "Chill"})
        PutJson(client, "/playlists/1", {"name": "Chill", "track_id": 1})
        # add same track again
        resp = PutJson(client, "/playlists/1", {"name": "Chill", "track_id": 1})
        assert resp.status_code == 200
        getResp = GetUrl(client, "/playlists/1")
        assert len(getResp.get_json()["tracks"]) == 1  # still just 1

    def test_PutPlaylistTrackNotFound(self, client):
        """PUT /playlists/1 with non-existent track returns 404"""
        PostJson(client, "/playlists", {"name": "Chill"})
        resp = PutJson(client, "/playlists/1", {"name": "Chill", "track_id": 999})
        assert resp.status_code == 404

    def test_PutPlaylistInvalidTrackIdType(self, client):
        """PUT /playlists/1 with non-integer track_id returns 400"""
        PostJson(client, "/playlists", {"name": "Chill"})
        resp = PutJson(client, "/playlists/1", {"name": "Chill", "track_id": "abc"})
        assert resp.status_code == 400

    def test_PutPlaylistAddUser(self, client):
        """PUT /playlists/1 with user_id links user to playlist"""
        PostJson(client, "/users", {"name": "John"})
        PostJson(client, "/playlists", {"name": "Chill"})
        resp = PutJson(client, "/playlists/1", {"name": "Chill", "user_id": 1})
        assert resp.status_code == 200
        getResp = GetUrl(client, "/playlists/1")
        data = getResp.get_json()
        assert len(data["users"]) == 1
        assert data["users"][0]["name"] == "John"

    def test_PutPlaylistAddUserAlreadyLinked(self, client):
        """PUT /playlists/1 with user already linked doesnt duplicate"""
        PostJson(client, "/users", {"name": "John"})
        PostJson(client, "/playlists", {"name": "Chill"})
        PutJson(client, "/playlists/1", {"name": "Chill", "user_id": 1})
        resp = PutJson(client, "/playlists/1", {"name": "Chill", "user_id": 1})
        assert resp.status_code == 200
        getResp = GetUrl(client, "/playlists/1")
        assert len(getResp.get_json()["users"]) == 1

    def test_PutPlaylistUserNotFound(self, client):
        """PUT /playlists/1 with non-existent user returns 404"""
        PostJson(client, "/playlists", {"name": "Chill"})
        resp = PutJson(client, "/playlists/1", {"name": "Chill", "user_id": 999})
        assert resp.status_code == 404

    def test_PutPlaylistInvalidUserIdType(self, client):
        """PUT /playlists/1 with non-integer user_id returns 400"""
        PostJson(client, "/playlists", {"name": "Chill"})
        resp = PutJson(client, "/playlists/1", {"name": "Chill", "user_id": "abc"})
        assert resp.status_code == 400

    def test_DeletePlaylist(self, client):
        """DELETE /playlists/1 removes the playlist"""
        PostJson(client, "/playlists", {"name": "Chill"})
        resp = DeleteUrl(client, "/playlists/1")
        assert resp.status_code == 200

    def test_DeletePlaylistNotFound(self, client):
        """DELETE /playlists/999 returns 404"""
        resp = DeleteUrl(client, "/playlists/999")
        assert resp.status_code == 404

    def test_GetPlaylistWithTracksAndUsers(self, client):
        """GET /playlists/1 shows full data with tracks and users"""
        PostJson(client, "/artists", {"name": "Eminem"})
        PostJson(client, "/albums", {"name": "Recovery", "artist_id": 1})
        PostJson(client, "/tracks", {"name": "Not Afraid", "length": 263, "album_id": 1})
        PostJson(client, "/users", {"name": "John"})
        PostJson(client, "/playlists", {"name": "Best Hits", "user_id": 1})
        PutJson(client, "/playlists/1", {"name": "Best Hits", "track_id": 1})
        resp = GetUrl(client, "/playlists/1")
        data = resp.get_json()
        assert data["name"] == "Best Hits"
        assert len(data["tracks"]) == 1
        assert len(data["users"]) == 1
        assert data["tracks"][0]["name"] == "Not Afraid"
        assert data["users"][0]["name"] == "John"
