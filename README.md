# ⚽ FIFA World Cup 2026 Predictor

> An ML-powered FIFA World Cup 2026 predictor that generates daily match predictions and tracks live standings and the knockout bracket in real time.

🔗 **[Live App](https://fifawc-predictor.streamlit.app)**

---

## Overview

Built from scratch for the 2026 FIFA World Cup — the biggest in history with 48 teams across the USA, Canada, and Mexico. The app uses a machine learning model trained on over 25,000 international football matches to predict match outcomes, win probabilities, and scorelines for every fixture in the tournament.

Predictions are generated automatically each matchday. As real results come in, team ELO ratings update, group standings adjust, and the knockout bracket populates — all in real time.

---

## Pages

| Page | Description |
|---|---|
| **Fixtures** | Today's matches with predicted scores, win probabilities, and confidence levels |
| **Results** | All past predictions grouped by date, compared against actual results |
| **Standings** | Live group tables for all 12 groups (A–L), sorted by points, GD, GF |
| **Knockouts** | Full bracket from R32 → R16 → QF → SF → Final, auto-populates as teams advance |
| **Admin** | Password-protected panel to enter results, trigger predictions, and manage the app |

---

## How the Model Works

### Training Data
- 25,000+ competitive international matches (2000–2024)
- Source: Kaggle International Football Results dataset
- Friendlies excluded — only competitive matches used

### Features
- `elo_diff` — home team ELO minus away team ELO, computed historically from every match in the dataset

### Model
- `GradientBoostingClassifier` wrapped in `CalibratedClassifierCV` for accurate probability outputs
- Class imbalance (H/D/A) handled via `compute_sample_weight('balanced')`
- Time-based 80/20 train/test split — no data leakage
- ~57% accuracy (realistic for football; most commercial models sit at 53–58%)

### ELO Rating System
Every team's ELO is computed from scratch by replaying 25,000+ matches chronologically. After each real World Cup result, both teams' ratings update using the standard ELO formula with **K=40** (high-stakes tournament weight). Future predictions automatically reflect the updated ratings — the model improves as the tournament progresses.

---

## Tech Stack

```
Frontend      Streamlit
Database      Supabase (PostgreSQL)
ML Model      scikit-learn — GradientBoostingClassifier
Scheduling    APScheduler
Auth          Supabase Auth
Deployment    Streamlit Community Cloud
```

---

## Project Structure

```
fifawc/
├── app.py                  # Entry point, navigation, scheduler
├── db.py                   # All Supabase query functions
├── predictor.py            # ML prediction engine
├── scheduler.py            # Midnight IST prediction job
├── train.py                # One-time model training script
├── pages/
│   ├── 0_home.py
│   ├── 1_match_pred.py
│   ├── 2_past_pred.py
│   ├── 3_standings.py
│   ├── 4_ko.py
│   └── 5_login.py
├── static/
│   ├── fonts/              # Tusker Grotesk
│   ├── flags/              # 48 country flags
│   └── bg.png
└── model/
    └── wc_predictor.pkl
```

---

## Running Locally

```bash
git clone https://github.com/vrunstar/fifawc.git
cd fifawc

python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

pip install -r requirements.txt
```

Create a `.env` file:
```
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_KEY=your_service_key
```

```bash
streamlit run app.py
```

---

## Tournament Timeline

```
Group Stage       Jun 11 – Jun 28
Round of 32       Jun 28 – Jul 4
Round of 16       Jul 4  – Jul 7
Quarter Finals    Jul 9  – Jul 12
Semi Finals       Jul 14 – Jul 15
Final             Jul 19  —  MetLife Stadium, New Jersey
```

---

## License

MIT — see [LICENSE](LICENSE) for details.
