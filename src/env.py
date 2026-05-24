"""
Centralized environment variables configuration.
All environment variables are loaded here and imported from this module.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Configuration
API_PORT = int(os.getenv("API_PORT", 8000))

# Convex API URL
CONVEX_URL = os.getenv("CONVEX_URL", "https://standing-wombat-211.convex.site")

# Scheduler Configuration
TRAINING_INTERVAL_HOURS = int(os.getenv("TRAINING_INTERVAL_HOURS", 24))
EDA_INTERVAL_HOURS = int(os.getenv("EDA_INTERVAL_HOURS", 24))

# Uber Authentication
UBER_EMAIL = os.getenv("uber_email")

# SMTP Configuration (Email Notifications)
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
