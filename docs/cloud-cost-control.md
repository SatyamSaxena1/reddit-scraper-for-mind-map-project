# Cloud Cost Control

Cloud processing is intentionally deferred until the local exporter works.

## Azure

- Create one dedicated resource group for this project.
- Configure budget alerts before deploying resources.
- Prefer Azure Functions Consumption or Container Apps Jobs.
- Avoid always-on services unless explicitly needed.
- Use Blob Storage only for raw exports or media backups.
- Store secrets in Azure Key Vault or app environment variables.
- Do not use paid GPU or AI services without explicit approval.
- Document teardown commands before deploying.

## DigitalOcean

- Enable billing alerts; they are disabled by default.
- Prefer App Platform static hosting for the browser graph viewer.
- Use `.do/app.yaml` for the static viewer only after the repo changes are pushed.
- Avoid Spaces unless media backup is worth the monthly base cost.
- Avoid Managed Databases for the first version.
- Use Droplets only for short-lived experiments and destroy them when idle.
