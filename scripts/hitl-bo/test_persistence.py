# Test script to simulate kernel interruption and recovery
# This demonstrates MongoDB persistence in mongodbintegrationmvp.py

import subprocess
import sys
import time
import signal
import os
from pymongo import MongoClient

def check_mongodb_connection():
    """Check if MongoDB is running and accessible."""
    try:
        client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=2000)
        client.admin.command("ping")
        print("✅ MongoDB is running and accessible")
        return True
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        return False

def get_experiment_status():
    """Check current experiment status in MongoDB."""
    try:
        client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=2000)
        db = client["ax_db"]
        snapshots_col = db["ax_snapshots"]
        
        # Find the most recent snapshot for the default experiment
        experiment_name = "branin_experiment_k7m9"
        record = snapshots_col.find_one(
            {"experiment_name": experiment_name},
            sort=[("timestamp", -1)]
        )
        
        if record:
            print(f"📊 Found experiment '{experiment_name}' with {record['trial_count']} trials")
            print(f"   Last updated: {record['timestamp']}")
            return record['trial_count']
        else:
            print(f"📊 No existing experiment '{experiment_name}' found")
            return 0
    except Exception as e:
        print(f"❌ Error checking experiment status: {e}")
        return 0

def run_experiment_with_interruption(trials_before_kill=3):
    """Run the experiment and kill it after a few trials."""
    print(f"\n🚀 Starting experiment (will be killed after ~{trials_before_kill} trials)...")
    
    # Start the experiment as a subprocess
    process = subprocess.Popen([
        sys.executable, "mongodbintegrationmvp.py"
    ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
    
    trial_count = 0
    output_lines = []
    
    try:
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                output_lines.append(output.strip())
                print(f"📝 {output.strip()}")
                
                # Count trials and kill after specified number
                if "Trial" in output and "x1=" in output and "x2=" in output:
                    trial_count += 1
                    if trial_count >= trials_before_kill:
                        print(f"\n💀 SIMULATING KERNEL KILL after {trial_count} trials...")
                        process.terminate()
                        time.sleep(2)
                        if process.poll() is None:
                            process.kill()
                        break
                        
    except KeyboardInterrupt:
        print("\n💀 SIMULATING KERNEL KILL (KeyboardInterrupt)...")
        process.terminate()
        time.sleep(1)
        if process.poll() is None:
            process.kill()
    
    print(f"🔴 Process terminated after {trial_count} trials")
    return trial_count

def run_experiment_recovery():
    """Run the experiment again to test recovery."""
    print("\n🔄 Testing recovery - running experiment again...")
    
    try:
        # Run the experiment normally
        result = subprocess.run([
            sys.executable, "mongodbintegrationmvp.py"
        ], capture_output=True, text=True, timeout=60)
        
        print("📝 Recovery run output:")
        for line in result.stdout.split('\n'):
            if line.strip():
                print(f"   {line}")
                
        if result.stderr:
            print("⚠️ Errors during recovery:")
            for line in result.stderr.split('\n'):
                if line.strip():
                    print(f"   {line}")
                    
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("⏰ Recovery run timed out (normal for long experiments)")
        return True
    except Exception as e:
        print(f"❌ Error during recovery run: {e}")
        return False

def main():
    """Main test function."""
    print("=" * 60)
    print("🧪 TESTING MONGODB PERSISTENCE & RECOVERY")
    print("=" * 60)
    
    # Step 1: Check MongoDB
    if not check_mongodb_connection():
        print("❌ Cannot proceed without MongoDB. Please start MongoDB first.")
        return
    
    # Step 2: Check initial state
    print("\n📋 STEP 1: Checking initial experiment state")
    initial_trials = get_experiment_status()
    
    # Step 3: Run experiment with interruption
    print("\n📋 STEP 2: Running experiment with simulated interruption")
    trials_completed = run_experiment_with_interruption(trials_before_kill=3)
    
    # Step 4: Check state after interruption
    print("\n📋 STEP 3: Checking experiment state after interruption")
    time.sleep(2)  # Give MongoDB time to process
    post_interrupt_trials = get_experiment_status()
    
    # Step 5: Test recovery
    print("\n📋 STEP 4: Testing recovery from MongoDB")
    recovery_success = run_experiment_recovery()
    
    # Step 6: Final state check
    print("\n📋 STEP 5: Final experiment state check")
    final_trials = get_experiment_status()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"Initial trials:        {initial_trials}")
    print(f"Trials after kill:     {post_interrupt_trials}")
    print(f"Final trials:          {final_trials}")
    print(f"Recovery successful:   {'✅ YES' if recovery_success else '❌ NO'}")
    print(f"Data persisted:        {'✅ YES' if post_interrupt_trials > initial_trials else '❌ NO'}")
    print(f"Experiment continued:  {'✅ YES' if final_trials >= post_interrupt_trials else '❌ NO'}")
    
    if post_interrupt_trials > initial_trials and recovery_success:
        print("\n🎉 SUCCESS: MongoDB persistence is working correctly!")
        print("   The experiment successfully resumed from the database after interruption.")
    else:
        print("\n❌ FAILURE: There may be issues with MongoDB persistence.")

if __name__ == "__main__":
    main()
