"""API registration in the Beatify module layout."""

from pathlib import Path

from flask import render_template_string, send_file
from flask_restful import Api

from .models import app
from .resources import (
    AlbumCollection,
    AlbumItem,
    ArtistCollection,
    ArtistItem,
    PlaylistCollection,
    PlaylistItem,
    TrackCollection,
    TrackItem,
    UserCollection,
    UserItem,
)
from .utils import build_root_payload, json_response
from .models import db

api = Api(app, prefix="/Beatify/api/v1")

api.add_resource(ArtistCollection, "/artists")
api.add_resource(ArtistItem, "/artists/<int:id>")
api.add_resource(TrackCollection, "/tracks")
api.add_resource(TrackItem, "/tracks/<int:id>")
api.add_resource(AlbumCollection, "/albums")
api.add_resource(AlbumItem, "/albums/<int:id>")
api.add_resource(UserCollection, "/users")
api.add_resource(UserItem, "/users/<int:id>")
api.add_resource(PlaylistCollection, "/playlists")
api.add_resource(PlaylistItem, "/playlists/<int:id>")


@app.route("/")
def index():
    """Root endpoint with usage information."""
    return json_response(build_root_payload("http://130.162.240.153:5000/Beatify/api/v1"))


@app.route("/openapi.yaml")
@app.route("/Beatify/api/v1/openapi.yaml")
def openapi_spec():
    """Serve the OpenAPI YAML document."""
    spec_path = Path(__file__).resolve().parent.parent / "docs" / "openapi.yaml"
    return send_file(spec_path, mimetype="application/yaml")


SWAGGER_UI_TEMPLATE = """<!doctype html>
<html lang=\"en\">
    <head>
        <meta charset=\"utf-8\" />
        <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
        <title>Beatify API Docs</title>
        <link rel=\"stylesheet\" href=\"https://unpkg.com/swagger-ui-dist@5/swagger-ui.css\" />
        <style>
            body { margin: 0; background: #f5f7fb; }
            #swagger-ui { max-width: 1200px; margin: 0 auto; }
        </style>
    </head>
    <body>
        <div id=\"swagger-ui\"></div>
        <script src=\"https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js\"></script>
        <script>
            window.ui = SwaggerUIBundle({
                url: '{{ spec_url }}',
                dom_id: '#swagger-ui',
                deepLinking: true,
                presets: [SwaggerUIBundle.presets.apis],
            });
        </script>
    </body>
</html>
"""


@app.route("/docs")
@app.route("/Beatify/api/v1/docs")
def swagger_docs():
        """Render interactive Swagger UI for the OpenAPI spec."""
        return render_template_string(SWAGGER_UI_TEMPLATE, spec_url="/Beatify/api/v1/openapi.yaml")


def start_api(debug: bool = True):
    """Create database tables and run the development server."""
    with app.app_context():
        db.create_all()
    print("App is running!")
    app.run(debug=debug)


if __name__ == "__main__":
    start_api(debug=True)
