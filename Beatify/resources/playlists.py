"""Playlist API resources."""

from flask import request
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from ..models import db, Playlist, Track, User


class PlaylistCollection(Resource):
	def get(self):
		playlist_list = []
		all_playlists = Playlist.query.all()
		for playlist in all_playlists:
			playlist_list.append(
				{"id": playlist.id, "name": playlist.name, "description": playlist.description}
			)
		return playlist_list

	def post(self):
		if not request.is_json:
			return {"message": "Request content type must be JSON"}, 415
		incoming_data = request.json
		required_fields = ["name"]
		if not all(field in incoming_data for field in required_fields):
			return {"message": "Incomplete request - missing fields"}, 400
		try:
			playlist_name = incoming_data["name"]
			playlist_desc = incoming_data.get("description", "")
		except (ValueError, TypeError):
			return {"message": "Invalid data types for fields"}, 400

		new_playlist = Playlist(name=playlist_name, description=playlist_desc)
		if "user_id" in incoming_data:
			try:
				user_id = int(incoming_data["user_id"])
			except (ValueError, TypeError):
				return {"message": "user_id must be an integer"}, 400
			found_user = User.query.get(user_id)
			if not found_user:
				return {"message": "User not found"}, 404
			new_playlist.users.append(found_user)

		db.session.add(new_playlist)
		try:
			db.session.commit()
		except IntegrityError:
			db.session.rollback()
			return {"message": "Database integrity error"}, 400
		return {"message": f"Playlist {playlist_name} created successfully!"}, 201

	def delete(self):
		num_deleted = Playlist.query.delete()
		db.session.commit()
		return {"message": f"Deleted {num_deleted} playlists"}, 200


class PlaylistItem(Resource):
	def get(self, id):
		playlist = Playlist.query.get(id)
		if not playlist:
			return {"message": "Playlist not found"}, 404
		track_list = []
		for track in playlist.tracks:
			track_list.append({"id": track.id, "name": track.name, "length": track.length})
		user_list = []
		for user in playlist.users:
			user_list.append({"id": user.id, "name": user.name})
		return {
			"id": playlist.id,
			"name": playlist.name,
			"description": playlist.description,
			"tracks": track_list,
			"users": user_list,
		}

	def put(self, id):
		playlist = Playlist.query.get(id)
		if not playlist:
			return {"message": "Playlist not found"}, 404
		if not request.is_json:
			return {"message": "Request content type must be JSON"}, 415
		incoming_data = request.json
		required_fields = ["name"]
		if not all(field in incoming_data for field in required_fields):
			return {"message": "Incomplete request - missing fields"}, 400
		try:
			playlist.name = incoming_data["name"]
			playlist.description = incoming_data.get("description", playlist.description)
		except (ValueError, TypeError):
			return {"message": "Invalid data types for fields"}, 400

		if "track_id" in incoming_data:
			try:
				track_id = int(incoming_data["track_id"])
			except (ValueError, TypeError):
				return {"message": "track_id must be an integer"}, 400
			found_track = Track.query.get(track_id)
			if not found_track:
				return {"message": "Track not found"}, 404
			if found_track not in playlist.tracks:
				playlist.tracks.append(found_track)

		if "user_id" in incoming_data:
			try:
				user_id = int(incoming_data["user_id"])
			except (ValueError, TypeError):
				return {"message": "user_id must be an integer"}, 400
			found_user = User.query.get(user_id)
			if not found_user:
				return {"message": "User not found"}, 404
			if found_user not in playlist.users:
				playlist.users.append(found_user)

		try:
			db.session.commit()
		except IntegrityError:
			db.session.rollback()
			return {"message": "Database integrity error"}, 400
		return {"message": f"Playlist {playlist.name} updated successfully!"}, 200

	def delete(self, id):
		playlist = Playlist.query.get(id)
		if not playlist:
			return {"message": "Playlist not found"}, 404
		db.session.delete(playlist)
		db.session.commit()
		return {"message": f"Playlist {playlist.name} deleted successfully"}, 200


__all__ = ["PlaylistCollection", "PlaylistItem"]
