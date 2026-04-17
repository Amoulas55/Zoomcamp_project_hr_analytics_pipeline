# 📊 HR Analytics Data Pipeline: Employee Attrition Deep-Dive

**Data Engineering Zoomcamp — Final Project**

![Dashboard Screenshot](zoomcamp_project_visualizations.png)

---

## 🎯 Problem Statement

Employee attrition is one of the most expensive and disruptive challenges facing modern organizations. The cost of replacing a single employee can range from 50% to 200% of their annual salary when accounting for recruitment, onboarding, lost productivity, and institutional knowledge drain. Yet most HR departments still rely on reactive, manual reporting that only reveals attrition *after* it has already impacted the business.

**This project solves that problem** by building a fully automated, end-to-end batch data pipeline that:

1. **Ingests** the IBM HR Analytics Employee Attrition dataset (1,470 employee records with 35 attributes) into a cloud Data Lake.
2. **Loads** the raw data into a Data Warehouse for analytical querying.
3. **Transforms** the data using dbt into clean, optimized fact and dimension tables — with partitioning and clustering for cost-efficient queries.
4. **Visualizes** key attrition metrics in an interactive Streamlit dashboard, enabling HR leaders to instantly identify which departments, income brackets, and tenure milestones carry the highest turnover risk.

**Dataset:** [IBM HR Analytics Employee Attrition & Performance](https://www.kaggle.com/datasets/pavansubhasht/ibm-hr-analytics-attrition-dataset) (Kaggle)

---

## 🏗️ Architecture & Technologies

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Raw CSV     │────▶│  GCS Bucket  │────▶│  BigQuery    │────▶│  Streamlit   │
│  (data/)     │     │  (Data Lake) │     │  (DWH)       │     │  Dashboard   │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
       │                    │                    │                    │
       └─── Kestra Orchestration (multi-step DAG) ──────────────────┘
                            │
                     dbt Transformations
                     (stg → dim → fct)
```

| Component | Technology |
|---|---|
| **Cloud** | Google Cloud Platform (GCP) |
| **Infrastructure as Code** | Terraform |
| **Orchestration** | Kestra (Docker) |
| **Data Lake** | Google Cloud Storage (GCS) |
| **Data Warehouse** | Google BigQuery |
| **Transformations** | dbt (Data Build Tool) |
| **Dashboard** | Streamlit (Dockerized) |
| **Containerization** | Docker & Docker Compose |

---

## 🗄️ Data Warehouse Design

### dbt Models (3-layer architecture)

| Model | Type | Description |
|---|---|---|
| `stg_hr_data` | View | Cleans raw data, standardizes to `snake_case`, casts types, generates `snapshot_date` |
| `dim_employees` | Table | Employee dimension with feature-engineered `income_bracket` and `tenure_category` columns |
| `fct_attrition_stats` | Table | Core fact table with binary `attrition_flag` for dashboard metrics |

### Optimization — Partitioning & Clustering

- **`fct_attrition_stats`** is **partitioned by `snapshot_date`** (daily granularity). When querying a specific date range, BigQuery only scans the relevant partitions, reducing cost and improving speed.
- **`fct_attrition_stats`** and **`dim_employees`** are **clustered by `department`**. Since the dashboard heavily filters and groups by department, clustering physically co-locates this data for faster reads.

---

## 📈 Dashboard

The Streamlit dashboard satisfies all project requirements with **3 interactive tiles**:

| Tile | Type | What it shows |
|---|---|---|
| **Attrition Rate by Department** | Bar chart | Categorical distribution — identifies Sales as the highest-risk department |
| **Attrition by Years at Company** | Line chart | Temporal distribution — reveals critical tenure milestones (1-2 years peak) |
| **Income Bracket vs Attrition** | Bar chart | Entry-level employees show significantly higher turnover |

Plus **KPI scorecards** showing Total Headcount, Attrition Count, and Global Attrition Rate.

---

## 🚀 Reproducibility — Step by Step

### Prerequisites

| Tool | Purpose |
|---|---|
| [Google Cloud account](https://cloud.google.com/) | Cloud infrastructure |
| [Terraform](https://www.terraform.io/downloads) | Provision GCS + BigQuery |
| [Docker & Docker Compose](https://www.docker.com/) | Run Kestra + Dashboard |
| [Git](https://git-scm.com/) | Clone this repository |

### Step 1 — Clone & Configure

```bash
git clone https://github.com/Amoulas55/hr-analytics-pipeline.git
cd hr-analytics-pipeline
```

Create a GCP Service Account with **BigQuery Admin** + **Storage Admin** roles. Download its JSON key and save it as `google_credentials.json` in the project root.

```bash
# Set up environment variables
cp .env.example .env
# Edit .env with your GCP_PROJECT_ID and GCP_BUCKET_NAME
```

### Step 2 — Provision Infrastructure (Terraform)

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your project_id and bucket name

terraform init
terraform apply
```

Type `yes` when prompted. This creates:
- A GCS bucket (Data Lake)
- A BigQuery dataset (`hr_analytics_dataset`)

### Step 3 — Run the Pipeline (Kestra)

```bash
cd ..
docker compose up -d
```

This starts:
- **Kestra** on [http://localhost:8080](http://localhost:8080)
- **Streamlit Dashboard** on [http://localhost:8501](http://localhost:8501) (will show data after pipeline runs)

**Upload namespace files** (required so Kestra can access your data and credentials):

```bash
# Option A — use the helper script (requires curl + bash/Git Bash)
bash setup_kestra.sh

# Option B — manual upload via Kestra UI
#   Go to Namespaces → zoomcamp → Files (Editor)
#   Upload: google_credentials.json, data/hr_dataset.csv, and the entire dbt/ folder
```

Then create and run the flow in Kestra UI:
1. Go to **Flows** → **Create**
2. Copy-paste the contents of `orchestration/hr_pipeline.yaml`
3. Click **Save** → **Execute**

The pipeline will automatically:
1. Upload `data/hr_dataset.csv` to your GCS bucket
2. Load the CSV into BigQuery (`raw_hr_data` table)
3. Run `dbt build` to create the `stg_hr_data`, `dim_employees`, and `fct_attrition_stats` tables

### Step 4 — View the Dashboard

Open [http://localhost:8501](http://localhost:8501) in your browser. The Streamlit dashboard reads directly from BigQuery and displays all visualizations.

### Step 5 — Cleanup

```bash
# Tear down cloud resources
cd terraform
terraform destroy

# Stop containers
cd ..
docker compose down -v
```

---

## 📁 Project Structure

```
hr-analytics-pipeline/
├── data/
│   └── hr_dataset.csv              # Raw IBM HR dataset
├── terraform/
│   ├── main.tf                     # GCS bucket + BigQuery dataset
│   ├── variables.tf                # Parameterized (no hardcoded values)
│   └── terraform.tfvars.example    # Template for user's values
├── orchestration/
│   └── hr_pipeline.yaml            # Kestra flow: CSV → GCS → BQ → dbt
├── dbt/
│   ├── dbt_project.yml
│   ├── profiles.yml
│   └── models/
│       ├── sources.yml             # BigQuery source definition
│       ├── stg_hr_data.sql         # Staging: clean + cast + generate date
│       ├── dim_employees.sql       # Dimension: income brackets + tenure
│       └── fct_attrition_stats.sql # Fact: partitioned + clustered + flags
├── dashboard/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app.py                      # Streamlit dashboard (3 tiles + KPIs)
├── docker-compose.yml              # Kestra + Postgres + Dashboard
├── setup_kestra.sh                 # Uploads namespace files to Kestra
├── .env.example                    # Environment variable template
├── .gitignore
└── README.md
```

---

## 🎯 Evaluation Criteria Self-Assessment

| Criteria | Score | Evidence |
|---|---|---|
| Problem Description | ⭐⭐⭐⭐ | Clear problem statement with business context and dataset description |
| Cloud + IaC | ⭐⭐⭐⭐ | GCP (GCS + BigQuery) provisioned via Terraform |
| Data Ingestion (Batch) | ⭐⭐⭐⭐ | Multi-step Kestra DAG: CSV → GCS → BigQuery → dbt |
| Data Warehouse | ⭐⭐⭐⭐ | Partitioned by `snapshot_date`, clustered by `department` (with explanation) |
| Transformations | ⭐⭐⭐⭐ | 3 dbt models (staging → dimension → fact) |
| Dashboard | ⭐⭐⭐⭐ | Streamlit with 3 tiles (bar + line + bar) + KPI scorecards |
| Reproducibility | ⭐⭐⭐⭐ | `git clone` → `.env` → `terraform apply` → `docker compose up` |
