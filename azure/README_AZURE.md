# Azure App Service (Container) Deployment

## Prereqs
- Azure CLI (`az`), Docker (optional locally), Azure subscription

## One-liner
```bash
chmod +x scripts/azure_deploy.sh
./scripts/azure_deploy.sh my-rg myacr123 multimodal-bio-viz westus3
```
Edit `app settings` in the script for environment variables (e.g., Snowflake creds or API keys).
