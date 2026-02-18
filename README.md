# Chicago Taxi & Weather Analytics Platform

A data analytics platform I built in my spare time to explore the relationship between weather conditions and taxi trip duration in Chicago. The project ingests public datasets from BigQuery, transforms them through a Medallion architecture, and visualizes insights in Looker Studio.

## What it does

- **Ingests** taxi trips and weather data from BigQuery public datasets
- **Transforms** data with dbt (Bronze → Silver → Gold layers)
- **Orchestrates** pipelines with Apache Airflow on Cloud Composer
- **Visualizes** results in an interactive Looker Studio dashboard

## Architecture

```
BigQuery (public datasets) → Cloud Functions → BigQuery (raw)
                                    ↓
                    dbt (Silver/Gold) + Airflow
                                    ↓
                         Looker Studio dashboard
```

**Tech stack:** Terraform, dbt, Apache Airflow, BigQuery, Cloud Functions, Looker Studio, GitHub Actions

## Quick start

1. Configure GitHub Secrets: `GCP_SA_KEY`, `GCP_PROJECT_ID`, `DEVELOPER_EMAIL`
2. Push to `main` – GitHub Actions deploys infrastructure and dbt models
3. Trigger the historical ingestion DAG in Airflow (one-time)
4. View the dashboard: [Looker Studio](https://lookerstudio.google.com/s/qfSVoIMVddw)

## Project structure

```
├── terraform/     # GCP infrastructure
├── dbt/           # Data transformations
├── airflow/       # Pipeline orchestration
├── functions/     # Cloud Functions (weather ingestion)
└── .github/       # CI/CD workflows
```

## Data

- **Period:** June–December 2023 (6 months)
- **Sources:** `bigquery-public-data.chicago_taxi_trips`, `bigquery-public-data.noaa_gsod`
- **Output:** ~3.8M taxi trips, weather correlations, daily aggregations

Built as a side project to practice end-to-end data engineering on GCP.
