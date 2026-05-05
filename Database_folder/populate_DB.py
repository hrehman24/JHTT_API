import os
import sys


app_dir = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, app_dir)
from Beatify.models import db, app, Artist, Album, Track, User, Playlist

with app.app_context():
    # Artists
    artist1 = Artist(name="Radiohead")
    artist2 = Artist(name="Daft Punk")
    artist3 = Artist(name="Pink Floyd")
    artist4 = Artist(name="The Beatles")
    artist5 = Artist(name="Nirvana")
    db.session.add_all([artist1, artist2, artist3, artist4, artist5])

    # Albums
    album1 = Album(name="OK Computer", artist=artist1)
    album2 = Album(name="Discovery", artist=artist2)
    album3 = Album(name="The Dark Side of the Moon", artist=artist3)
    album4 = Album(name="Abbey Road", artist=artist4)
    album5 = Album(name="Nevermind", artist=artist5)
    album6 = Album(name="Kid A", artist=artist1)
    album7 = Album(name="Random Access Memories", artist=artist2)
    db.session.add_all([album1, album2, album3, album4, album5, album6, album7])

    # Tracks
    track1 = Track(name="Paranoid Android", length=386, album=album1)
    track2 = Track(name="One More Time", length=320, album=album2)
    track3 = Track(name="Karma Police", length=263, album=album1)
    track4 = Track(name="Lucky", length=258, album=album1)
    track5 = Track(name="Digital Love", length=301, album=album2)
    track6 = Track(name="Time", length=413, album=album3)
    track7 = Track(name="Money", length=382, album=album3)
    track8 = Track(name="Breathe", length=169, album=album3)
    track9 = Track(name="Come Together", length=259, album=album4)
    track10 = Track(name="Here Comes the Sun", length=185, album=album4)
    track11 = Track(name="Something", length=182, album=album4)
    track12 = Track(name="Smells Like Teen Spirit", length=301, album=album5)
    track13 = Track(name="Come as You Are", length=219, album=album5)
    track14 = Track(name="Everything in Its Right Place", length=250, album=album6)
    track15 = Track(name="Get Lucky", length=369, album=album7)
    db.session.add_all([
        track1, track2, track3, track4, track5,
        track6, track7, track8, track9, track10,
        track11, track12, track13, track14, track15
    ])

    # Users
    user1 = User(name="Alice")
    user2 = User(name="Bob")
    user3 = User(name="Charlie")
    db.session.add_all([user1, user2, user3])

    # Playlists
    playlist1 = Playlist(name="Favorites", description="My favorite songs")
    playlist1.users.append(user1)
    playlist1.tracks.extend([track1, track2, track6, track9, track12])

    playlist2 = Playlist(name="Chill Vibes", description="Relaxing tracks to unwind")
    playlist2.users.append(user2)
    playlist2.tracks.extend([track5, track8, track10, track15])

    playlist3 = Playlist(name="Rock Classics", description="Best rock songs of all time")
    playlist3.users.append(user3)
    playlist3.users.append(user1)
    playlist3.tracks.extend([track3, track7, track9, track11, track12, track13])

    db.session.add_all([playlist1, playlist2, playlist3])

    db.session.commit()
