# GCP Cloud Run Deployment

## Prereqs
- gcloud CLI, billing-enabled project, Artifact Registry API enabled

## Steps
```bash
chmod +x scripts/gcp_deploy.sh
./scripts/gcp_deploy.sh my-project us-central1
```
The script builds, pushes, and deploys the container to Cloud Run on port 8050.
