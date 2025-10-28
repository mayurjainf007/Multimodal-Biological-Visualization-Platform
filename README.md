[![CI](https://img.shields.io/github/actions/workflow/status/OWNER/REPO/ci.yml?branch=main)](#)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](#)
[![Docker](https://img.shields.io/badge/docker-ready-brightgreen)](#)


# Multimodal Biological Visualization Platform

**Stack:** Plotly Dash, Python, (optional) Snowflake, (optional) Azure App Service

Explore spatial transcriptomics alongside clinical features.

## Quickstart (Local)
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export DATA_SOURCE=local
python app.py
```
Open http://localhost:8050

## Using Snowflake (Optional)
Set `DATA_SOURCE=snowflake` and `SNOWFLAKE_*` envs. See `utils/snowflake_connector.py` for details.

## Docker
```bash
docker build -t multimodal-bio-viz -f docker/Dockerfile .
docker run -p 8050:8050 --env DATA_SOURCE=local multimodal-bio-viz
```


## Screenshots
![App Screenshot](docs/screenshots/screenshot.png)
