import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.collection import run_collection

print("Starting the collection process...")
run_collection()