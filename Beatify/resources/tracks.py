"""Track API resources."""

from flask import request
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from ..models import db, Album, Track


class TrackCollection(Resource):
	def get(self):
		track_list = []
		tracks = Track.query.all()
		for track in tracks:
			track_list.append({"name": track.name, "length": track.length, "album_id": track.album_id, "id": track.id})
		return track_list

	def post(self):
		if not request.is_json:
			return {"message": "Request content type must be JSON"}, 415
		incoming_json = request.json
		fields = ["name", "length", "album_id"]
		if not all(field in incoming_json for field in fields):
			return {"message": "Incomplete request - missing fields"}, 400
		try:
			name = incoming_json["name"]
			length = int(incoming_json["length"])
			album_id = int(incoming_json["album_id"])
		except (ValueError, TypeError):
			return {"message": "Invalid data types for fields"}, 400
		album = Album.query.get(album_id)
		if not album:
			return {"message": "Album not found"}, 404

		new_track = Track(name=name, length=length, album_id=album_id)
		db.session.add(new_track)
		try:
			db.session.commit()
		except IntegrityError:
			db.session.rollback()
			return {"message": "Database integrity error - possible duplicate entry"}, 400
		return {"message": f"Track {name} created successfully!"}, 201

	def delete(self):
		num_deleted = Track.query.delete()
		db.session.commit()
		return {"message": f"Deleted {num_deleted} tracks"}, 200


class TrackItem(Resource):
	def get(self, id):
		track = Track.query.get(id)
		if not track:
			return {"message": "Track not found"}, 404
		return {"name": track.name, "length": track.length, "album_id": track.album_id, "id": track.id}

	def put(self, id):
		track = Track.query.get(id)
		if not track:
			return {"message": "Track not found"}, 404
		if not request.is_json:
			return {"message": "Request content type must be JSON"}, 415
		incoming_json = request.json
		fields = ["name", "length", "album_id"]
		if not all(field in incoming_json for field in fields):
			return {"message": "Incomplete request - missing fields"}, 400
		try:
			track.name = incoming_json["name"]
			track.length = int(incoming_json["length"])
			track.album_id = int(incoming_json["album_id"])
		except (ValueError, TypeError):
			return {"message": "Invalid data types for fields"}, 400
		try:
			db.session.commit()
		except IntegrityError:
			db.session.rollback()
			return {"message": "Database integrity error - possible duplicate entry"}, 400
		return {"message": f"Track {track.name} updated successfully!"}, 200

	def delete(self, id):
		track = Track.query.get(id)
		if not track:
			return {"message": "Track not found"}, 404
		db.session.delete(track)
		db.session.commit()
		return {"message": f"Track {track.name} deleted successfully"}, 200


__all__ = ["TrackCollection", "TrackItem"]
