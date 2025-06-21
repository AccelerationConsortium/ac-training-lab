# Ax Bayesian Optimization with Prefect and MongoDB

Minimal working example of integrating Ax (Adaptive Experimentation Platform) with Prefect for Bayesian optimization with MongoDB checkpointing.

## Features

- **Ax Integration**: Bayesian optimization using the Hartmann6 benchmark function
- **Prefect Orchestration**: Workflow management with restart capability  
- **MongoDB Checkpointing**: JSON checkpoint storage with automatic restart from last state
- **EC2 Ready**: Designed to run continuously on EC2 with fault tolerance

## Quick Start

1. **Install dependencies**:
   ```bash
   pip install ax-platform prefect pymongo
   ```

2. **Set MongoDB connection**:
   ```bash
   export MONGODB_CONNECTION_STRING="mongodb://localhost:27017/"
   export MONGODB_DATABASE="ax_optimization"
   ```

3. **Run optimization**:
   ```bash
   python ax_prefect_minimal.py
   ```

4. **Deploy to Prefect**:
   ```bash
   python create_ax_tutorial_deployment.py
   ```

## Files

- `ax_prefect_minimal.py` - Main optimization script
- `create_ax_tutorial_deployment.py` - Prefect deployment configuration
- `.env.example` - Environment variable template

## MongoDB Setup

The script will automatically create the database and collection. For production, consider using MongoDB Atlas or a dedicated MongoDB instance.

## Restart Behavior

The optimization automatically resumes from the last checkpoint stored in MongoDB. This makes it suitable for running on EC2 instances that may restart unexpectedly.