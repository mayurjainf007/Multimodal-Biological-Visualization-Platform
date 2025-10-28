#!/usr/bin/env bash
# Usage: ./scripts/azure_deploy.sh <resource-group> <acr-name> <webapp-name> [region]
set -euo pipefail
RG=${1:-bio-rg}
ACR=${2:-bioacr$RANDOM}
APP=${3:-multimodal-bio-viz}
LOC=${4:-eastus}
IMAGE="${ACR}.azurecr.io/multimodal-bio-viz:latest"

# Login
az account show >/dev/null || az login

# Resource group
az group create -n "$RG" -l "$LOC"

# ACR
az acr create -n "$ACR" -g "$RG" --sku Basic --admin-enabled true
az acr login -n "$ACR"

# Build & push
az acr build -r "$ACR" -t "multimodal-bio-viz:latest" .

# App Service plan + Web App for Containers
az appservice plan create -g "$RG" -n "${APP}-plan" --is-linux --sku B1
az webapp create -g "$RG" -p "${APP}-plan" -n "$APP" -i "$IMAGE"

# Configure settings (edit as needed)
az webapp config appsettings set -g "$RG" -n "$APP" --settings PORT=8050 DATA_SOURCE=local

echo "Deployed https://$APP.azurewebsites.net"
