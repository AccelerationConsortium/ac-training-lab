"""
Ax Bayesian Optimization Tutorial with Prefect Human-in-the-Loop Integration

This tutorial demonstrates how to integrate Ax (Adaptive Experimentation Platform) 
with Prefect for human-in-the-loop Bayesian optimization workflows. It includes:

- Checkpointing optimization state to MongoDB
- Human-in-the-loop decision making
- Resume capability for interrupted workflows
- Prefect free-tier compatible setup

Requirements:
- ax-platform
- prefect
- pymongo
- numpy
- matplotlib (optional, for plotting)

Setup Instructions:
1. Install dependencies: pip install ax-platform prefect pymongo numpy matplotlib
2. Set up MongoDB connection (see docs/ax_tutorial_setup.md)
3. Configure Prefect (see docs/ax_tutorial_setup.md)
4. Run the tutorial: python ax_bayesian_optimization_hitl.py

References:
- https://ax.dev/tutorials/gpei_hartmann_service.html
- https://www.prefect.io/blog/unveiling-interactive-workflows
- https://docs.prefect.io
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any

import numpy as np
from prefect import flow, get_run_logger, task
from prefect.context import get_run_context
from prefect.engine import pause_flow_run
from prefect.input import RunInput

# Conditional imports with fallbacks for development
try:
    from ax.service.ax_client import AxClient
    from ax.utils.measurement.synthetic_functions import hartmann6
    AX_AVAILABLE = True
except ImportError:
    AX_AVAILABLE = False
    print("Warning: Ax not available. Install with: pip install ax-platform")

try:
    from pymongo import MongoClient
    MONGO_AVAILABLE = True
except ImportError:
    MONGO_AVAILABLE = False
    print("Warning: PyMongo not available. Install with: pip install pymongo")

# Configuration
EXPERIMENT_NAME = "ax_tutorial_hartmann6"
N_ITERATIONS = 10
MIN_CONFIDENCE_THRESHOLD = 0.8  # Minimum confidence before asking for human input

# MongoDB configuration (set these environment variables)
MONGODB_CONNECTION_STRING = os.getenv("MONGODB_CONNECTION_STRING", 
                                     "mongodb://localhost:27017/")
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE", "ax_tutorial")
MONGODB_COLLECTION = os.getenv("MONGODB_COLLECTION", "optimization_checkpoints")


class HumanInput(RunInput):
    """Input schema for human-in-the-loop decisions."""
    continue_optimization: bool = True
    adjust_parameters: bool = False
    parameter_suggestions: str = ""
    comments: str = ""
    confidence_override: Optional[float] = None


class OptimizationCheckpoint:
    """Handles saving and loading optimization state to/from MongoDB."""
    
    def __init__(self, connection_string: str, database: str, collection: str):
        self.connection_string = connection_string
        self.database = database
        self.collection = collection
    
    def save_checkpoint(self, experiment_name: str, ax_client_snapshot: str, 
                       iteration: int, best_parameters: Dict, 
                       best_objective: float, metadata: Dict = None) -> str:
        """Save optimization checkpoint to MongoDB."""
        if not MONGO_AVAILABLE:
            # Fallback: save to local file
            checkpoint_data = {
                "experiment_name": experiment_name,
                "ax_client_snapshot": ax_client_snapshot,
                "iteration": iteration,
                "best_parameters": best_parameters,
                "best_objective": best_objective,
                "metadata": metadata or {},
                "timestamp": datetime.utcnow().isoformat()
            }
            filename = f"/tmp/{experiment_name}_checkpoint_{iteration}.json"
            with open(filename, 'w') as f:
                json.dump(checkpoint_data, f, indent=2)
            return filename
        
        try:
            with MongoClient(self.connection_string) as client:
                db = client[self.database]
                collection = db[self.collection]
                
                checkpoint_data = {
                    "experiment_name": experiment_name,
                    "ax_client_snapshot": ax_client_snapshot,
                    "iteration": iteration,
                    "best_parameters": best_parameters,
                    "best_objective": best_objective,
                    "metadata": metadata or {},
                    "timestamp": datetime.utcnow(),
                    "status": "active"
                }
                
                result = collection.insert_one(checkpoint_data)
                return str(result.inserted_id)
        except Exception as e:
            logging.error(f"Failed to save checkpoint to MongoDB: {e}")
            # Fallback to local file
            return self.save_checkpoint(experiment_name, ax_client_snapshot, 
                                      iteration, best_parameters, best_objective, metadata)
    
    def load_latest_checkpoint(self, experiment_name: str) -> Optional[Dict]:
        """Load the latest checkpoint for an experiment."""
        if not MONGO_AVAILABLE:
            # Try to load from local files
            import glob
            pattern = f"/tmp/{experiment_name}_checkpoint_*.json"
            files = glob.glob(pattern)
            if not files:
                return None
            
            latest_file = max(files, key=os.path.getctime)
            with open(latest_file, 'r') as f:
                return json.load(f)
        
        try:
            with MongoClient(self.connection_string) as client:
                db = client[self.database]
                collection = db[self.collection]
                
                checkpoint = collection.find_one(
                    {"experiment_name": experiment_name},
                    sort=[("timestamp", -1)]
                )
                return checkpoint
        except Exception as e:
            logging.error(f"Failed to load checkpoint from MongoDB: {e}")
            return None


def hartmann6_objective(parameters: Dict[str, float]) -> float:
    """
    Hartmann6 synthetic function for optimization.
    This is a standard benchmark function with known global minimum.
    
    Args:
        parameters: Dictionary with keys x1, x2, x3, x4, x5, x6
    
    Returns:
        Objective value (we want to minimize this)
    """
    if AX_AVAILABLE:
        # Use the actual Ax implementation
        x = np.array([parameters[f"x{i}"] for i in range(1, 7)])
        return hartmann6(x)
    else:
        # Simplified version for demonstration
        x = np.array([parameters[f"x{i}"] for i in range(1, 7)])
        # This is a simplified approximation of Hartmann6
        return np.sum(x**2) - 3.0 * np.exp(-np.sum(x**2))


@task
def evaluate_objective(parameters: Dict[str, float]) -> Tuple[float, Dict[str, Any]]:
    """
    Evaluate the objective function with the given parameters.
    
    Returns:
        Tuple of (objective_value, evaluation_metadata)
    """
    logger = get_run_logger()
    
    try:
        objective_value = hartmann6_objective(parameters)
        
        metadata = {
            "parameters": parameters,
            "timestamp": datetime.utcnow().isoformat(),
            "evaluation_successful": True
        }
        
        logger.info(f"Evaluated parameters {parameters}: objective = {objective_value:.4f}")
        return objective_value, metadata
        
    except Exception as e:
        logger.error(f"Failed to evaluate objective: {e}")
        # Return a penalty value
        return 1000.0, {
            "parameters": parameters,
            "timestamp": datetime.utcnow().isoformat(),
            "evaluation_successful": False,
            "error": str(e)
        }


@task
def save_checkpoint_task(checkpoint_handler: OptimizationCheckpoint,
                        experiment_name: str, ax_client_snapshot: str,
                        iteration: int, best_parameters: Dict, 
                        best_objective: float, metadata: Dict = None) -> str:
    """Task wrapper for saving checkpoints."""
    return checkpoint_handler.save_checkpoint(
        experiment_name, ax_client_snapshot, iteration, 
        best_parameters, best_objective, metadata
    )


@task
def initialize_ax_client(experiment_name: str, existing_checkpoint: Optional[Dict] = None) -> Any:
    """Initialize or restore Ax client from checkpoint."""
    logger = get_run_logger()
    
    if not AX_AVAILABLE:
        logger.warning("Ax not available - using mock client")
        # Return a mock client for demonstration
        return {
            "type": "mock_client",
            "experiment_name": experiment_name,
            "parameter_space": {
                f"x{i}": {"type": "range", "bounds": [0.0, 1.0]} 
                for i in range(1, 7)
            },
            "iteration": 0,
            "best_parameters": None,
            "best_objective": None
        }
    
    if existing_checkpoint:
        logger.info(f"Restoring Ax client from checkpoint at iteration {existing_checkpoint['iteration']}")
        # In a real implementation, you would restore from the snapshot
        ax_client = AxClient()
        # For now, create a new client (in practice, you'd use ax_client.load_from_json_snapshot)
        ax_client.create_experiment(
            name=experiment_name,
            parameters=[
                {"name": f"x{i}", "type": "range", "bounds": [0.0, 1.0]}
                for i in range(1, 7)
            ],
            objective_name="hartmann6",
            minimize=True,
        )
        return ax_client
    else:
        logger.info("Creating new Ax client")
        ax_client = AxClient()
        ax_client.create_experiment(
            name=experiment_name,
            parameters=[
                {"name": f"x{i}", "type": "range", "bounds": [0.0, 1.0]}
                for i in range(1, 7)
            ],
            objective_name="hartmann6",
            minimize=True,
        )
        return ax_client


@task
def get_next_trial(ax_client: Any) -> Tuple[Dict[str, float], int]:
    """Get next trial parameters from Ax."""
    if not AX_AVAILABLE or isinstance(ax_client, dict):
        # Mock implementation
        trial_index = ax_client.get("iteration", 0)
        parameters = {
            f"x{i}": np.random.uniform(0, 1) for i in range(1, 7)
        }
        return parameters, trial_index
    
    parameters, trial_index = ax_client.get_next_trial()
    return parameters, trial_index


@task
def complete_trial(ax_client: Any, trial_index: int, objective_value: float) -> Any:
    """Complete a trial with the objective value."""
    if not AX_AVAILABLE or isinstance(ax_client, dict):
        # Mock implementation
        ax_client["iteration"] = trial_index + 1
        if ax_client["best_objective"] is None or objective_value < ax_client["best_objective"]:
            ax_client["best_objective"] = objective_value
        return ax_client
    
    ax_client.complete_trial(trial_index=trial_index, raw_data=objective_value)
    return ax_client


@task
def get_best_parameters(ax_client: Any) -> Tuple[Dict[str, float], float]:
    """Get the current best parameters and objective value."""
    if not AX_AVAILABLE or isinstance(ax_client, dict):
        # Mock implementation
        if ax_client["best_parameters"] is None:
            return {f"x{i}": 0.1 for i in range(1, 7)}, ax_client.get("best_objective", 1.0)
        return ax_client["best_parameters"], ax_client["best_objective"]
    
    best_parameters, best_values = ax_client.get_best_parameters()
    return best_parameters, best_values[0]["hartmann6"]


@task
def calculate_confidence(ax_client: Any, iteration: int) -> float:
    """Calculate confidence in the current best solution."""
    if not AX_AVAILABLE or isinstance(ax_client, dict):
        # Mock confidence calculation
        return min(0.9, iteration * 0.1)
    
    # In a real implementation, you might use prediction intervals or other uncertainty metrics
    # For now, use a simple heuristic based on iteration count
    return min(0.95, iteration * 0.05 + 0.1)


@flow(name="ax-bayesian-optimization-hitl")
async def bayesian_optimization_with_hitl(
    experiment_name: str = EXPERIMENT_NAME,
    n_iterations: int = N_ITERATIONS,
    resume_from_checkpoint: bool = True
) -> Dict[str, Any]:
    """
    Main Bayesian optimization flow with human-in-the-loop decision making.
    
    Args:
        experiment_name: Name of the optimization experiment
        n_iterations: Maximum number of optimization iterations
        resume_from_checkpoint: Whether to try resuming from existing checkpoint
    
    Returns:
        Dictionary containing optimization results
    """
    logger = get_run_logger()
    logger.info(f"Starting Bayesian optimization: {experiment_name}")
    
    # Initialize checkpoint handler
    checkpoint_handler = OptimizationCheckpoint(
        MONGODB_CONNECTION_STRING, MONGODB_DATABASE, MONGODB_COLLECTION
    )
    
    # Try to load existing checkpoint
    existing_checkpoint = None
    start_iteration = 0
    
    if resume_from_checkpoint:
        existing_checkpoint = checkpoint_handler.load_latest_checkpoint(experiment_name)
        if existing_checkpoint:
            start_iteration = existing_checkpoint["iteration"]
            logger.info(f"Resuming from checkpoint at iteration {start_iteration}")
    
    # Initialize Ax client
    ax_client = await initialize_ax_client(experiment_name, existing_checkpoint)
    
    results = {
        "experiment_name": experiment_name,
        "iterations": [],
        "best_parameters": None,
        "best_objective": None,
        "human_interventions": []
    }
    
    for iteration in range(start_iteration, n_iterations):
        logger.info(f"Starting iteration {iteration + 1}/{n_iterations}")
        
        try:
            # Get next trial parameters
            parameters, trial_index = await get_next_trial(ax_client)
            logger.info(f"Trial {trial_index}: parameters = {parameters}")
            
            # Evaluate objective function
            objective_value, eval_metadata = await evaluate_objective(parameters)
            
            # Complete the trial
            ax_client = await complete_trial(ax_client, trial_index, objective_value)
            
            # Get current best
            best_parameters, best_objective = await get_best_parameters(ax_client)
            
            # Calculate confidence in the current solution
            confidence = await calculate_confidence(ax_client, iteration + 1)
            
            iteration_result = {
                "iteration": iteration + 1,
                "trial_index": trial_index,
                "parameters": parameters,
                "objective_value": objective_value,
                "best_parameters": best_parameters,
                "best_objective": best_objective,
                "confidence": confidence,
                "metadata": eval_metadata
            }
            
            results["iterations"].append(iteration_result)
            results["best_parameters"] = best_parameters
            results["best_objective"] = best_objective
            
            # Save checkpoint
            ax_snapshot = json.dumps({"mock": "snapshot"})  # In real case: ax_client.to_json_snapshot()
            checkpoint_id = await save_checkpoint_task(
                checkpoint_handler, experiment_name, ax_snapshot,
                iteration + 1, best_parameters, best_objective,
                {"confidence": confidence, "total_iterations": n_iterations}
            )
            
            logger.info(f"Saved checkpoint: {checkpoint_id}")
            
            # Human-in-the-loop decision point
            if confidence < MIN_CONFIDENCE_THRESHOLD or iteration % 3 == 2:  # Every 3rd iteration or low confidence
                logger.info(f"Requesting human input (confidence: {confidence:.3f})")
                
                # Prepare human-readable summary
                flow_run = get_run_context().flow_run
                summary_message = (
                    f"🧪 **Optimization Update - Iteration {iteration + 1}**\n\n"
                    f"📊 **Current Best:**\n"
                    f"   • Objective Value: {best_objective:.4f}\n"
                    f"   • Parameters: {best_parameters}\n\n"
                    f"🎯 **Latest Trial:**\n"
                    f"   • Parameters: {parameters}\n"
                    f"   • Objective: {objective_value:.4f}\n\n"
                    f"🤖 **Algorithm Confidence:** {confidence:.1%}\n\n"
                    f"**Should we continue optimization?**"
                )
                
                # Pause for human input
                human_input = await pause_flow_run(
                    wait_for_input=HumanInput.with_initial_data(
                        continue_optimization=True,
                        adjust_parameters=False,
                        parameter_suggestions="",
                        comments="",
                        confidence_override=None
                    ),
                    timeout=300,  # 5 minutes timeout
                    poll_interval=10
                )
                
                results["human_interventions"].append({
                    "iteration": iteration + 1,
                    "confidence": confidence,
                    "human_input": {
                        "continue_optimization": human_input.continue_optimization,
                        "adjust_parameters": human_input.adjust_parameters,
                        "parameter_suggestions": human_input.parameter_suggestions,
                        "comments": human_input.comments,
                        "confidence_override": human_input.confidence_override
                    }
                })
                
                logger.info(f"Human decision: continue={human_input.continue_optimization}")
                
                if not human_input.continue_optimization:
                    logger.info("Human requested to stop optimization")
                    break
                
                if human_input.adjust_parameters and human_input.parameter_suggestions:
                    logger.info(f"Human suggested parameter adjustments: {human_input.parameter_suggestions}")
                    # In a real implementation, you might adjust the search space or add constraints
                
                if human_input.confidence_override is not None:
                    confidence = human_input.confidence_override
                    logger.info(f"Human overrode confidence to: {confidence}")
            
            logger.info(f"Completed iteration {iteration + 1}: best_objective = {best_objective:.4f}")
            
        except Exception as e:
            logger.error(f"Error in iteration {iteration + 1}: {e}")
            # Save error checkpoint
            checkpoint_id = await save_checkpoint_task(
                checkpoint_handler, experiment_name, "error_state",
                iteration + 1, results.get("best_parameters", {}), 
                results.get("best_objective", float('inf')),
                {"error": str(e), "status": "error"}
            )
            
            # Ask human whether to continue after error
            error_input = await pause_flow_run(
                wait_for_input=HumanInput.with_initial_data(
                    continue_optimization=False,
                    comments=f"Error occurred: {str(e)}"
                ),
                timeout=600  # 10 minutes for error recovery
            )
            
            if not error_input.continue_optimization:
                logger.info("Human chose to stop after error")
                break
    
    # Final summary
    logger.info(f"Optimization completed: {len(results['iterations'])} iterations")
    logger.info(f"Best objective: {results['best_objective']:.4f}")
    logger.info(f"Best parameters: {results['best_parameters']}")
    
    return results


if __name__ == "__main__":
    # For local testing
    logging.basicConfig(level=logging.INFO)
    
    # Run the optimization
    asyncio.run(bayesian_optimization_with_hitl.serve(
        name="ax-bayesian-optimization-tutorial"
    ))