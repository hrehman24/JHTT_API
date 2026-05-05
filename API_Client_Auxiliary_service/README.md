# API Client and Auxiliary Service

This folder currently contains:

1. `PWP_JHHT_CLIENT/`: Streamlit client application
2. `auxiliary_service/`: Auxiliary analytics/recommendation service (Flask)

Main API used by both components:

- `http://130.162.240.153:5000/Beatify/api/v1`

## Why Separate Components

- The **client** focuses on user interaction, resource browsing, and data entry.
- The **auxiliary service** handles aggregation and recommendation logic that would be inconvenient to keep inside the main API server.

## Quick Start

### Client

```bash
cd API_Client_Auxiliary_service/PWP_JHHT_CLIENT
pip install -r requirements.txt
streamlit run app.py
```

### Auxiliary Service

```bash
cd API_Client_Auxiliary_service/auxiliary_service
pip install -r requirements.txt
python service.py
```

Service base URL:

- `http://localhost:7000`

Component documentation:

- [PWP_JHHT_CLIENT/README.md](https://github.com/Heiguli/PWP_JHHT_CLIENT/blob/main/README.md)
- [auxiliary_service/README.md](auxiliary_service/README.md)
