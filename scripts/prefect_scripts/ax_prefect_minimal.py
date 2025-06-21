"""
Minimal working example of Ax Bayesian optimization with Prefect and MongoDB checkpointing.

This script demonstrates:
- Ax integration with Prefect
- MongoDB JSON checkpoint storage
- Restart capability for interrupted workflows
- Simple optimization loop without human-in-the-loop complexity

Requirements:
- ax-platform
- prefect
- pymongo
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional

import numpy as np
from ax.service.ax_client import AxClient
from ax.utils.measurement.synthetic_functions import hartmann6
from prefect import flow, task, get_run_logger
from pymongo import MongoClient


# MongoDB connection
MONGODB_URI = os.getenv("MONGODB_CONNECTION_STRING", "mongodb://localhost:27017/")
DATABASE_NAME = os.getenv("MONGODB_DATABASE", "ax_optimization")
COLLECTION_NAME = "checkpoints"


def get_mongo_client():
    """Get MongoDB client."""
    return MongoClient(MONGODB_URI)


def save_checkpoint(experiment_id: str, checkpoint_data: dict):
    """Save checkpoint to MongoDB."""
    client = get_mongo_client()
    db = client[DATABASE_NAME]
    collection = db[COLLECTION_NAME]
    
    checkpoint_data.update({
        "experiment_id": experiment_id,
        "timestamp": datetime.now().isoformat(),
    })
    
    collection.replace_one(
        {"experiment_id": experiment_id},
        checkpoint_data,
        upsert=True
    )
    client.close()


def load_checkpoint(experiment_id: str) -> Optional[dict]:
    """Load checkpoint from MongoDB."""
    client = get_mongo_client()
    db = client[DATABASE_NAME]
    collection = db[COLLECTION_NAME]
    
    checkpoint = collection.find_one({"experiment_id": experiment_id})
    client.close()
    
    return checkpoint


@task
def objective_function(parameters: Dict[str, float]) -> float:
    """Objective function to optimize - using Hartmann6 benchmark."""
    # Convert parameters dict to list for hartmann6
    x = [parameters[f'x{i}'] for i in range(1, 7)]
    return hartmann6(np.array(x))


@task
def initialize_ax_client(experiment_id: str) -> AxClient:
    """Initialize Ax client with parameter space."""
    ax_client = AxClient()
    ax_client.create_experiment(
        parameters=[
            {"name": f"x{i}", "type": "range", "bounds": [0.0, 1.0]}
            for i in range(1, 7)
        ],
        objective_name="hartmann6",
        minimize=True,
    )
    return ax_client


@task
def run_optimization_step(ax_client: AxClient, iteration: int) -> Dict:
    """Run a single optimization step."""
    logger = get_run_logger()
    
    # Get next trial parameters
    parameters, trial_index = ax_client.get_next_trial()
    logger.info(f"Iteration {iteration}: Trial {trial_index} with parameters {parameters}")
    
    # Evaluate objective function
    objective_value = objective_function(parameters)
    logger.info(f"Objective value: {objective_value}")
    
    # Complete trial in Ax
    ax_client.complete_trial(trial_index=trial_index, raw_data=objective_value)
    
    # Get current best
    best_parameters, best_values = ax_client.get_best_parameters()
    best_objective = best_values[0]["hartmann6"]
    
    return {
        "iteration": iteration,
        "trial_index": trial_index,
        "parameters": parameters,
        "objective_value": objective_value,
        "best_parameters": best_parameters,
        "best_objective": best_objective,
        "ax_client_json": ax_client.to_json_snapshot(),
    }


@flow(name="ax-bayesian-optimization")
def ax_optimization_flow(
    experiment_id: str = "hartmann6_optimization",
    max_iterations: int = 20,
    resume_from_checkpoint: bool = True,
):
    """Main optimization flow with checkpointing."""
    logger = get_run_logger()
    
    # Try to load from checkpoint
    checkpoint = None
    if resume_from_checkpoint:
        checkpoint = load_checkpoint(experiment_id)
        if checkpoint:
            logger.info(f"Resuming from checkpoint at iteration {checkpoint.get('iteration', 0)}")
    
    # Initialize or restore Ax client
    if checkpoint and "ax_client_json" in checkpoint:
        ax_client = AxClient.from_json_snapshot(checkpoint["ax_client_json"])
        start_iteration = checkpoint["iteration"] + 1
        logger.info(f"Restored Ax client from checkpoint, starting at iteration {start_iteration}")
    else:
        ax_client = initialize_ax_client(experiment_id)
        start_iteration = 1
        logger.info("Initialized new Ax client")
    
    # Run optimization loop
    for iteration in range(start_iteration, max_iterations + 1):
        logger.info(f"Starting optimization iteration {iteration}/{max_iterations}")
        
        # Run optimization step
        step_result = run_optimization_step(ax_client, iteration)
        
        # Save checkpoint
        save_checkpoint(experiment_id, step_result)
        logger.info(f"Checkpoint saved for iteration {iteration}")
        
        # Log progress
        logger.info(f"Current best: {step_result['best_objective']:.6f} at {step_result['best_parameters']}")
    
    # Final results
    best_parameters, best_values = ax_client.get_best_parameters()
    final_best = best_values[0]["hartmann6"]
    
    logger.info(f"Optimization complete!")
    logger.info(f"Final best objective: {final_best:.6f}")
    logger.info(f"Final best parameters: {best_parameters}")
    
    return {
        "experiment_id": experiment_id,
        "final_best_objective": final_best,
        "final_best_parameters": best_parameters,
        "total_iterations": max_iterations,
    }


if __name__ == "__main__":
    # Run the optimization
    result = ax_optimization_flow()
    print(f"Optimization complete: {result}")