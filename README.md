# Macro Dashboard

A lightweight **Streamlit** app that pulls U.S. labor-market time-series data from the **FRED** API and displays interactive charts for employment, inflation, and non-farm payrolls (NFP).

---

## Quick Start

```bash
# 1) Clone repo
git clone https://github.com/waihin26/macro-dashboard.git
cd macro-dashboard

# 2) Create virtual env
python3 -m venv .venv
source .venv/bin/activate        # Windows: .\.venv\Scripts\activate

# 3) Install dependencies
pip install -r requirements.txt

# 4) Add your FRED API key
export FRED_API_KEY="YOUR_FRED_API_KEY"   # Windows (PowerShell): setx FRED_API_KEY "YOUR_FRED_API_KEY"

# 5) Run the app
streamlit run Home.py
