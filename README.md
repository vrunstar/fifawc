# ⚽ FIFA World Cup 2026 Predictor

A real-time match prediction app for the 2026 FIFA World Cup, built with Streamlit and powered by a machine learning model trained on 25,000+ international football matches.

🔗 **Live App:** [fifawc-predictor.streamlit.app](https://fifawc-predictor.streamlit.app)

---

## Features

- **Match Predictions** — Daily predictions for today's fixtures with win/draw/loss probabilities and predicted scorelines
- **Results** — All past predictions grouped by date, compared against actual results
- **Group Standings** — Live standings for all 12 groups (A–L), updated after every match
- **Knockout Bracket** — Full R32 → R16 → QF → SF → Final bracket, auto-populates as teams advance
- **Admin Panel** — Password-protected panel to enter real match results, trigger predictions, and update ELO ratings

---

## How It Works

### ML Model
- Trained on 25,000+ competitive international matches (2000–2024) from the Kaggle International Football Results dataset
- Features: `elo_diff` (home ELO − away ELO)
- Model: `GradientBoostingClassifier` with `CalibratedClassifierCV` for probability calibration
- Class imbalance handled via `compute_sample_weight(balanced)`
- Time-based train/test split (80/20) to prevent data leakage
- Accuracy: ~57% (realistic for football prediction)

### ELO Rating System
- All 48 teams start with historically computed ELO ratings built from match-by-match processing of 25,000+ games
- After every real result, both teams' ELO ratings are updated using the standard ELO formula with K=40 (World Cup weight)
- Future predictions automatically use updated ELO — model improves as the tournament progresses

### Predictions
- Generated daily at midnight IST via APScheduler
- Can also be triggered manually from the Admin panel
- Stored in Supabase and displayed on the Fixtures page

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit |
| Database | Supabase (PostgreSQL) |
| ML Model | scikit-learn (GradientBoostingClassifier) |
| Scheduling | APScheduler |
| Data Processing | pandas, numpy |
| Auth | Supabase Auth |
| Deployment | Streamlit Community Cloud |

---

## Project Structure

```
fifawc/
├── app.py                  # Entry point, navigation, scheduler bootstrap
├── db.py                   # All Supabase query functions
├── predictor.py            # ML prediction engine
├── scheduler.py            # APScheduler midnight IST job
├── train.py                # Model training script (run once)
├── pages/
│   ├── 0_home.py           # Welcome page
│   ├── 1_match_pred.py     # Today's fixtures & predictions
│   ├── 2_past_pred.py      # Past predictions grouped by date
│   ├── 3_standings.py      # Live group standings
│   ├── 4_ko.py             # Knockout bracket
│   └── 5_login.py          # Admin panel
├── static/
│   ├── fonts/              # Tusker Grotesk font files
│   ├── flags/              # Country flag PNGs (48 teams)
│   └── bg.png              # Background image
├── model/
│   └── wc_predictor.pkl    # Trained model
└── data/
    └── results.csv         # Historical match data (training)
```

---

## Database Schema

| Table | Purpose |
|---|---|
| `teams` | All 48 teams with ELO, xG, xGA, FIFA rank |
| `fixtures` | All 104 matches with kickoff times (UTC + IST) |
| `prediction` | Model predictions per match |
| `results` | Actual match results entered via admin |
| `standings` | Live group standings (auto-updated) |

---

## Running Locally

```bash
# Clone the repo
git clone https://github.com/vrunstar/fifawc.git
cd fifawc

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
# Create .env file:
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_KEY=your_service_key

# Run the app
streamlit run app.py
```

---

## Admin Panel

The Admin page is password-protected via Supabase Auth. Only the registered admin user can:
- Enter real match results
- Trigger today's predictions manually
- Results automatically update ELO ratings and group standings

---

## Deployment

Deployed on **Streamlit Community Cloud**. Secrets (Supabase credentials) are stored in the app's Secrets settings, not in the repository.

---

## Tournament Schedule

- **Group Stage:** June 11 – June 28, 2026
- **Round of 32:** June 28 – July 4, 2026
- **Round of 16:** July 4 – July 7, 2026
- **Quarter Finals:** July 9 – July 12, 2026
- **Semi Finals:** July 14 – July 15, 2026
- **Final:** July 19, 2026 — MetLife Stadium, New Jersey

---
## License

MIT License — see [LICENSE](LICENSE) for details.
