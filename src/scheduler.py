"""
Scheduler module for automated EDA and model training tasks.
Runs EDA and training every 24 hours.
"""

import logging
import os
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

TRAINING_INTERVAL_HOURS = int(os.getenv("TRAINING_INTERVAL_HOURS", 24))
EDA_INTERVAL_HOURS = int(os.getenv("EDA_INTERVAL_HOURS", 24))

logger = logging.getLogger(__name__)

# Create logs directory if it doesn't exist
LOGS_DIR = os.path.join(os.getcwd(), "logs")
os.makedirs(LOGS_DIR, exist_ok=True)

# Configure logging for scheduler
scheduler_logger = logging.getLogger("apscheduler.schedulers.background")
scheduler_logger.setLevel(logging.INFO)

# File handler for scheduler logs
handler = logging.FileHandler(os.path.join(LOGS_DIR, "scheduler.log"))
handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
scheduler_logger.addHandler(handler)


def run_eda_task():
    """Execute EDA pipeline."""
    from src.eda import run_eda
    
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logger.info(f"[{timestamp}] Starting scheduled EDA task...")
        print(f"\n{'='*60}")
        print(f"[{timestamp}] 📊 Starting scheduled EDA task...")
        print(f"{'='*60}\n")
        
        run_eda()
        
        logger.info(f"[{timestamp}] ✅ EDA task completed successfully")
        print(f"\n✅ EDA task completed successfully\n")
    except Exception as e:
        logger.error(f"❌ EDA task failed: {str(e)}", exc_info=True)
        print(f"\n❌ EDA task failed: {str(e)}\n")


def run_training_task():
    """Execute training pipeline."""
    from src.models import run_training
    
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logger.info(f"[{timestamp}] Starting scheduled training task...")
        print(f"\n{'='*60}")
        print(f"[{timestamp}] 🤖 Starting scheduled training task...")
        print(f"{'='*60}\n")
        
        run_training()
        
        logger.info(f"[{timestamp}] ✅ Training task completed successfully")
        print(f"\n✅ Training task completed successfully\n")
    except Exception as e:
        logger.error(f"❌ Training task failed: {str(e)}", exc_info=True)
        print(f"\n❌ Training task failed: {str(e)}\n")


def init_scheduler():
    """Initialize and start the background scheduler."""
    scheduler = BackgroundScheduler()
    
    run_eda_task()  # Run EDA immediately on startup
    run_training_task()  # Run training immediately on startup
    
    scheduler.add_job(
        run_eda_task,
        trigger=IntervalTrigger(hours=EDA_INTERVAL_HOURS),
        id="eda_job",
        name="EDA Task",
        replace_existing=True,
        max_instances=1  # Prevent concurrent executions
    )
    
    scheduler.add_job(
        run_training_task,
        trigger=IntervalTrigger(hours=TRAINING_INTERVAL_HOURS),
        id="training_job",
        name="Training Task",
        replace_existing=True,
        max_instances=1,  # Prevent concurrent executions
    )
    
    scheduler.start()
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"[{timestamp}] Scheduler initialized and started")
    print(f"\n✅ Scheduler initialized - EDA will run every {EDA_INTERVAL_HOURS} hours")
    print(f"   Training will run every {TRAINING_INTERVAL_HOURS} hours")
    print(f"   📊 EDA logs: {os.path.join(LOGS_DIR, 'scheduler.log')}")
    print(f"   🤖 Training logs: {os.path.join(LOGS_DIR, 'scheduler.log')}")
    
    return scheduler
