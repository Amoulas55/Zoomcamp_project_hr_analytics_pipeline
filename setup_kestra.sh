#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────
# Upload required namespace files to Kestra so the pipeline
# can access google_credentials.json, hr_dataset.csv, and dbt/
# ─────────────────────────────────────────────────────────────
set -euo pipefail

KESTRA_URL="${KESTRA_URL:-http://localhost:8080}"
NAMESPACE="zoomcamp"

echo "⏳ Uploading google_credentials.json ..."
curl -s -X PUT "${KESTRA_URL}/api/v1/namespaces/${NAMESPACE}/files?path=/google_credentials.json" \
  -H "Content-Type: multipart/form-data" \
  -F "fileContent=@google_credentials.json"

echo "⏳ Uploading hr_dataset.csv ..."
curl -s -X PUT "${KESTRA_URL}/api/v1/namespaces/${NAMESPACE}/files?path=/hr_dataset.csv" \
  -H "Content-Type: multipart/form-data" \
  -F "fileContent=@data/hr_dataset.csv"

echo "⏳ Uploading dbt/ directory ..."
for f in dbt/dbt_project.yml dbt/profiles.yml dbt/models/sources.yml dbt/models/stg_hr_data.sql dbt/models/dim_employees.sql dbt/models/fct_attrition_stats.sql; do
  echo "   → ${f}"
  curl -s -X PUT "${KESTRA_URL}/api/v1/namespaces/${NAMESPACE}/files?path=/${f}" \
    -H "Content-Type: multipart/form-data" \
    -F "fileContent=@${f}"
done

echo "✅ All namespace files uploaded to Kestra (namespace: ${NAMESPACE})"
