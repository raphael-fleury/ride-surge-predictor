# ride-surge-predictor

A CLI application to collect Uber ride data, extract pricing via LLMs, process, and train Machine Learning models.

## Installation

1. Clone the repo.
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Install Playwright browsers (for headless data collection):
   ```bash
   playwright install
   ```
4. Set your Credentials & API keys:
   Using Playwright to extract DOM elements.
   Setup a `.env` file in the root of the project. Because Uber uses OTP (SMS/Email code) for login, the script will pause and wait for you to type the code manually in the browser window, then it will save the session automatically. **Uber sessions are valid for 180 days (6 months).** When the 6-month period is reached and the session expires, the script will automatically send an email to notify you that intervention is needed.
   
   To enable this email notification, you must fill in the SMTP credentials (e.g. Gmail app password) in your `.env` file:
   ```env
   uber_email="your-uber-email@example.com"

   # SMTP Configuration (Example using Gmail)
   SMTP_SERVER="smtp.gmail.com"
   SMTP_PORT=587
   SMTP_USER="your-email-used-to-send@gmail.com"
   SMTP_PASS="your-app-specific-password"
   ```

## Usage

You can run each phase of the data pipeline using `main.py`:

> **Note:** For Machine Learning models to learn accurately and capture ride pricing patterns, waiting times, weekend spikes, and varying weather phenomena, we strongly recommend leaving `--collect` running continuously for **at least 1 to 4 weeks** before attempting the `--process` and `--train` phases. Otherwise, your trees (XGBoost/LightGBM) will severely overfit a tinyt dataset.

```bash
python main.py --collect
python main.py --process
python main.py --eda
python main.py --train
python main.py --server
```

* `--collect`: Runs Playwright headless browser to load predefined routes and directly extracts pricing and wait times locally into `data/interim/uber_rides_log.csv`.
* `--process`: Cleans data and engineers features for ML.
* `--eda`: Runs Exploratory Data Analysis.
* `--train`: Trains and evaluates the ML prediction models.
* `--server`: Starts the prediction API server with **automatic EDA & Training scheduler** (runs every 24 hours).

### 🤖 Automated EDA & Training (Every 24 Hours)

The API server includes an **automatic scheduler** that executes EDA and training tasks every 24 hours:

```bash
python main.py --server
```

**Features:**
- ✅ Automatically runs EDA every 24 hours
- ✅ Automatically trains models every 24 hours (1 hour after EDA)
- ✅ Detailed logging in `logs/scheduler.log`
- ✅ Monitor status via HTTP endpoints: `/scheduler/status` and `/scheduler/jobs`
```

## Enviroment Variables template (.env)
uber_login=
uber_password=