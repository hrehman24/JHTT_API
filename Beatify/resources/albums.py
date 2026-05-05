"""Album API resources."""

from flask import request
from flask_restful import Resource

from ..models import db, Artist, Album


class AlbumCollection(Resource):
	def get(self):
		response_data = []
		albums = Album.query.all()
		for album in albums:
			response_data.append({"name": album.name, "artist_id": album.artist_id, "id":album.id})
		return response_data

	def post(self):
		if not request.is_json:
			return {"message": "Request content type must be JSON"}, 415
		try:
			name = request.json["name"]
			artist_id = int(request.json["artist_id"])
		except KeyError:
			return {"message": "Incomplete request - missing fields"}, 400
		except ValueError:
			return {"message": "artist_id must be an integer"}, 400

		if not Artist.query.filter_by(id=artist_id).first():
			return {"message": "artist_id does not match any artist"}, 400
		if Album.query.filter_by(name=name, artist_id=artist_id).first():
			return {"message": f"Album {name} by artist_id {artist_id} already exists"}, 400

		new_album = Album(name=name, artist_id=artist_id)
		db.session.add(new_album)
		db.session.commit()
		return {"message": f"Album {name} created successfully"}, 201


class AlbumItem(Resource):
	def get(self, id):
		album = Album.query.get(id)
		if not album:
			return {"message": "Album not found"}, 404
		return {"name": album.name, "artist_id": album.artist_id, "id":album.id}

	def put(self, id):
		album = Album.query.get(id)
		if not album:
			return {"message": "Album not found"}, 404
		if not request.is_json:
			return {"message": "Request content type must be JSON"}, 415
		try:
			name = request.json["name"]
			artist_id = int(request.json["artist_id"])
		except KeyError:
			return {"message": "Incomplete request - missing fields"}, 400
		except ValueError:
			return {"message": "artist_id must be an integer"}, 400

		if not Artist.query.filter_by(id=artist_id).first():
			return {"message": "artist_id does not match any artist"}, 400
		if name == album.name and artist_id == album.artist_id:
			return {"message": "No changes detected"}, 400

		album.name = name
		album.artist_id = artist_id
		db.session.commit()
		return {"message": f"Album {name} updated successfully"}, 200

	def delete(self, id):
		album = Album.query.get(id)
		if not album:
			return {"message": "Album not found"}, 400
		db.session.delete(album)
		db.session.commit()
		return {"message": f"Album {album.name} deleted successfully"}, 200


__all__ = ["AlbumCollection", "AlbumItem"]
