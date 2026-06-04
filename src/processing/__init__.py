import os
import pandas as pd
from .feature_eng import prepare_data

INTERIM_CSV = os.path.join(os.getcwd(), "data", "interim", "uber_rides_log.csv")
PROCESSED_CSV = os.path.join(os.getcwd(), "data", "processed", "uber_dataset.csv")

def run_processing():
    print("| Starting processing and feature engineering...")
    
    if not os.path.exists(INTERIM_CSV):
        print(f"| Interim data not found at {INTERIM_CSV}. Run --extract first.")
        return
        
    try:
        # Load the raw extracted data
        df = pd.read_csv(INTERIM_CSV)
        print(f"| Loaded {len(df)} rows from interim data.")
        
        # Apply Pipeline
        df = prepare_data(df)
        
        # Save to processed directory
        df.to_csv(PROCESSED_CSV, index=False)
        print(f"\n| Processing complete. Clean dataset saved to: {PROCESSED_CSV}")
        print(f"| Final dataset shape: {df.shape[0]} rows, {df.shape[1]} columns.")
        
    except Exception as e:
        print(f"| Error during processing: {e}")