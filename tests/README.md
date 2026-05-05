# How to Run Tests

## API Endpoints

| Resource Name | Resource URL | Resource Description | Supported Methods | Implemented |
|---|---|---|---|---|
| Artists Collection | http://localhost:5000/Beatify/api/v1/artists | Collection of all artists | GET, POST, DELETE | Yes |
| Artist Item | http://localhost:5000/Beatify/api/v1/artists/\<id\> | A single artist | GET, PUT, DELETE | Yes |
| Albums Collection | http://localhost:5000/Beatify/api/v1/albums | Collection of all albums | GET, POST | Yes |
| Album Item | http://localhost:5000/Beatify/api/v1/albums/\<id\> | A single album | GET, PUT, DELETE | Yes |
| Tracks Collection | http://localhost:5000/Beatify/api/v1/tracks | Collection of all tracks | GET, POST, DELETE | Yes |
| Track Item | http://localhost:5000/Beatify/api/v1/tracks/\<id\> | A single track | GET, PUT, DELETE | Yes |
| Users Collection | http://localhost:5000/Beatify/api/v1/users | Collection of all users | GET, POST, DELETE | Yes |
| User Item | http://localhost:5000/Beatify/api/v1/users/\<id\> | A single user with playlists | GET, PUT, DELETE | Yes |
| Playlists Collection | http://localhost:5000/Beatify/api/v1/playlists | Collection of all playlists | GET, POST, DELETE | Yes |
| Playlist Item | http://localhost:5000/Beatify/api/v1/playlists/\<id\> | A single playlist with tracks and users | GET, PUT, DELETE | Yes |

## Prerequisites

Make sure you have the required packages installed:

```bash
pip install flask flask-restful flask-sqlalchemy pytest pytest-cov
```

Or install from the requirements file:

`setup.py` can install requirements and start the API automatically.
If you want to do everything manually:

```bash
pip install -r Database_folder/requirements.txt
pip install flask-restful pytest pytest-cov
```

## Running the Tests

From project root run:

```bash
python -m pytest tests/api_test.py -v
```

The `-v` flag gives verbose output showing each test name and result.

## Running with Coverage Report

To see how much of the code is covered by tests:

```bash
python -m pytest tests/api_test.py -v --cov=Beatify --cov-report=term-missing
```

This will show:
- Which files were tested
- The percentage of lines covered
- Which lines were **not** covered (if any)

## Quick Summary

| Command | What it does |
|---|---|
| `python -m pytest tests/api_test.py` | Run API tests |
| `python -m pytest tests/api_test.py -v` | Run API tests with detailed output |
| `python -m pytest tests/api_test.py --cov=Beatify` | Run API tests + show coverage % |
| `python -m pytest tests/api_test.py --cov=Beatify --cov-report=term-missing` | Run API tests + show missing lines |
| `python -m pytest tests/api_test.py -k "Artist"` | Run only Artist tests |
| `python -m pytest tests/api_test.py -k "User"` | Run only User tests |
| `python -m pytest tests/api_test.py -k "Playlist"` | Run only Playlist tests |
