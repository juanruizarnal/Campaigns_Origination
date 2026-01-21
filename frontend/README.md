# Alter-5 Origination Frontend

Streamlit application for the Alter-5 Origination Engine.

## Quick Start

```bash
# From project root
cd frontend

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py
```

## Structure

```
frontend/
├── app.py                    # Main entry point
├── pages/                    # Streamlit pages
│   ├── 1_📊_Dashboard.py     # Dashboard with metrics
│   ├── 2_🏢_Empresas.py      # Company search, enrichment & management
│   ├── 3_🚀_Nueva_Campaña.py # Campaign creation wizard
│   ├── 4_🏷️_Evaluacion_FEI.py # FEI evaluation
│   ├── 5_📋_Campañas.py      # Campaign list
│   └── 6_🔄_Originacion.py   # Origination pipeline
├── components/               # Reusable UI components
│   ├── metrics.py            # Metric cards
│   ├── feedback.py           # Alerts, progress bars
│   ├── forms.py              # Form inputs
│   └── tables.py             # Data tables
├── utils/                    # Utilities
│   ├── api.py                # Backend API wrapper
│   ├── session.py            # Session state management
│   ├── styles.py             # Custom CSS
│   └── helpers.py            # Formatting helpers
├── assets/                   # Static files
│   └── logo.png              # Logo
├── .streamlit/
│   └── config.toml           # Streamlit configuration
└── requirements.txt          # Dependencies
```

## Features

- **Dashboard**: Quick overview with metrics and recent campaigns
- **Nueva Campaña**: 4-step wizard for campaign creation from market triggers
- **Empresas**: Browse, search, enrich companies
- **Evaluación FEI**: Individual and batch FEI eligibility evaluation
- **Campañas**: View and manage existing campaigns
- **Originación**: Run full origination pipeline (Search → Enrich → Evaluate)

## Environment

Requires the backend to be configured with:
- `AIRTABLE_API_KEY`
- `AIRTABLE_BASE_ID`
- `ANTHROPIC_API_KEY`
- `GOOGLE_API_KEY`

