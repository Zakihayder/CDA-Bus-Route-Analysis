# CDA Bus Route Analysis (Process Mining Project)

This project applies process mining to CDA bus route schedules and provides an interactive Streamlit dashboard with:

- route/process discovery from event logs,
- performance and bottleneck analytics,
- an agentic trip planner (Task 5),
- personal route mapping for team members (Task 6 bonus).

## Project Structure

```text
code/
  app.py                # Main Streamlit app (Tasks 3, 4, 5, 6)
  Scraper.py            # Task 1 base route extraction
  extraction.py         # Task 1 stop/timing extraction from route PDFs
  trace_gen.py          # Task 2 merged XES generation
  Total_Trips.py        # Trip count extraction
  AI_agent.py           # Optional terminal-based agent script

data/
  routes.csv
  Total_Trips.csv
  merged_event_log.xes
  extracted_routes/     # Per-route stop/timing CSVs
```

## Features by Task

### Task 1 - Data Extraction & CSV Generation

- Scrapes CDA route metadata to `data/routes.csv`.
- Extracts stop/timing tables from route PDFs into `data/extracted_routes/*.csv`.

### Task 2 - Trace Log Construction

- Merges extracted route CSVs and converts to XES.
- Outputs `data/merged_event_log.xes` for process mining.

### Task 3 - Process Discovery & Interactive GUI

- Displays full-network and route-specific process maps.
- Supports route filtering from sidebar.
- Shows transition labels with time and frequency.

### Task 4 - Performance & Bottleneck Analytics

- Shows avg/min/max throughput.
- Computes bottlenecks and highlights top slow transitions.
- Visually marks route start/end nodes.
- Removes artificial cycle wrap edges from map rendering.

### Task 5 - Agentic AI Trip Planner

- Natural-language Q&A grounded in extracted CDA schedule data.
- Fast local mode for low-latency responses.
- Dropdown-based route planner for deterministic best-route output.
- Route optimization: fewer buses first, then minimum travel time.

### Task 6 (Bonus) - Personal Route Map

- Member-wise route generation from FAST University to nearest home stop.
- Schematic route map + actual map view.
- Member record management in UI.
- CSV export for report submission.

## Requirements

- Python 3.10+
- Chrome/Chromedriver (for Selenium scraping)
- Tesseract OCR + Poppler (for PDF OCR scripts)

Recommended Python packages:

```bash
pip install streamlit pandas pm4py selenium webdriver-manager requests pdf2image pytesseract pillow pydeck langchain-google-genai
```

## Setup

1. Clone repo and enter folder:

```bash
git clone <your-repo-url>
cd CDA_Bus_Route_Analysis
```

2. (Optional but recommended) create virtual environment:

```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

If you do not have a `requirements.txt`, use the package command from the Requirements section.

## Data Pipeline (End-to-End)

Run from project root.

1. Task 1 base scraper:

```bash
python code/Scraper.py
```

2. Task 1 route PDF extraction:

```bash
python code/extraction.py
```

3. Trip count extraction:

```bash
python code/Total_Trips.py
```

4. Task 2 XES generation:

```bash
python code/trace_gen.py
```

## Run Dashboard

```bash
streamlit run code/app.py
```

Then open the local URL shown in terminal (usually `http://localhost:8501`).

## App Usage Guide

### Sidebar

- `Select Route Segment`: switch between full network and specific route direction.
- `Enable process map analytics`: enable heavy map/analytics rendering.
- `Use enhanced network maps`: DOT-based styled map rendering.
- `Map detail (max edges)`: control density of displayed edges.
- `Fast mode`: use fully grounded local answers for planner/chat.

### Task 5 Planner

- Use `From` and `Where to` dropdowns for deterministic best route.
- Click `Find Best Route` to get:
  - total buses,
  - estimated travel time,
  - next departure,
  - step-by-step route segments.

### Task 6 Bonus

- Fill `Member Name`, `Home Area`, and `Nearest CDA Stop to Home`.
- Click `Generate Personal Route`.
- View:
  - Schematic route map,
  - Actual map view,
  - summary table and CSV export.

## Troubleshooting

### Streamlit command exits with non-zero code

- Ensure dependencies are installed in active environment.
- Verify required data files exist in `data/`.
- Run quick syntax check:

```bash
python -m py_compile code/app.py
```

### OCR scripts fail

- Set valid local paths for Tesseract and Poppler in:
  - `code/extraction.py`
  - `code/Total_Trips.py`

### Actual map view cannot render fully

- Geocoding may fail for some stop names.
- App will still show complete step-by-step route instructions as fallback.

## Suggested Submission Bundle

- `report/` with screenshots and explanation for Tasks 1-6.
- `code/` with all final scripts.
- `data/` with required CSV/XES artifacts (as needed by instructor constraints).

## Notes

- This repository is currently configured for a practical, reproducible academic workflow.
- Keep API keys and personal tokens out of source code and use environment variables.
