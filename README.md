# Dash Movie Dashboard (Starter)

This repository is a starter template for an interactive movie analytics dashboard built with Dash.

## Contents
- `app.py` - main Dash app
- `layouts.py` - layout builder
- `callbacks.py` - callback logic for interactivity
- `utils.py` - helper functions
- `data/Top Movies (Cleaned Data).csv` - dataset (included)
- `assets/style.css` - simple styling
- `requirements.txt` - Python dependencies

## Run locally
1. Create a virtual environment and install dependencies:
   ```
   python -m venv venv
   source venv/bin/activate   # or venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```

2. Run the app:
   ```
   python app.py
   ```

3. Open http://127.0.0.1:8050 in your browser.

## Next steps / Enhancements
- Add more filters (studio, country, MPAA rating)
- Add more charts (scatter with budget vs gross, profitability metrics)
- Add authentication if deploying publicly
- Clean and normalize 'Production/Financing Companies' to explode multiple companies per movie