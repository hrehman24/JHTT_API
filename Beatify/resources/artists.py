"""Artist API resources."""

from flask import request
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from ..models import db, Artist


class ArtistCollection(Resource):
	def get(self):
		artist_list = []
		artists = Artist.query.all()
		for artist in artists:
			artist_list.append({"name": artist.name, "id": artist.id})
		return artist_list

	def post(self):
		if not request.is_json:
			return {"message": "Request content type must be JSON"}, 415
		incoming_json = request.json
		fields = ["name"]
		if not all(field in incoming_json for field in fields):
			return {"message": "Incomplete request - missing fields"}, 400
		try:
			name = incoming_json["name"]
		except (ValueError, TypeError):
			return {"message": "Invalid data types for fields"}, 400
		new_artist = Artist(name=name)
		db.session.add(new_artist)
		try:
			db.session.commit()
		except IntegrityError:
			db.session.rollback()
			return {"message": "Database integrity error - possible duplicate entry"}, 400
		return {"message": f"Artist {name} created successfully!"}, 201

	def delete(self):
		num_deleted = Artist.query.delete()
		db.session.commit()
		return {"message": f"Deleted {num_deleted} artists"}, 200


class ArtistItem(Resource):
	def get(self, id):
		artist = Artist.query.get(id)
		if not artist:
			return {"message": "Artist not found"}, 404
		return {"name": artist.name, "id": artist.id}

	def put(self, id):
		artist = Artist.query.get(id)
		if not artist:
			return {"message": "Artist not found"}, 404
		if not request.is_json:
			return {"message": "Request content type must be JSON"}, 415
		incoming_json = request.json
		fields = ["name"]
		if not all(field in incoming_json for field in fields):
			return {"message": "Incomplete request - missing fields"}, 400
		try:
			artist.name = incoming_json["name"]
		except (ValueError, TypeError):
			return {"message": "Invalid data types for fields"}, 400
		try:
			db.session.commit()
		except IntegrityError:
			db.session.rollback()
			return {"message": "Database integrity error - possible duplicate entry"}, 400
		return {"message": f"Artist {artist.name} updated successfully!"}, 200

	def delete(self, id):
		artist = Artist.query.get(id)
		if not artist:
			return {"message": "Artist not found"}, 404
		db.session.delete(artist)
		db.session.commit()
		return {"message": f"Artist {artist.name} deleted successfully"}, 200


__all__ = ["ArtistCollection", "ArtistItem"]
