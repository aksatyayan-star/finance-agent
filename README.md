# Finance Buddy - AI Financial Advisor

Finance Buddy is a multi-capable financial advisor agent built with the Google ADK. It integrates with various financial data sources to provide stock analysis, portfolio management, and answers to financial questions.

## Features

*   **Modular Architecture:** The agent is built with a scalable, modular architecture, including components for data ingestion, user profiling, analysis, portfolio management, and a RAG-powered knowledge base.
*   **Data Ingestion:** Integrates with Alpha Vantage, FRED, and NewsAPI.org to fetch real-time and historical market data, economic indicators, and financial news.
*   **User Profiling:** Manages user financial profiles, including risk tolerance and investment goals, using a simple JSON-based database.
*   **Portfolio Management:** Allows users to track their investment portfolios, analyze performance, and receive basic asset allocation suggestions.
*   **Analysis Engine:** Provides stock analysis with key metrics and relevant macroeconomic context.
*   **Proactive Alerting:** A monitoring system that checks for significant price movements, news events, and technical levels for stocks in a user's portfolio.
*   **RAG Knowledge Base:** Uses a Retrieval-Augmented Generation (RAG) pipeline with Zerodha Varsity articles to answer conceptual financial questions.

## Deployment to Google Cloud Run

This application is designed to be deployed as a containerized web service on Google Cloud Run.

### 1. Prerequisites

*   A Google Cloud Platform (GCP) project.
*   The `gcloud` CLI installed and authenticated.
*   An Artifact Registry repository created in your GCP project.
*   A configured Cloud Build trigger connected to your source code repository.

### 2. Environment Variables

Before deploying, you must have the following environment variables available to your Cloud Run service. It is recommended to manage these using a secret manager like Google Secret Manager and expose them to the Cloud Run service.

```
# --- Data Source API Keys ---
ALPHA_VANTAGE_API_KEY="YOUR_ALPHA_VANTAGE_API_KEY"
FRED_API_KEY="YOUR_FRED_API_KEY"
NEWS_API_KEY="YOUR_NEWS_API_KEY"

# --- GCP and Vertex AI Configuration ---
GCP_PROJECT_ID="YOUR_GCP_PROJECT_ID"
GCP_REGION="us-central1"
VECTOR_SEARCH_INDEX_ID="YOUR_VECTOR_SEARCH_INDEX_ID"
VECTOR_SEARCH_ENDPOINT_ID="YOUR_VECTOR_SEARCH_ENDPOINT_ID"
VECTOR_SEARCH_DEPLOYED_INDEX_ID="YOUR_VECTOR_SEARCH_DEPLOYED_INDEX_ID"
```

**Note:** The `Dockerfile` does **not** copy any local `.env` file into the container.

### 3. Running the Deployment

The deployment is automated via the `cloudbuild.yaml` file in this repository.

1.  **Connect to Cloud Build:** Connect your source code repository (e.g., GitHub, Bitbucket) to Google Cloud Build.
2.  **Create a Trigger:** Create a Cloud Build trigger that points to the `cloudbuild.yaml` file. You can configure it to run on pushes to a specific branch (e.g., `main`).
3.  **Run the Trigger:** Push your code to the configured branch to automatically start the build and deployment process. Alternatively, you can run the trigger manually from the GCP console.
4.  **Monitor the Build:** You can monitor the build, push, and deploy steps in the Cloud Build history section of the GCP console. The service will be deployed to Cloud Run in the region specified in the `cloudbuild.yaml` file.
