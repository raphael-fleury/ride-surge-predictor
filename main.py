# /// script
# dependencies = ["playwright", "bs4", "requests", "pandas", "scikit-learn", "xgboost", "joblib", "matplotlib", "seaborn", "python-dotenv"]
# ///

import argparse
import os
from src.env import API_PORT as PORT

parser = argparse.ArgumentParser(description="Ride Surge Predictor Data Pipeline")
parser.add_argument("--collect", action="store_true", help="Run the data collection (Playwright Scraping + Weather API -> CSV)")
parser.add_argument("--process", action="store_true", help="Clean data and engineer features for ML")
parser.add_argument("--eda", action="store_true", help="Run Exploratory Data Analysis on processed data")
parser.add_argument("--train", action="store_true", help="Train and evaluate ML models")
parser.add_argument("--server", action="store_true", help="Start the HTTP prediction server")

def check_directories():
    base = "data"
    subdirs = ["raw", "interim", "processed", "archive"] 
    for subdir in subdirs:
        target = os.path.join(base, subdir)
        if not os.path.isdir(target):
            os.makedirs(target, exist_ok=True)
            
    # Also ensure models directory exists
    os.makedirs("models", exist_ok=True)
    return True

if __name__ == "__main__":
    args = parser.parse_args()
    check_directories()
    
    if args.collect:
        from src.collection import run_collection
        print("Initializing Collection Pipeline...")
        run_collection()
    elif args.process:
        from src.processing import run_processing
        print("Initializing Processing Pipeline...")
        run_processing()
    elif args.eda:
        from src.eda import run_eda
        print("Initializing EDA Pipeline...")
        run_eda()
    elif args.train:
        from src.models import run_training
        print("Initializing ML Training Pipeline...")
        run_training()
    elif args.server:
        import uvicorn
        from src.http import create_app
        
        app = create_app()
        print("\n🚀 Starting Ride Surge Predictor API Server...")
        print(f"📍 Server: http://localhost:{PORT}")
        print(f"📚 Docs: http://localhost:{PORT}/docs")
        print(f"🏥 Health: http://localhost:{PORT}/health")
        print("\nPress CTRL+C to stop the server\n")
        
        uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="info")
    else:
        print("No action specified. Use --collect, --process, --eda, --train, or --server.")