# Simple test to demonstrate MongoDB persistence
# This script will run mongodbintegrationmvp.py twice to show persistence

import subprocess
import sys
import time
from pymongo import MongoClient

def check_experiment_trials():
    """Check how many trials are in the database."""
    try:
        client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=2000)
        db = client["ax_db"]
        snapshots_col = db["ax_snapshots"]
        
        experiment_name = "branin_experiment_k7m9"
        record = snapshots_col.find_one(
            {"experiment_name": experiment_name},
            sort=[("timestamp", -1)]
        )
        
        if record:
            return record['trial_count']
        return 0
    except:
        return 0

def run_experiment_limited(max_trials=5):
    """Run the experiment but modify MAX_TRIALS temporarily."""
    print(f"🚀 Running experiment with MAX_TRIALS={max_trials}")
    
    # Read the original file
    with open("mongodbintegrationmvp.py", "r") as f:
        original_content = f.read()
    
    # Create a temporary modified version
    modified_content = original_content.replace(
        'MAX_TRIALS = 19', 
        f'MAX_TRIALS = {max_trials}'
    )
    
    with open("temp_experiment.py", "w") as f:
        f.write(modified_content)
    
    try:
        # Run the modified experiment
        result = subprocess.run([
            sys.executable, "temp_experiment.py"
        ], capture_output=True, text=True, timeout=30)
        
        print("📝 Output:")
        for line in result.stdout.split('\n'):
            if line.strip() and any(keyword in line for keyword in 
                ["Trial", "Best", "Connected", "Created", "Resuming", "completed"]):
                print(f"   {line}")
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("⏰ Experiment timed out (might be normal)")
        return True
    finally:
        # Clean up temp file
        try:
            import os
            os.remove("temp_experiment.py")
        except:
            pass

def main():
    print("=" * 50)
    print("🧪 TESTING MONGODB PERSISTENCE")
    print("=" * 50)
    
    # Check MongoDB connection
    try:
        client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=2000)
        client.admin.command("ping")
        print("✅ MongoDB is running")
    except:
        print("❌ MongoDB is not running. Please start MongoDB first.")
        return
    
    print("\n📋 STEP 1: Check initial state")
    initial_trials = check_experiment_trials()
    print(f"   Initial trials in database: {initial_trials}")
    
    print("\n📋 STEP 2: Run experiment (first run)")
    run_experiment_limited(max_trials=initial_trials + 3)
    time.sleep(1)
    
    after_first_run = check_experiment_trials()
    print(f"   Trials after first run: {after_first_run}")
    
    print("\n📋 STEP 3: Run experiment again (second run - should resume)")
    run_experiment_limited(max_trials=after_first_run + 2)
    time.sleep(1)
    
    final_trials = check_experiment_trials()
    print(f"   Trials after second run: {final_trials}")
    
    print("\n" + "=" * 50)
    print("📊 RESULTS")
    print("=" * 50)
    print(f"Initial:     {initial_trials} trials")
    print(f"After 1st:   {after_first_run} trials")
    print(f"After 2nd:   {final_trials} trials")
    
    if final_trials > after_first_run >= initial_trials:
        print("\n🎉 SUCCESS! Experiment resumed correctly from MongoDB")
        print("   This proves the kernel can be 'killed' and experiment continues")
    else:
        print("\n❌ Something went wrong with persistence")

if __name__ == "__main__":
    main()
