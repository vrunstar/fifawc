# FIFA World Cup Predictor

A Streamlit-based application for predicting FIFA World Cup match outcomes using Elo ratings and machine learning models.

## Features

- Match prediction for upcoming World Cup games
- Historical match data analysis
- Standings and knockout stage predictions
- Interactive web interface
- Scheduled predictions with APScheduler

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd fifawc
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv fifa
   fifa\Scripts\activate  # On Windows
   # or
   source fifa/bin/activate  # On macOS/Linux
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the Streamlit app:
```bash
streamlit run app.py
```

Navigate through the pages:
- Home: Overview and introduction
- Match Prediction: Predict individual matches
- Past Predictions: View historical predictions
- Standings: Current team standings
- Knockout: Knockout stage predictions
- Login: User authentication

## Data

The application uses historical FIFA match data stored in `data/` directory:
- `historical.csv`: Historical match results
- `computed_elo.csv`: Computed Elo ratings
- `results.csv`: Match results data

## Model

The prediction model is trained using machine learning algorithms on Elo ratings and historical performance data. See `train.py` for training details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License.