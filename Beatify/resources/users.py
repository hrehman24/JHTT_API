"""User API resources."""

from flask import request
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from ..models import db, User


class UserCollection(Resource):
    def get(self):
        user_list = []
        all_users = User.query.all()
        for user in all_users:
            user_list.append({"id": user.id, "name": user.name})
        return user_list

    def post(self):
        if not request.is_json:
            return {"message": "Request content type must be JSON"}, 415
        incoming_data = request.json
        required_fields = ["name"]
        if not all(field in incoming_data for field in required_fields):
            return {"message": "Incomplete request - missing fields"}, 400
        try:
            user_name = incoming_data["name"]
        except (ValueError, TypeError):
            return {"message": "Invalid data types for fields"}, 400
        new_user = User(name=user_name)
        db.session.add(new_user)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return {"message": "Database integrity error - possible duplicate entry"}, 400
        return {"message": f"User {user_name} created successfully!"}, 201

    def delete(self):
        num_deleted = User.query.delete()
        db.session.commit()
        return {"message": f"Deleted {num_deleted} users"}, 200


class UserItem(Resource):
    def get(self, id):
        user = User.query.get(id)
        if not user:
            return {"message": "User not found"}, 404
        playlist_list = []
        for playlist in user.playlists:
            playlist_list.append({"id": playlist.id, "name": playlist.name})
        return {"id": user.id, "name": user.name, "playlists": playlist_list}

    def put(self, id):
        user = User.query.get(id)
        if not user:
            return {"message": "User not found"}, 404
        if not request.is_json:
            return {"message": "Request content type must be JSON"}, 415
        incoming_data = request.json
        required_fields = ["name"]
        if not all(field in incoming_data for field in required_fields):
            return {"message": "Incomplete request - missing fields"}, 400
        try:
            user.name = incoming_data["name"]
        except (ValueError, TypeError):
            return {"message": "Invalid data types for fields"}, 400
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return {"message": "Database integrity error - possible duplicate entry"}, 400
        return {"message": f"User {user.name} updated successfully!"}, 200

    def delete(self, id):
        user = User.query.get(id)
        if not user:
            return {"message": "User not found"}, 404
        db.session.delete(user)
        db.session.commit()
        return {"message": f"User {user.name} deleted successfully"}, 200


__all__ = ["UserCollection", "UserItem"]
