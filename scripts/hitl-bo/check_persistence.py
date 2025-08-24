# Manual test for MongoDB persistence
# Run this to check the state before and after manually killing mongodbintegrationmvp.py

from pymongo import MongoClient
from datetime import datetime
import json

def check_mongodb_status():
    """Check MongoDB connection and experiment status."""
    try:
        client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=2000)
        client.admin.command("ping")
        print("✅ MongoDB is running and accessible")
        
        db = client["ax_db"]
        snapshots_col = db["ax_snapshots"]
        
        experiment_name = "branin_experiment_k7m9"
        
        # Get all snapshots for this experiment
        snapshots = list(snapshots_col.find(
            {"experiment_name": experiment_name}
        ).sort("timestamp", -1).limit(5))
        
        if snapshots:
            print(f"\n📊 Found {len(snapshots)} recent snapshots for '{experiment_name}':")
            for i, snapshot in enumerate(snapshots):
                timestamp = snapshot['timestamp']
                trial_count = snapshot['trial_count']
                snapshot_id = str(snapshot['_id'])[:8] + "..."
                print(f"   {i+1}. {timestamp} | {trial_count} trials | ID: {snapshot_id}")
            
            # Show details of most recent
            latest = snapshots[0]
            print(f"\n🔍 Most recent snapshot details:")
            print(f"   Timestamp: {latest['timestamp']}")
            print(f"   Trial count: {latest['trial_count']}")
            print(f"   Document ID: {latest['_id']}")
            
            return latest['trial_count']
        else:
            print(f"📊 No snapshots found for experiment '{experiment_name}'")
            return 0
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def cleanup_old_experiments():
    """Optional: Clean up old experiment data."""
    try:
        client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=2000)
        db = client["ax_db"]
        snapshots_col = db["ax_snapshots"]
        
        experiment_name = "branin_experiment_k7m9"
        
        count = snapshots_col.count_documents({"experiment_name": experiment_name})
        print(f"\n🗑️ Found {count} total snapshots for '{experiment_name}'")
        
        if count > 0:
            choice = input("Do you want to delete all snapshots? (y/N): ").strip().lower()
            if choice == 'y':
                result = snapshots_col.delete_many({"experiment_name": experiment_name})
                print(f"   Deleted {result.deleted_count} snapshots")
                return True
        
        return False
        
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
        return False

def main():
    print("=" * 60)
    print("🔍 MONGODB PERSISTENCE CHECKER")
    print("=" * 60)
    print("This tool helps you manually test the persistence of mongodbintegrationmvp.py")
    print("")
    print("How to use:")
    print("1. Run this script to check current state")
    print("2. Start mongodbintegrationmvp.py and let it run a few trials")
    print("3. Kill mongodbintegrationmvp.py (Ctrl+C or close terminal)")
    print("4. Run this script again to verify data was saved")
    print("5. Start mongodbintegrationmvp.py again to see it resume")
    print("")
    
    while True:
        print("\nChoose an option:")
        print("1. Check current experiment status")
        print("2. Clean up old experiments (delete all data)")
        print("3. Exit")
        
        choice = input("\nEnter choice (1-3): ").strip()
        
        if choice == "1":
            print("\n" + "-" * 40)
            trial_count = check_mongodb_status()
            print("-" * 40)
            
            if trial_count is not None:
                if trial_count == 0:
                    print("\n💡 No trials found. You can now:")
                    print("   - Start mongodbintegrationmvp.py to begin a new experiment")
                else:
                    print(f"\n💡 Found {trial_count} trials. You can now:")
                    print("   - Start mongodbintegrationmvp.py to resume the experiment")
                    print("   - Or kill it partway through to test persistence")
            
        elif choice == "2":
            print("\n" + "-" * 40)
            cleanup_old_experiments()
            print("-" * 40)
            
        elif choice == "3":
            print("\n👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    main()
