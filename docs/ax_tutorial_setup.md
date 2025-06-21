# Ax Bayesian Optimization with Prefect Human-in-the-Loop Tutorial Setup

This tutorial demonstrates how to set up and run Bayesian optimization workflows using Ax (Adaptive Experimentation Platform) integrated with Prefect for human-in-the-loop decision making and MongoDB for checkpointing.

## Prerequisites

- Python 3.8+
- MongoDB (local installation or cloud service like MongoDB Atlas)
- Prefect Cloud account (free tier) or local Prefect server

## Installation

### 1. Install Python Dependencies

```bash
pip install ax-platform prefect pymongo numpy matplotlib
```

### 2. Install Additional Dependencies (Optional)

For enhanced plotting and visualization:
```bash
pip install plotly seaborn
```

## MongoDB Setup

### Option A: Local MongoDB Installation

1. Install MongoDB Community Edition:
   - **Ubuntu/Debian**: `sudo apt-get install mongodb`
   - **macOS**: `brew install mongodb-community`
   - **Windows**: Download from [MongoDB official site](https://www.mongodb.com/try/download/community)

2. Start MongoDB service:
   ```bash
   # Linux/macOS
   sudo systemctl start mongod
   # or
   brew services start mongodb-community
   
   # Windows
   net start MongoDB
   ```

### Option B: MongoDB Atlas (Cloud - Recommended)

1. Create a free account at [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create a new cluster (free tier available)
3. Set up database access:
   - Create a database user
   - Add your IP address to the network access list
4. Get your connection string from the "Connect" button

### Environment Variables

Set the following environment variables:

```bash
# For local MongoDB
export MONGODB_CONNECTION_STRING="mongodb://localhost:27017/"

# For MongoDB Atlas
export MONGODB_CONNECTION_STRING="mongodb+srv://<username>:<password>@<cluster>.mongodb.net/"

export MONGODB_DATABASE="ax_tutorial"
export MONGODB_COLLECTION="optimization_checkpoints"
```

## Prefect Setup

### Option A: Prefect Cloud (Recommended for beginners)

1. Create a free account at [Prefect Cloud](https://app.prefect.cloud/)
2. Create a workspace
3. Generate an API key from your profile settings
4. Configure your local environment:

```bash
prefect cloud login
# Enter your API key when prompted

# Set up a work pool (for running flows)
prefect work-pool create --type process my-work-pool
```

### Option B: Self-Hosted Prefect Server

1. Start Prefect server:
```bash
prefect server start
```

2. Configure your environment:
```bash
prefect config set PREFECT_API_URL="http://127.0.0.1:4200/api"
```

### Set up Notifications (Optional)

For human-in-the-loop notifications, you can set up Slack webhooks:

1. Create a Slack webhook URL in your Slack workspace
2. Create a Prefect notification block:

```python
from prefect.blocks.notifications import SlackWebhook

slack_webhook = SlackWebhook(url="YOUR_SLACK_WEBHOOK_URL")
slack_webhook.save("optimization-notifications")
```

## Running the Tutorial

### 1. Basic Execution

Run the tutorial script directly:

```bash
cd scripts/prefect_scripts
python ax_bayesian_optimization_hitl.py
```

### 2. Deploy as a Prefect Flow

Create a deployment for scheduled or triggered runs:

```python
# create_ax_deployment.py
from prefect import flow
from ax_bayesian_optimization_hitl import bayesian_optimization_with_hitl

if __name__ == "__main__":
    flow.from_source(
        source="https://github.com/AccelerationConsortium/ac-training-lab.git",
        entrypoint="scripts/prefect_scripts/ax_bayesian_optimization_hitl.py:bayesian_optimization_with_hitl",
    ).deploy(
        name="ax-bayesian-optimization-tutorial",
        work_pool_name="my-work-pool",
        # Schedule to run daily
        cron="0 9 * * *",  # 9 AM daily
        parameters={
            "experiment_name": "daily_optimization",
            "n_iterations": 20,
            "resume_from_checkpoint": True
        }
    )
```

Then run:
```bash
python create_ax_deployment.py
```

### 3. Start a Worker

To execute flows, start a Prefect worker:

```bash
prefect worker start --pool my-work-pool
```

## Tutorial Workflow

The tutorial implements a complete Bayesian optimization workflow with the following features:

### 1. Objective Function
- Uses the Hartmann6 benchmark function (6-dimensional optimization)
- Known global minimum for validation
- Fallback implementation if Ax is not available

### 2. Checkpointing
- Saves optimization state to MongoDB after each iteration
- Supports resuming from interruptions
- Fallback to local JSON files if MongoDB unavailable

### 3. Human-in-the-Loop Integration
- Pauses workflow when confidence is low or at regular intervals
- Presents optimization progress to human decision-makers
- Allows humans to:
  - Continue or stop optimization
  - Suggest parameter adjustments
  - Override confidence assessments
  - Add comments and observations

### 4. Error Handling
- Graceful handling of evaluation failures
- Human intervention on errors
- Checkpoint saving for error recovery

## Configuration Options

You can customize the tutorial behavior by modifying these parameters:

```python
# In ax_bayesian_optimization_hitl.py

EXPERIMENT_NAME = "my_optimization_experiment"
N_ITERATIONS = 25  # Number of optimization iterations
MIN_CONFIDENCE_THRESHOLD = 0.7  # Threshold for human intervention

# MongoDB settings
MONGODB_DATABASE = "my_optimization_db"
MONGODB_COLLECTION = "checkpoints"
```

## Monitoring and Visualization

### Prefect UI
- Access Prefect Cloud dashboard or local UI (http://localhost:4200)
- Monitor flow runs, task execution, and logs
- View human input responses and decisions

### MongoDB Data
Query optimization progress directly:

```python
from pymongo import MongoClient

client = MongoClient("your_connection_string")
db = client["ax_tutorial"]
collection = db["optimization_checkpoints"]

# Get latest checkpoint
latest = collection.find_one(sort=[("timestamp", -1)])
print(f"Best objective: {latest['best_objective']}")
print(f"Best parameters: {latest['best_parameters']}")
```

## Troubleshooting

### Common Issues

1. **MongoDB Connection Errors**
   - Verify MongoDB is running
   - Check connection string format
   - Ensure network access (for Atlas)

2. **Prefect Authentication Issues**
   - Re-run `prefect cloud login`
   - Check API key validity
   - Verify workspace access

3. **Ax Installation Problems**
   - Ax has heavy dependencies (PyTorch, BoTorch)
   - Consider using conda: `conda install -c conda-forge ax-platform`
   - Tutorial includes fallback mock implementation

4. **Flow Execution Timeouts**
   - Human input has 5-minute default timeout
   - Increase timeout in `pause_flow_run` calls
   - Set up proper notifications for alerts

### Performance Tips

1. **MongoDB Optimization**
   - Create indexes on `experiment_name` and `timestamp`
   - Use MongoDB Atlas for better performance and reliability

2. **Prefect Optimization**
   - Use appropriate work pool configurations
   - Monitor resource usage in long-running optimizations
   - Set up proper logging levels

## Next Steps

1. **Customize Objective Function**: Replace Hartmann6 with your real optimization problem
2. **Add Constraints**: Implement parameter constraints and feasibility checks
3. **Enhanced Visualization**: Add plotting tasks for optimization progress
4. **Multi-Objective**: Extend to multi-objective optimization scenarios
5. **Advanced HiTL**: Implement more sophisticated human decision interfaces

## References

- [Ax Documentation](https://ax.dev/)
- [Prefect Documentation](https://docs.prefect.io/)
- [MongoDB Python Driver](https://pymongo.readthedocs.io/)
- [Bayesian Optimization Tutorial](https://ax.dev/tutorials/gpei_hartmann_service.html)
- [Prefect Interactive Workflows](https://www.prefect.io/blog/unveiling-interactive-workflows)