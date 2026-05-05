# Beatify Auxiliary Service

## Purpose

This service adds value on top of Beatify API by providing:

- Global analytics summary
- Top artists by derived track count
- User-level track recommendations

Main API target:

- `http://130.162.240.153:5000/Beatify/api/v1`

Service base URL (local):

- `http://localhost:7000`

## Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Service metadata and endpoint index |
| `/analytics/summary` | GET | Counts and high-level metrics |
| `/analytics/top-artists` | GET | Top artists by number of tracks |
| `/recommendations/user/{user_id}` | GET | Recommended tracks for a user |

## Install and Run

```bash
cd API_Client_Auxiliary_service/auxiliary_service
pip install -r requirements.txt
python service.py
```

## Notes

- This service expects Beatify list endpoints to return `id` fields (for artists, albums, tracks).
- If Beatify API is not running or unreachable, service endpoints return `503` with an explanatory message.

## Example Requests

You can use `sample_requests.http` in this folder, or run:

```bash
curl http://localhost:7000/analytics/summary
curl http://localhost:7000/analytics/top-artists
curl http://localhost:7000/recommendations/user/1
```

## Linting

```bash
cd API_Client_Auxiliary_service/auxiliary_service
pylint service.py --rcfile=../.pylintrc --reports=y
```

## Sources

- Flask docs: https://flask.palletsprojects.com/
- Requests docs: https://requests.readthedocs.io/
